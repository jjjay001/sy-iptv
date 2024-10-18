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

    # 通过 JavaScript 动态获取滑动区域的位置和宽度
    swiper_position = driver.execute_script("""
        const el = document.querySelector('.swiper-container');  // 替换为实际的滑动容器
        const rect = el.getBoundingClientRect();
        return { left: rect.left, right: rect.right, width: rect.width, top: rect.top, bottom: rect.bottom };
    """)

    start_x = swiper_position['right'] - 10  # 滑动的起点，接近容器右边
    end_x = swiper_position['left'] + 10  # 滑动的终点，接近容器左边
    start_y = (swiper_position['top'] + swiper_position['bottom']) / 2  # 垂直居中

    # 通过模拟触摸事件滑动切换频道
    for i in range(1, 10):  # 假设有10个频道
        print(f"滑动到频道 {i}")
        try:
            driver.execute_script(f"""
                const el = document.querySelector('.swiper-container');  // 滑动的实际容器
                const touchStartEvent = new TouchEvent('touchstart', {{
                    touches: [{{ clientX: {start_x}, clientY: {start_y} }}]
                }});
                const touchMoveEvent = new TouchEvent('touchmove', {{
                    touches: [{{ clientX: {end_x}, clientY: {start_y} }}]
                }});
                const touchEndEvent = new TouchEvent('touchend');
                
                el.dispatchEvent(touchStartEvent);
                el.dispatchEvent(touchMoveEvent);
                el.dispatchEvent(touchEndEvent);
            """)
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
            print(f"滑动操作失败: {e}")

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
