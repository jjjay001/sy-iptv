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

    # 等待页面完全加载并确保 Swiper 实例存在
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'programSwiper'))  # 确保页面加载完毕
    )

    # 确保 Swiper 初始化完毕
    swiper_initialized = False
    for _ in range(10):  # 尝试10次，每次等待1秒
        swiper_initialized = driver.execute_script("""
            if (typeof swiper !== 'undefined' && swiper.initialized) {
                return true;
            } else {
                return false;
            }
        """)
        if swiper_initialized:
            print("Swiper 已初始化")
            break
        time.sleep(1)  # 等待1秒
    if not swiper_initialized:
        raise Exception("Swiper 未能初始化")

    # 获取默认直播源
    video_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'videoBox'))
    )
    default_live_url = video_element.get_attribute('src')
    live_sources.append(default_live_url)
    print(f"找到默认直播源: {default_live_url}")

    # 通过 hash 切换频道
    channel_hash_map = {
        'star': 1,
        'nl': 2,
        '1': 3,
        '2': 4,
        '3': 5,
        '4': 6,
        '5': 7,
        '6': 8,
        '7': 9,
        '8': 10
    }

    # 假设当前的 hash 是 'star'
    cur_hash = 'star'  # 可以根据实际情况进行修改
    if cur_hash in channel_hash_map:
        target_index = channel_hash_map[cur_hash]
        print(f"通过 hash 切换到频道: {cur_hash}")
        driver.execute_script(f"swiper.slideTo({target_index}, 1000, false);")
        time.sleep(1)  # 等待滑动动画结束
        
        # 获取当前直播源
        video_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'videoBox'))
        )
        current_live_url = video_element.get_attribute('src')

        if current_live_url != default_live_url:
            live_sources.append(current_live_url)
            print(f"当前直播源: {current_live_url}")
        else:
            print(f"未检测到新直播源，当前仍为默认频道")

    # 循环抓取其他频道（可选）
    for i in range(2, 11):  # 假设频道从2到10
        driver.execute_script(f"swiper.slideTo({i}, 1000, false);")
        time.sleep(1)  # 等待滑动动画结束
        
        # 获取当前直播源
        video_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'videoBox'))
        )
        current_live_url = video_element.get_attribute('src')

        if current_live_url != default_live_url:
            live_sources.append(current_live_url)
            print(f"当前直播源: {current_live_url}")
        else:
            print(f"未检测到新直播源，跳过第 {i} 频道")

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
