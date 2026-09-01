import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ============================================================
# Chrome 配置
# ============================================================
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')
options.add_argument('--window-size=640,1000')

# 【修改1】DOM解析完即返回，防止因外链或慢速静态资源挂起导致 TimeoutException
options.page_load_strategy = 'eager'

options.add_argument(
    '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) '
    'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
)

print("正在启动 Chrome...")
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(20)

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

def get_valid_m3u8_url(timeout=8):
    """【修改2】安全获取有效的 .m3u8 视频流地址，自动过滤掉 html 页面链接"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            video = driver.find_element(By.ID, "videoBox")
            src = video.get_attribute("src")
            if src and (src.endswith(".m3u8") or "m3u8" in src or ("http" in src and not src.endswith(".html"))):
                return src
        except Exception:
            pass
        time.sleep(0.5)
    return None

# ============================================================
# 主程序
# ============================================================
try:
    url = "http://m.snrtv.com/snrtv_tv/index.html"
    print(f"正在打开网页: {url}")
    
    try:
        driver.get(url)
    except TimeoutException:
        print("网页加载超时（已忽略，继续解析 DOM）...")

    # 等待 Swiper 区域就绪
    print("等待频道列表加载...")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#programSwiper .swiper-slide"))
    )
    time.sleep(2)

    # 【修改3】直接获取所有 slide 进行迭代与点击切台
    slides = driver.find_elements(By.CSS_SELECTOR, "#programSwiper .swiper-slide")
    print(f"检测到共有 {len(slides)} 个频道选项")

    for idx, slide in enumerate(slides):
        channel_name = channel_ys.get(idx, f"陕西频道_{idx}")
        print(f"\n========== 正在获取频道 [{idx}]: {channel_name} ==========")

        try:
            # 方案1: JS 强制点击 Slide 节点
            driver.execute_script("arguments[0].click();", slide)
            # 方案2: 配合 Swiper 实例的 slideTo 强制跳转
            driver.execute_script(f"""
            const swiperEl = document.querySelector('#programSwiper');
            if (swiperEl && swiperEl.swiper) {{
                swiperEl.swiper.slideTo({idx});
            }}
            """)
        except Exception as e:
            print(f"触发切台指令失败: {e}")

        # 循环校验获取新的 m3u8
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

    # 写入陕西广电系列
    for channel_name, source in live_sources:
        f.write(f"#EXTINF:-1, {channel_name}\n")
        f.write(f"{source}\n")

    # 写入西安电视台系列
    for channel_name, source in additional_sources:
        f.write(f"#EXTINF:-1, {channel_name}\n")
        f.write(f"{source}\n")

print("========================================")
print(f"已生成 ShaanxiTV.m3u 文件，共获取 {len(live_sources)} 个陕西广电直播源")
print("========================================")

# ============================================================
# 【修改4】熔断机制：若未获取到任何陕西源，主动抛出 exit 1 触发 GitHub Actions 30 分钟重试
# ============================================================
if len(live_sources) == 0:
    print("\n[ERROR] 本次未成功抓取到任何陕西广电直播源，触发退出码 1 启动重试机制！")
    sys.exit(1)
