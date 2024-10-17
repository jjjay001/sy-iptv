from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

# 设置Selenium的Chrome选项（可选）
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式，不打开浏览器界面（可选）
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

    # 等待页面加载
    time.sleep(5)  # 根据页面加载时间调整

    # 找到频道选择器
    channel_selector = driver.find_element(By.CLASS_NAME, 'channel-selector')  # 替换为实际的频道选择器类名

    # 定义滑动操作
    action = ActionChains(driver)

    # 循环抓取频道直播源，每次右滑后再抓取下一个
    for _ in range(5):  # 假设抓取5个频道
        # 查找并获取视频源
        try:
            live_video = driver.find_element(By.TAG_NAME, 'video')
            live_url = live_video.get_attribute('src')
            if live_url:  # 确保URL不为空
                live_sources.append(live_url)
                print(f"找到直播源: {live_url}")
        except Exception as e:
            print(f"未找到视频源: {e}")

        # 模拟向右滑动操作
        action.click_and_hold(channel_selector).move_by_offset(-300, 0).release().perform()  # 向右滑动
        time.sleep(2)  # 等待滑动动画和下一个频道加载

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
