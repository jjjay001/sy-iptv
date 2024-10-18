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

def get_live_url():
    """获取当前视频的直播源 URL."""
    try:
        video_source = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )
        live_url = video_source.get_attribute('src')
        return live_url
    except Exception as e:
        print(f"获取直播源时发生错误: {e}")
        return None

try:
    # 打开目标网页
    url = "http://live.snrtv.com"  # 替换为实际的直播页面URL
    driver.get(url)

    # 等待视频标签出现
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'video'))
    )

    # 假设频道名称列表
    channel_names = ["陕西卫视", "新闻资讯", "都市青春", "生活频道", "影视频道", "公共频道", "乐家购物", "体育休闲", "农林卫视", "移动电视"]

    for channel in channel_names:
        # 切换到对应频道
        channel_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[text()='{channel}']"))
        )
        channel_element.click()

        # 等待视频标签更新
        time.sleep(2)  # 等待视频加载

        # 获取直播源URL，最多重试3次
        retries = 3
        live_url = None
        while retries > 0:
            live_url = get_live_url()
            if live_url and live_url.endswith('.m3u8'):
                live_sources.append((channel, live_url))
                print(f"找到频道 {channel} 的直播源: {live_url}")
                break
            else:
                print(f"频道 {channel} 的直播源不是 m3u8 格式，正在重试...")
                time.sleep(1)  # 等待一段时间后重试
                retries -= 1

        if retries == 0 and (not live_url or not live_url.endswith('.m3u8')):
            print(f"频道 {channel} 的直播源未找到或不是 m3u8 格式")

except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭浏览器
    driver.quit()

# 生成 .m3u 文件
with open('live_streams.m3u', 'w') as f:
    f.write('#EXTM3U\n')
    for channel, source in live_sources:
        f.write(f'#EXTINF:-1, {channel}\n')
        f.write(f'{source}\n')

print("已生成 live_streams.m3u 文件")
