from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback

# 设置Selenium的Chrome选项
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式（可移除以查看浏览器）
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

    # 等待视频元素出现
    video_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'video'))
    )

    # 直接获取默认频道的直播源URL
    live_url = video_element.get_attribute('src')
    if live_url and live_url.endswith('.m3u8'):
        live_sources.append(live_url)
        print(f"找到默认直播源: {live_url}")

    # 等待频道元素出现
    channel_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.channel-name-selector'))  # 根据实际页面结构调整选择器
    )

    # 循环访问每个频道
    for index, channel in enumerate(channel_elements):
        try:
            # 暂停当前视频
            driver.execute_script("arguments[0].pause();", video_element)  # 暂停视频
            time.sleep(1)  # 等待视频暂停

            # 向左滑动选择下一个频道
            action = webdriver.ActionChains(driver)
            action.move_to_element(channel).move_by_offset(-100, 0).click().perform()  # 左滑并点击
            time.sleep(1)  # 等待滑动和点击效果

            # 点击播放
            video_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'video'))
            )
            driver.execute_script("arguments[0].play();", video_element)  # 播放视频
            time.sleep(1)  # 等待视频播放

            # 获取直播源的URL
            live_url = video_element.get_attribute('src')
            if live_url and live_url.endswith('.m3u8'):  # 确保是m3u8格式
                live_sources.append(live_url)
                print(f"找到频道 {index + 1} 的直播源: {live_url}")

        except Exception as inner_e:
            print(f"处理频道时发生错误: {inner_e}")
            print(traceback.format_exc())

except Exception as e:
    print(f"发生错误: {e}")
    print(traceback.format_exc())

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
