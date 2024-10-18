from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
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

    # 初始化ActionChains用于执行滑动操作
    actions = ActionChains(driver)

    # 等待视频标签出现，确保页面加载完成
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'video'))
    )

    # 假设我们需要抓取的频道数量
    num_channels = 5  # 假设有5个频道

    for index in range(num_channels):
        # 获取当前视频元素并暂停播放
        live_source = driver.find_element(By.TAG_NAME, 'video')
        driver.execute_script("document.querySelector('video').pause();")

        # 等待视频元素加载完成
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script("""
                let video = document.querySelector('video');
                return video && video.readyState === 4;
            """)
        )

        # 获取当前直播源的 URL
        live_url = live_source.get_attribute('src')
        live_sources.append(live_url)
        print(f"找到频道 {index + 1} 的直播源: {live_url}")

        # 滑动到下一个频道图标
        # 假设频道图标的类名是 'channel-icon'，需要根据实际情况调整
        channel_icons = driver.find_elements(By.CLASS_NAME, 'channel-icon')
        
        # 计算下一个频道的图标位置
        if index < len(channel_icons) - 1:  # 避免越界
            next_icon = channel_icons[index + 1]
            driver.execute_script("arguments[0].scrollIntoView();", next_icon)
            time.sleep(1)  # 等待动画完成

            # 点击播放按钮
            play_button = next_icon.find_element(By.CLASS_NAME, 'play-button')  # 假设播放按钮的类名是 'play-button'
            play_button.click()

            # 等待视频重新加载并获取新的直播源
            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script("""
                    let video = document.querySelector('video');
                    return video && video.readyState === 4 && video.src;
                """)
            )
        else:
            print("已达到最后一个频道，停止滑动。")

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
