from seleniumwire import webdriver  # 使用Selenium Wire代替Selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

except Exception as e:
    print(f"发生错误: {e}")
    traceback.print_exc()  # 打印完整的堆栈跟踪信息

# 设置Selenium Wire的Chrome选项
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 启动带有Selenium Wire的Chrome浏览器
driver = webdriver.Chrome(options=options)

# 直播源URL列表
live_sources = []

try:
    # 打开目标网页
    url = "http://live.snrtv.com"  # 替换为实际的直播页面URL
    driver.get(url)

    # 假设频道名称列表
    channel_names = ["陕西卫视", "新闻资讯", "都市青春", "生活频道", "影视频道", "公共频道", "乐家购物", "体育休闲", "农林卫视", "移动电视"]

    for channel in channel_names:
        # 切换到对应频道
        channel_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[text()='{channel}']"))
        )
        channel_element.click()

        # 等待视频标签更新
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))  # 假设视频标签为 <video>
        )

        # 监听并获取 m3u8 请求
        m3u8_url = None
        for request in driver.requests:
            if request.response and '.m3u8' in request.url:
                m3u8_url = request.url
                break

        # 确保找到 m3u8 URL
        if m3u8_url:
            live_sources.append((channel, m3u8_url))
            print(f"找到频道 {channel} 的直播源: {m3u8_url}")
        else:
            print(f"未找到频道 {channel} 的 m3u8 格式直播源")

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
