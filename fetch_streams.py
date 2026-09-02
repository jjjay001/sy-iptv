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

# 【核心修复】改为 'eager' 或 'none'，不再傻等网页所有广告/跟踪脚本/媒体加载完成
options.page_load_strategy = 'eager'

# 更标准的 Android Chrome 移动端 User-Agent
options.add_argument(
    '--user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
)

# 开启性能日志监听（用于捕获网络请求中的 .m3u8 真实接口）
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

print("正在启动 Chrome...")
driver = webdriver.Chrome(options=options)

# 【核心修复】将渲染器超时时间放宽到 15 秒，配合 script/page_load 超时拦截
driver.set_page_load_timeout(15)
driver.set_script_timeout(10)

# 存储结果列表: [(频道名称, 直播源URL)]
live_sources = []

# 频道映射表
channel_ys = {
    0: "陕西卫视",
    1: "农林卫视",
    2: "新闻资讯",
    3: "都市青春",
    4: "银龄",
    5: "秦腔",
    6: "体育休闲",
    7: "移动"
}

additional_sources = [
    ("西安综合", "https://xatv-yt.xiancity.cn/live/1/index.m3u8"),
    ("西安都市", "https://xatv-yt.xiancity.cn/live/2/index.m3u8"),
    ("西安商务资讯", "https://xatv-yt.xiancity.cn/live/3/index.m3u8"),
    ("西安影视", "https://xatv-yt.xiancity.cn/live/4/index.m3u8"),
    ("西安丝路", "https://xatv-yt.xiancity.cn/live/5/index.m3u8"),
]

def extract_m3u8_from_network_logs():
    """【双保险 1】从 Performance 网络日志中逆向抓取最新发出的 .m3u8 请求"""
    try:
        logs = driver.get_log('performance')
        for entry in reversed(logs):
            log = json.loads(entry['message'])['message']
            if log['method'] == 'Network.requestWillBeSent':
                url = log['params']['request']['url']
                if '.m3u8' in url and not url.endswith('.html'):
                    return url
    except Exception:
        pass
    return None

def get_valid_m3u8_url(timeout=8):
    """【双保险 2】多维检索并提取有效的 .m3u8 视频流地址"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 1. 优先查网络抓包日志
        net_url = extract_m3u8_from_network_logs()
        if net_url:
            return net_url

        # 2. 备用逻辑：解析 DOM 节点
        try:
            video = driver.find_element(By.ID, "videoBox")
            src = video.get_attribute("src")
            if src and (src.endswith(".m3u8") or "m3u8" in src) and not src.startswith("blob:"):
                return src
        except Exception:
            pass

        time.sleep(0.5)
    return None

# ============================================================
# 主程序
# ============================================================
try:
    url_https = "https://m.snrtv.com/snrtv_tv/index.html"
    url_http = "http://m.snrtv.com/snrtv_tv/index.html"
    
    print(f"正在打开网页: {url_https}")
    
    try:
        driver.get(url_https)
    except TimeoutException:
        print("捕获到页面加载超时，强制停止页面加载并继续解析...")
        try:
            driver.execute_script("window.stop();")
        except Exception:
            pass
    except WebDriverException as e:
        if "ERR_SSL" in str(e) or "CIPHER_MISMATCH" in str(e):
            print("警告: HTTPS 失败，尝试回退 HTTP 协议...")
            try:
                driver.get(url_http)
            except TimeoutException:
                driver.execute_script("window.stop();")
        else:
            raise e

    # 打印诊断数据
    try:
        print(f"当前实际 URL: {driver.current_url}")
        print(f"当前页面标题: {driver.title}")
    except Exception:
        pass

    # 等待 Swiper 区域或备用频道节点就绪
    print("等待频道列表加载...")
    css_selectors = "#programSwiper .swiper-slide, .swiper-wrapper .swiper-slide, .channel-list li"
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selectors))
        )
    except TimeoutException:
        print("警告: 显式等待超时，尝试强行寻找已存在的 DOM 节点...")

    time.sleep(2)

    # 获取频道 slide
    slides = driver.find_elements(By.CSS_SELECTOR, css_selectors)
    print(f"检测到共有 {len(slides)} 个频道选项")

    if len(slides) == 0:
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text.replace("\n", " ")[:300]
            print(f"[PAGE BODY HEAD]: {body_text}")
        except Exception:
            pass

    for idx, slide in enumerate(slides):
        channel_name = channel_ys.get(idx, f"陕西频道_{idx}")
        print(f"\n========== 正在获取频道 [{idx}]: {channel_name} ==========")

        try:
            driver.execute_script("arguments[0].click();", slide)
            driver.execute_script(f"""
            const swiperEl = document.querySelector('#programSwiper') || document.querySelector('.swiper-container');
            if (swiperEl && swiperEl.swiper) {{
                swiperEl.swiper.slideTo({idx});
            }}
            const v = document.getElementById('videoBox') || document.querySelector('video');
            if (v && v.play) {{ v.play(); }}
            """)
        except Exception as e:
            print(f"触发切台指令失败: {e}")

        time.sleep(2)

        m3u8_url = get_valid_m3u8_url(timeout=8)

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

# ============================================================
# 熔断机制：若未获取到任何陕西源，主动抛出 exit 1 触发重试机制
# ============================================================
if len(live_sources) == 0:
    print("\n[ERROR] 本次未成功抓取到任何陕西广电直播源，触发退出码 1 启动重试机制！")
    sys.exit(1)
