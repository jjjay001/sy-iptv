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

try:
    # 打开目标网页
    url = "http://live.snrtv.com"  # 目标直播页面URL
    driver.get(url)

    # 等待视频标签出现
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'video'))
    )

    # 获取所有频道列表
    channel_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.btnBox li'))
    )

    for channel_element in channel_elements:
        # 获取频道名称
        channel_name = channel_element.text.strip()
        print(f"切换到频道: {channel_name}")

        # 点击该频道以切换
        channel_element.click()
        time.sleep(2)  # 等待视频切换

        # 获取当前视频的URL
        video_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )
        live_url = video_element.get_attribute('src')

        if live_url:
            live_sources.append({'channel': channel_name, 'url': live_url})
            print(f"找到频道 {channel_name} 的直播源: {live_url}")

except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭浏览器
    driver.quit()

# 生成 .m3u 文件
with open('live_streams.m3u', 'w') as f:
    f.write('#EXTM3U\n')
    for source in live_sources:
        f.write(f'#EXTINF:-1, {source["channel"]}\n')
        f.write(f'{source["url"]}\n')

print("已生成 live_streams.m3u 文件")
