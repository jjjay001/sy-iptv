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

    # 抓取默认频道的直播源URL
    live_url = video_element.get_attribute('src')
    if live_url and live_url.endswith('.m3u8'):
        live_sources.append(live_url)
        print(f"找到默认直播源: {live_url}")

    # 定义最大切换次数（避免无限循环）
    max_swipes = 10
    for i in range(max_swipes):
        try:
            # 暂停视频
            driver.execute_script("arguments[0].pause();", video_element)
            time.sleep(1)  # 等待暂停

            # 保存当前的直播源URL
            current_url = video_element.get_attribute('src')
            print(f"当前直播源: {current_url}")

            # 滚动页面，确保视频元素可见
            driver.execute_script("arguments[0].scrollIntoView();", video_element)
            time.sleep(1)  # 等待滚动完成

            # 查找频道名称
            channel_name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'channelName'))
            )
            print(f"当前频道: {channel_name_element.text}")

            # 模拟左滑动操作
            driver.execute_script("window.scrollBy(-100, 0);")  # 左滑动
            time.sleep(1)  # 等待滑动效果

            # 播放视频
            driver.execute_script("arguments[0].play();", video_element)
            time.sleep(3)  # 等待视频加载和播放

            # 等待视频URL发生变化
            try:
                new_url = WebDriverWait(driver, 10).until(
                    lambda d: d.find_element(By.TAG_NAME, 'video').get_attribute('src') != current_url
                )
                # 检查新URL并存储
                live_url = video_element.get_attribute('src')
                if live_url and live_url.endswith('.m3u8'):
                    live_sources.append(live_url)
                    print(f"找到新的直播源: {live_url}")
            except Exception as url_change_e:
                print(f"未能检测到频道变化: {url_change_e}")
                print(traceback.format_exc())
                break  # 如果未能检测到变化，则退出循环

        except Exception as inner_e:
            print(f"处理频道时发生错误: {inner_e}")
            print(traceback.format_exc())
            break  # 如果发生错误，退出循环

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
