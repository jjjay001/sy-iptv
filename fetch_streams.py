import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# ============================================================
# Chrome 配置 (针对加载超时及 SSL/TLS 协议全面优化)
# ============================================================
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')
options.add_argument('--window-size=1280,800')

# 显式指定语言
options.add_argument('--lang=zh-CN')

# 忽略 SSL/TLS 错误
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--allow-insecure-localhost')
options.add_argument('--allow-running-insecure-content')
options.add_argument('--ssl-version-min=tls1.0')
options.add_argument('--ssl-version-max=tls1.3')

# 防封与绕过自动化检测
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# 页面加载策略：eager
options.page_load_strategy = 'eager'

# 标准 Android Chrome 移动端 User-Agent
options.add_argument(
    '--user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
)

# 开启性能日志监听（用于备用或调试）
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

print("正在启动 Chrome...")
driver = webdriver.Chrome(options=options)

driver.set_page_load_timeout(15)
driver.set_script_timeout(10)

# 存储结果列表: [(频道名称, 直播源URL)]
live_sources = []

# 陕西广电频道 data-num 与中文名映射表
num_to_name = {
    "star": "陕西卫视",
    "nl": "农林卫视",
    "1": "陕西新闻资讯",
    "2": "陕西都市青春",
    "3": "陕西影视频道",
    "5": "陕西体育休闲",
    "7": "陕西生活资讯",
    "11": "陕西移动频道"
}

additional_sources = [
    ("西安综合", "https://xatv-yt.xiancity.cn/live/1/index.m3u8"),
    ("西安都市", "https://xatv-yt.xiancity.cn/live/2/index.m3u8"),
    ("西安影视", "https://xatv-yt.xiancity.cn/live/4/index.m3u8"),
    ("西安丝路", "https://xatv-yt.xiancity.cn/live/5/index.m3u8"),
]

def get_valid_m3u8_url(timeout=6):
    """从 video 标签中提取有效的 .m3u8 视频流地址"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            video = driver.find_element(By.ID, "videoBox")
            src = video.get_attribute("src")
            if src and (".m3u8" in src) and not src.startswith("blob:"):
                return src
        except Exception:
            pass
        time.sleep(0.5)
    return None

# ============================================================
# 主程序
# ============================================================
try:
    url_http = "http://m.snrtv.com/snrtv_tv/index.html"
    print(f"正在打开网页: {url_http}")
    
    try:
        driver.get(url_http)
    except TimeoutException:
        print("捕获到页面加载超时，强制停止页面加载并继续解析...")
        try:
            driver.execute_script("window.stop();")
        except Exception:
            pass

    try:
        print(f"当前实际 URL: {driver.current_url}")
        print(f"当前页面标题: {driver.title}")
    except Exception:
        pass

    print("等待频道列表加载...")
    # 过滤掉 swiper 复制的镜像节点，只获取真实的频道列表
    css_selectors = "#programSwiper .swiper-slide:not(.swiper-slide-duplicate)"
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors))
        )
    except TimeoutException:
        print("警告: 显式等待超时，尝试强行寻找已存在的 DOM 节点...")

    time.sleep(2)

    slides = driver.find_elements(By.CSS_SELECTOR, css_selectors)
    print(f"检测到共有 {len(slides)} 个真实频道选项")

    for slide in slides:
        data_num = slide.get_attribute("data-num")
        if not data_num:
            continue
            
        channel_name = num_to_name.get(data_num, f"陕西频道_{data_num}")
        print(f"\n========== 正在获取频道: {channel_name} (data-num={data_num}) ==========")

        try:
            # 点击切换频道
            driver.execute_script("arguments[0].click();", slide)
            # 尝试调用 swiper 的 slideTo 或强制播放
            driver.execute_script(f"""
            const swiperEl = document.querySelector('#programSwiper') || document.querySelector('.swiper-container');
            if (swiperEl && swiperEl.swiper) {{
                swiperEl.swiper.slideNext();
            }}
            const v = document.getElementById('videoBox');
            if (v && v.play) {{ v.play(); }}
            """)
        except Exception as e:
            print(f"触发切台指令失败: {e}")

        # 等待该频道的 m3u8 地址加载刷新
        time.sleep(1.5)
        m3u8_url = get_valid_m3u8_url(timeout=6)

        if m3u8_url:
            print(f"成功获取 [{channel_name}] 直播源: {m3u8_url}")
            if not any(url == m3u8_url for _, url in live_sources):
                live_sources.append((channel_name, m3u8_url))
            else:
                print("与已有直播源重复，跳过")
        else:
            print(f"[{channel_name}] 未能解析到有效 m3u8 地址")

        time.sleep(0.5)

except Exception as e:
    print(f"\n发生错误: {type(e).__name__}: {e}")

finally:
    print("\n正在关闭 Chrome...")
    try:
        driver.quit()
    except Exception:
        pass

# ============================================================
# 生成 M3U 文件
# ============================================================
print("\n正在生成 ShaanxiTV.m3u...")

with open("ShaanxiTV.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")

    for channel_name, source in live_sources:
        f.write(f"#EXTINF:-1, {channel_name}\n")
        f.write(f"{source}\n")

    for channel_name, source in additional_sources:
        f.write(f"#EXTINF:-1, {channel_name}\n")
        f.write(f"{source}\n")

print("========================================")
print(f"已生成 ShaanxiTV.m3u 文件，共获取 {len(live_sources)} 个陕西广电直播源")
print("========================================")

if len(live_sources) == 0:
    print("\n[ERROR] 本次未成功抓取到任何陕西广电直播源，触发退出码 1 启动重试机制！")
    sys.exit(1)
