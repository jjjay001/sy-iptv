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

    # 等待频道元素出现
    channel_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.channel-name-selector'))  # 根据实际页面结构调整选择器
    )

    # 循环访问每个频道
    for channel in channel_elements:
        try:
            channel.click()  # 点击切换到该频道
            time.sleep(2)  # 等待视频加载

            # 等待视频元素出现
            video_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'video'))
            )

            # 获取直播源的URL
            live_url = video_element.get_attribute('src')
            if live_url and live_url.endswith('.m3u8'):  # 确保是m3u8格式
                live_sources.append(live_url)
                print(f"找到直播源: {live_url}")

        except Exception as inner_e:
            print(f"处理频道时发生错误: {inner_e}")

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
