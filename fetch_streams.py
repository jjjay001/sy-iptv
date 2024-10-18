from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 设置Selenium的Chrome选项
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 启动Chrome浏览器
driver = webdriver.Chrome(options=options)

# 直播源URL列表
live_sources = []

# 启用网络监控
driver.execute_cdp_cmd('Network.enable', {})

try:
    # 打开目标网页
    url = "http://m.snrtv.com/snrtv_tv/index.html"  # 替换为实际的直播页面URL
    driver.get(url)

    # 等待页面完全加载并确保 videoBox 元素加载完毕
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'videoBox'))
    )

    # 监听 XHR 请求
    def intercept_request(request):
        if '.m3u8' in request['url']:
            live_sources.append(request['url'])
            print(f"捕获到直播源 URL: {request['url']}")

    driver.request_interceptor = intercept_request

    # 获取默认直播源
    video_element = driver.find_element(By.ID, 'videoBox')
    default_live_url = video_element.get_attribute('src')
    if default_live_url:
        live_sources.append(default_live_url)
        print(f"找到默认直播源: {default_live_url}")
    else:
        print("未能找到默认直播源")

    # 切换频道
    channel_names = ['star', 'nl', '1', '2', '3', '4', '5', '6', '7']  # 列出需要切换的频道名称
    for channel in channel_names:
        try:
            print(f"通过hash切换到频道: {channel}")
            driver.execute_script(f"window.location.hash = '{channel}';")  # 通过hash切换频道
            
            # 等待页面加载
            time.sleep(3)  # 根据需要调整等待时间
            
            # 确认页面是否刷新
            current_url = driver.current_url
            if f'#{channel}' in current_url:
                print(f"成功切换到频道: {channel}，页面已刷新")
            else:
                print(f"切换频道: {channel} 后页面未刷新")

            # 检查是否有新的 XHR 请求
            if not live_sources or (live_sources and live_sources[-1] == default_live_url):
                print(f"未检测到新直播源，跳过频道: {channel}")
            else:
                print(f"成功切换到频道: {channel}")

        except Exception as e:
            print(f"切换频道时发生错误: {e}")

except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭浏览器
    driver.quit()

# 生成 .m3u 文件
with open('live_streams.m3u', 'w') as f:
    f.write('#EXTM3U\n')
    for index, source in enumerate(live_sources, start=1):
        f.write(f'#EXTINF:-1, Channel {index}\n')
        f.write(f'{source}\n')

print("已生成 live_streams.m3u 文件")
