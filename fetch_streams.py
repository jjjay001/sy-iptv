import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# ============================================================
# Chrome 配置 (针对 GitHub Actions CI 环境全面优化)
# ============================================================
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1280,800')

# 显式指定语言
options.add_argument('--lang=zh-CN')

# 忽略 SSL 错误
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-insecure-localhost')

# 防封与绕过自动化检测
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# 恢复默认的 normal 页面加载策略，确保 JS 和 DOM 完全渲染
options.page_load_strategy = 'normal'

# 标准 Android Chrome 移动端 User-Agent
options.add_argument(
    '--user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
)

print("正在启动 Chrome...")
driver = webdriver.Chrome(options=options)

# 适当放宽超时时间
driver.set_page_load_timeout(30)
driver.set_script_timeout(15)

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
        print("捕获到页面加载超时，尝试继续解析...")

    try:
        print(f"当前实际 URL: {driver.current_url}")
        print(f"当前页面标题: {driver.title}")
    except Exception:
        pass

    # 关键：先等待 body 标签出现，确保页面有内容
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        print("[ERROR] 页面 body 加载超时，可能被网络拦截或无响应！")

    print("等待频道列表加载...")
    css_selectors = "#programSwiper .swiper-slide:not(.swiper-slide-duplicate)"
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors))
        )
    except TimeoutException:
        print("警告: 显式等待频道超时。保存当前页面源码用于排查...")
        print(driver.page_source[:1000]) # 打印前1000字符查看页面返回了什么

    time.sleep(3) # 给予额外时间让 Swiper 渲染完成

    slides = driver.find_elements(By.CSS_SELECTOR, css_selectors)
    print(f"检测到共有 {len(slides)} 个真实频道选项")

    for slide in slides:
        data_num = slide.get_attribute("data-num")
        if not data_num:
            continue
            
        channel_name = num_to_name.get(data_num, f"陕西频道_{data_num}")
        print(f"\n========== 正在获取频道: {channel_name} (data-num={data_num}) ==========")

        try:
            driver.execute_script("arguments[0].click();", slide)
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

        time.sleep(2)
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
