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

    # 确认 `swiper` 对象已经定义
    driver.execute_script("""
        if (typeof swiper === 'undefined') {
            throw new Error('Swiper is not initialized');
        }
    """)

    # 获取默认直播源
    video_element = WebDriverWait
