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
    url = "http://m.snrtv.com/snrtv_tv/index.html"  # 替换为实际的直播页面URL
    driver.get(url)

    # 等待频道列表加载完成
    print("等待频道列表加载...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'swiper-slide'))
    )
    print("频道列表已加载.")

    # 获取所有频道的 li 元素
    channel_elements = driver.find_elements(By.XPATH, "//li[contains(@class, 'swiper-slide')]")

    for index, channel in enumerate(channel_elements):
        # 模拟点击每个频道以获取直播源
        print(f"切换到频道 {index + 1}...")
        channel.click()

        # 等待视频标签加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'videoBox'))
        )

        # 获取直播源的 URL
        live_source = driver.find_element(By.ID, 'videoBox')
        live_url = live_source.get_attribute('src')

        # 获取频道名称
        channel_name = driver.find_element(By.ID, 'channelName').text

        if live_url:
            live_sources.append((channel_name, live_url))
            print(f"找到频道 {channel_name} 的直播源: {live_url}")
        else:
            print(f"频道 {channel_name} 的直播源 URL 为 None")

        # 等待一段时间以确保可以加载下一个频道
        time.sleep(1)

except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭浏览器
    driver.quit()

# 生成 .m3u 文件
with open('live_streams.m3u', 'w') as f:
    f.write('#EXTM3U\n')
    for channel_name, source in live_sources:
        f.write(f'#EXTINF:-1, {channel_name}\n')
        f.write(f'{source}\n')

print("已生成 live_streams.m3u 文件")
