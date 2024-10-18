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

    # 等待页面加载并找到暂停按钮
    pause_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'animationPause'))
    )
    
    # 滚动页面以确保按钮可见
    driver.execute_script("arguments[0].scrollIntoView(true);", pause_button)
    time.sleep(1)  # 给页面一些时间进行调整
    
    # 点击暂停按钮，显示频道图标
    pause_button.click()
    print("已点击暂停按钮，频道图标显示出来")

    # 等待频道图标加载出来
    channel_icons = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.swiper-slide'))
    )

    actions = ActionChains(driver)

    for index, icon in enumerate(channel_icons):
        # 滚动到该图标并确保它在视图内
        driver.execute_script("arguments[0].scrollIntoView(true);", icon)
        time.sleep(1)  # 等待滑动完成

        # 模拟点击频道图标
        icon.click()
        print(f"已点击频道 {index + 1} 图标")

        # 点击播放按钮
        play_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'animationPlay'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", play_button)
        play_button.click()
        print(f"已点击频道 {index + 1} 的播放按钮")

        # 获取当前直播源
        live_source = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )
        live_url = live_source.get_attribute('src')
        live_sources.append(live_url)
        print(f"找到频道 {index + 1} 的直播源: {live_url}")

        # 暂停当前频道播放（每次获取到直播源后暂停当前频道）
        pause_button.click()

        # 等待切换
        time.sleep(2)

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
