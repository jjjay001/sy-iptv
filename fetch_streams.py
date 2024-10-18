from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
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

    # 获取页面的尺寸信息
    window_size = driver.execute_script("return { width: window.innerWidth, height: window.innerHeight };")
    screen_width = window_size['width']
    screen_height = window_size['height']

    # 每次滑动的起点和纵向位置
    start_x = screen_width * 3 / 4  # 从屏幕中间靠右 1/4 处开始
    y_position = screen_height / 3  # 纵向位置位于屏幕上三分之一
    move_distance = -100  # 设置每次滑动的距离

    # 通过鼠标拖动事件滑动切换频道
    action = ActionChains(driver)

    channel_count = 10  # 假设有10个频道
    for i in range(1, channel_count + 1):
        print(f"滑动到频道 {i}")
        try:
            # 执行滑动操作
            action.move_by_offset(start_x, y_position).click_and_hold().move_by_offset(move_distance, 0).release().perform()

            time.sleep(3)  # 等待页面完全加载

            # 获取当前直播源
            video_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'videoBox'))
            )
            current_live_url = video_element.get_attribute('src')

            if current_live_url != default_live_url:
                live_sources.append(current_live_url)
                print(f"当前直播源: {current_live_url}")
                default_live_url = current_live_url  # 更新默认直播源为当前直播源
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
