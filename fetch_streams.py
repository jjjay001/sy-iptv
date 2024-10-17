from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    url = "live.snrtv.com"  # 替换为实际的直播页面URL
    driver.get(url)

    # 等待动态内容加载，例如查找某个标签
    live_source = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'video'))  # 等待video标签出现
    )

    # 获取直播源的URL
    live_url = live_source.get_attribute('src')
    live_sources.append(live_url)
    print(f"找到直播源: {live_url}")

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
