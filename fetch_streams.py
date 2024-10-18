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

    # 获取当前频道名称和URL
    for _ in range(10):  # 假设我们要抓取10个频道
        # 获取当前视频的URL
        video_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'videoBox'))
        )
        live_url = video_element.get_attribute('src')

        # 获取当前频道名称
        channel_name = driver.find_element(By.ID, 'channelName').text

        if live_url:
            live_sources.append({'channel': channel_name, 'url': live_url})
            print(f"找到频道 {channel_name} 的直播源: {live_url}")

        # 点击下方的频道名称进行切换
        channel_button = driver.find_element(By.XPATH, "//p[contains(@class, 'BtnInfo') and text()='点此播放']")
        channel_button.click()

        # 等待视频切换
        time.sleep(2)  # 根据需要调整等待时间

except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭浏览器
    driver.quit()

# 生成 .m3u 文件
with open('live_streams.m3u', 'w') as f:
    f.write('#EXTM3U\n')
    for index, source in enumerate(live_sources, start=1):
        f.write(f'#EXTINF:-1, {source["channel"]}\n')
        f.write(f'{source["url"]}\n')

print("已生成 live_streams.m3u 文件")
