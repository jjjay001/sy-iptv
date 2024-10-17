from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 设置Selenium的Chrome选项（可选）
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式，不打开浏览器界面（可选）
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 启动Chrome浏览器
driver = webdriver.Chrome(options=options)

# 直播源URL列表
live_sources = []

try:
    # 打开目标网页
    url = "http://m.snrtv.com/snrtv_tv/index.html"  # 替换为实际的直播页面URL
    driver.get(url)

    # 等待页面加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'channel-selector'))  # 替换为实际的频道选择器类名
    )

    # 假设频道选择器是一个可滚动的容器
    channel_selector = driver.find_element(By.CLASS_NAME, 'channel-selector')  # 替换为实际选择器

    # 滑动到所有频道
    while True:
        # 获取当前显示的频道
        channels = channel_selector.find_elements(By.CLASS_NAME, 'channel-item')  # 替换为实际频道项的类名
        for index, channel in enumerate(channels, start=1):
            # 点击频道以加载视频源
            channel.click()
            time.sleep(2)  # 等待视频源加载

            # 获取视频标签
            try:
                live_video = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'video'))
                )
                live_url = live_video.get_attribute('src')
                if live_url:  # 确保URL不为空
                    live_sources.append(live_url)
                    print(f"找到直播源 {index}: {live_url}")
            except Exception as e:
                print(f"未找到视频源: {e}")

        # 检查是否还有更多频道可供滑动
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", channel_selector)
        time.sleep(1)  # 等待滚动

        # 如果频道选择器滚动到顶端，结束循环
        if len(live_sources) >= len(channels):  # 这里可以根据实际情况调整条件
            break

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
