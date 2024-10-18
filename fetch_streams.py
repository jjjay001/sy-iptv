from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# 设置Selenium的Chrome选项
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 启动Chrome浏览器
driver = webdriver.Chrome(options=options)

# 直播源URL列表
live_sources = []

def request_interceptor(request):
    # 监听请求并获取 .m3u8 URL
    if '.m3u8' in request['url']:
        live_sources.append(request['url'])
        print(f"捕获到直播源 URL: {request['url']}")

try:
    # 打开目标网页
    url = "http://live.snrtv.com"  # 替换为实际的直播页面URL
    driver.get(url)

    # 等待页面完全加载并确保视频盒子加载完毕
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'videoBox'))
    )

    # 启用网络监控
    driver.execute_cdp_cmd('Network.enable', {})
    
    # 注册请求拦截器
    driver.request_interceptor = request_interceptor

    # 查找频道列表元素
    channel_list = driver.find_elements(By.CSS_SELECTOR, '.channel-class')  # 替换为实际频道列表的类名

    # 获取默认直播源
    video_element = driver.find_element(By.ID, 'videoBox')
    default_live_url = video_element.get_attribute('src')
    live_sources.append(default_live_url)
    print(f"找到默认直播源: {default_live_url}")

    # 循环遍历频道并点击
    for index, channel in enumerate(channel_list):
        try:
            print(f"切换到频道: {channel.text}")
            channel.click()  # 模拟点击频道

            # 等待视频盒子更新
            time.sleep(3)

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
