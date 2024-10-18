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
options.add_argument('--user-agent=Mozilla/5.0')

# 启动Chrome浏览器
driver = webdriver.Chrome(options=options)

# 直播源URL列表
live_sources = []

try:
    # 打开目标网页
    url = "http://live.snrtv.com"  # 替换为实际的直播页面URL
    driver.get(url)

    # 等待视频标签出现，确保页面加载完成
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'video'))
    )

    # 获取频道名称列表
    channel_names = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'selector-for-channel-names'))  # 替换为实际的选择器
    )

    for index, channel in enumerate(channel_names):
        try:
            # 点击频道名称切换频道
            channel.click()

            # 等待新频道的视频加载
            time.sleep(2)  # 可根据实际加载时间调整

            # 获取当前直播源
            live_source = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'video'))
            )

            # 获取直播源的URL
            live_url = live_source.get_attribute('src')
            live_sources.append(live_url)
            print(f"找到频道 {index + 1} 的直播源: {live_url}")

        except Exception as e:
            print(f"获取频道 {index + 1} 时发生错误: {e}")

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
