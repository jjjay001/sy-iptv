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
    num_channels = 10  # 假设有10个频道

    for index in range(num_channels):
        try:
            # 获取当前直播源
            live_source = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.TAG_NAME, 'video'))
            )

            # 获取直播源的URL
            live_url = live_source.get_attribute('src')
            if live_url:
                live_sources.append(live_url)
                print(f"找到频道 {index + 1} 的直播源: {live_url}")
            else:
                print(f"频道 {index + 1} 的直播源 URL 为 None")

            # 等待一段时间，确保视频缓冲完成
            time.sleep(3)  # 根据需要调整等待时间

            # 暂停当前视频（通过执行JavaScript暂停）
            driver.execute_script("arguments[0].pause();", live_source)

            # 等待1秒，确保视频暂停后再进行切换
            time.sleep(1)

            # 点击点此暂停/换台的按钮
            switch_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'p.BtnInfo'))
            )
            switch_button.click()  # 执行切换频道的操作

            # 等待切换后的视频加载
            time.sleep(3)  # 根据实际加载时间调整

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
