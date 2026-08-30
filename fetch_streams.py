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
options.add_argument('--window-size=640,1000')

# 伪装移动端 UA，确保页面加载 H5 移动端逻辑
options.add_argument(
    '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) '
    'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
)

print("正在启动 Chrome...")
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(30)

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
    8: "移动"
}

additional_sources = [
    ("西安综合", "https://xatv-yt.xiancity.cn/live/1/index.m3u8"),
    ("西安都市", "https://xatv-yt.xiancity.cn/live/2/index.m3u8"),
    ("西安商务资讯", "https://xatv-yt.xiancity.cn/live/3/index.m3u8"),
    ("西安影视", "https://xatv-yt.xiancity.cn/live/4/index.m3u8"),
    ("西安丝路", "https://xatv-yt.xiancity.cn/live/5/index.m3u8"),
]

def get_video_url():
    """获取当前视频源地址"""
    try:
        video = driver.find_element(By.ID, "videoBox")
        return video.get_attribute("src")
    except Exception:
        return None

def trigger_swiper_next():
    """使用 JS 驱动 Swiper 切换下一个 Slide（优先 API，备选 TouchEvent）"""
    js_code = """
    const swiperEl = document.querySelector('#programSwiper');
    if (!swiperEl) return false;

    // 方案 1: 如果页面直接挂载了 swiper 实例，调用 API 切换
    if (swiperEl.swiper) {
        swiperEl.swiper.slideNext();
        return "api";
    }

    // 方案 2: 模拟 H5 TouchTouchEvent 拖拽
    const rect = swiperEl.getBoundingClientRect();
    const startX = rect.left + rect.width * 0.8;
    const endX = rect.left + rect.width * 0.2;
    const centerY = rect.top + rect.height / 2;

    const createTouch = (x, y) => new Touch({
        identifier: Date.now(),
        target: swiperEl,
        clientX: x,
        clientY: y
    });

    const dispatchTouch = (type, x, y) => {
        const touch = createTouch(x, y);
        const event = new TouchEvent(type, {
            touches: type === 'touchend' ? [] : [touch],
            targetTouches: type === 'touchend' ? [] : [touch],
            changedTouches: [touch],
            bubbles: true,
            cancelable: true
        });
        swiperEl.dispatchEvent(event);
    };

    dispatchTouch('touchstart', startX, centerY);
    dispatchTouch('touchmove', endX, centerY);
    dispatchTouch('touchend', endX, centerY);
    return "touch_event";
    """
    return driver.execute_script(js_code)

# ============================================================
# 主程序
# ============================================================
try:
    url = "http://m.snrtv.com/snrtv_tv/index.html"
    print(f"正在打开网页: {url}")
    
    try:
        driver.get(url)
    except TimeoutException:
        print("网页加载超时，尝试继续处理...")

    # 等待关键播放器元素
    video_element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "videoBox"))
    )
    
    # 获取默认（第0频道：陕西卫视）
    default_url = get_video_url()
    if default_url:
        print(f"找到默认频道 [陕西卫视]: {default_url}")
        live_sources.append(("陕西卫视", default_url))

    # 等待 Swiper 区域就绪
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "programSwiper"))
    )

    channel_count = 8
    for i in range(1, channel_count + 1):
        print(f"\n========== 尝试获取频道 {i} ==========")
        old_url = get_video_url()
        
        # 触发切换
        mode = trigger_swiper_next()
        print(f"触发 Swiper 切换，响应模式: {mode}")

        # 循环等待 URL 变动
        new_url = None
        for wait_count in range(16):
            time.sleep(0.5)
            new_url = get_video_url()
            if new_url and new_url != old_url:
                break

        # 结果校验与保存
        if new_url and new_url != old_url:
            channel_name = channel_ys.get(i, f"陕西频道_{i}")
            print(f"频道 {i} [{channel_name}] 获取成功: {new_url}")
            
            # 排除特定不需要的频道索引（如第 7 项）
            if i != 7:
                live_sources.append((channel_name, new_url))
        else:
            print(f"频道 {i}: 直播源未发生变化，跳过")

        time.sleep(1)

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
