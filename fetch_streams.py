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

    # 等待页面完全加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'videoBox'))  # 确保视频盒子加载完毕
    )

    # 获取默认直播源
    video_element = driver.find_element(By.ID, 'videoBox')
    default_live_url = video_element.get_attribute('src')
    live_sources.append(default_live_url)
    print(f"找到默认直播源: {default_live_url}")

    # 通过 swiper 左滑切换频道
    for i in range(1, 10):  # 假设有10个频道
        print(f"滑动到频道 {i}")
        driver.execute_script(f"swiper.slideTo({i}, 1000, false);")  # 模拟滑动到下一个频道
        time.sleep(3)  # 等待滑动动画和视频切换
        
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
