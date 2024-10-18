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
        # 获取当前直播源
        live_source = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )

        # 获取直播源的URL
        live_url = live_source.get_attribute('src')
        live_sources.append(live_url)
        print(f"找到频道 {index + 1} 的直播源: {live_url}")

        # 暂停当前视频（通过执行JavaScript暂停）
        driver.execute_script("document.querySelector('video').pause();")

        # 滑动前，确保视频元素可见
        driver.execute_script("arguments[0].scrollIntoView();", live_source)

        # 获取元素位置并检查它是否有大小
        location = live_source.location
        size = live_source.size

        if size['width'] > 0 and size['height'] > 0:
            # 只有在视频元素有可见尺寸时才滑动
            actions.click_and_hold(live_source).move_by_offset(-500, 0).release().perform()
        else:
            print(f"视频元素在频道 {index + 1} 不可见，跳过滑动")

        # 等待切换后的视频加载
        time.sleep(2)  # 可根据实际加载时间调整

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
