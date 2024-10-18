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

    # 获取默认直播源
    video_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'videoBox'))
    )
    default_live_url = video_element.get_attribute('src')
    live_sources.append(default_live_url)
    print(f"找到默认直播源: {default_live_url}")

    # 循环抓取其他频道
    for i in range(2, 11):  # 假设频道从2到10，你可以根据实际情况调整范围
        # 调用滑动的 JavaScript，使用 swiper.slideTo() 方法
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
