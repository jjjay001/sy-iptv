from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

# 设置 Chrome 选项
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 启动 Chrome 浏览器
driver = webdriver.Chrome(options=options)

# 直播源 URL 列表
live_sources = []

try:
    # 打开目标网页
    driver.get("http://m.snrtv.com/snrtv_tv/index.html")

    # 等待 Hls.js 加载
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return typeof Hls !== 'undefined';")  # 确保 Hls 可用
    )
    
    # 获取默认直播源
    video_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'videoBox'))
    )
    default_live_url = video_element.get_attribute('src')
    live_sources.append(default_live_url)
    print(f"找到默认直播源: {default_live_url}")

    # 切换频道的示例列表
    channels = [
        "http://stream.snrtv.com/sxbc-star-dnyXZ6.m3u8",  # 频道示例
        # 添加其他频道的 URL
    ]

    for channel_url in channels:
        print(f"通过 Hls.js 切换到频道: {channel_url}")
        driver.execute_script(f"""
            var video = document.getElementById('videoBox');
            if (Hls) {{
                var hls = new Hls();
                hls.loadSource('{channel_url}');
                hls.attachMedia(video);
                video.play();
            }}
        """)
        time.sleep(5)  # 等待播放一段时间

        # 获取当前直播源
        current_live_url = video_element.get_attribute('src')
        if current_live_url != default_live_url:
            live_sources.append(current_live_url)
            print(f"当前直播源: {current_live_url}")
        else:
            print(f"未检测到新直播源，跳过频道 {channel_url}")

except Exception as e:
    print(f"发生错误: {e}")
finally:
    driver.quit()

# 生成 .m3u 文件
with open('live_streams.m3u', 'w') as f:
    f.write('#EXTM3U\n')
    for index, source in enumerate(live_sources, start=1):
        f.write(f'#EXTINF:-1, Channel {index}\n')
        f.write(f'{source}\n')

print("已生成 live_streams.m3u 文件")
