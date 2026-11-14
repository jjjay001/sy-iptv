
import sys
import time
import json
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


# ============================================================
# 基础配置
# ============================================================

MAIN_URL = "http://m.snrtv.com/snrtv_tv/index.html"

BASE_ASSETS = (
    "http://res.cnwest.com/t/site/10001/"
    "a209bcf3e52b0593bd2c51ae47c9d6ab/assets"
)

JS_FILES = [
    "snrtv2020/js/EmperorNewClothes.js",
    "snrtv2020/js/dress.js",
    "snrtv2020/js/Event.js",
    "snrtv2020/js/programGuides.js",
    "public2018/js/zepto.min.js",
    "sxtvs2020/js/swiper.min.4.5.3.js",
]

OUTPUT_FILE = "ShaanxiTV.m3u"

USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 10; K) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Mobile Safari/537.36"
)

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Referer": MAIN_URL,
    "Accept": "*/*",
    "Connection": "close",
}


# ============================================================
# 陕西广电频道映射
# ============================================================

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


# ============================================================
# 西安备用频道（保持原样，不修改）
# ============================================================

additional_sources = [
    ("西安综合", "https://xatv-yt.xiancity.cn/live/1/index.m3u8"),
    ("西安都市", "https://xatv-yt.xiancity.cn/live/2/index.m3u8"),
    ("西安影视", "https://xatv-yt.xiancity.cn/live/4/index.m3u8"),
    ("西安丝路", "https://xatv-yt.xiancity.cn/live/5/index.m3u8"),
]


live_sources = []


# ============================================================
# 日志工具
# ============================================================

def log(message):
    print(
        time.strftime("[%Y-%m-%d %H:%M:%S]"),
        message,
        flush=True
    )


# ============================================================
# 网络诊断
# ============================================================

def test_network():
    log("========== 开始网络诊断 ==========")

    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)

    # 测试主页
    log("测试陕西广电主页：" + MAIN_URL)

    try:
        response = session.get(
            MAIN_URL,
            timeout=(10, 20)
        )

        log(
            f"主页 HTTP 状态码：{response.status_code}，"
            f"下载大小：{len(response.content)} bytes"
        )

        log(f"主页最终 URL：{response.url}")

        if response.status_code == 200:
            log("主页访问正常")
        else:
            log("警告：主页返回非 200 状态码")

    except requests.RequestException as e:
        log(f"主页访问失败：{type(e).__name__}: {e}")

    # 测试关键 JS 文件
    log("")
    log("========== 测试静态资源 CDN ==========")

    success_count = 0

    for item in JS_FILES:
        js_url = f"{BASE_ASSETS}/{item}"

        log(f"测试 JS：{item}")

        try:
            start = time.time()

            response = session.get(
                js_url,
                timeout=(12, 25)
            )

            elapsed = time.time() - start
            size = len(response.content)

            content_type = response.headers.get(
                "Content-Type",
                "未知"
            )

            log(
                f"状态码：{response.status_code} | "
                f"大小：{size} bytes | "
                f"耗时：{elapsed:.2f}s | "
                f"类型：{content_type}"
            )

            if response.status_code == 200 and size > 0:
                success_count += 1
                log("JS 下载成功")
            else:
                log("JS 下载异常")

        except requests.RequestException as e:
            log(f"JS 下载失败：{type(e).__name__}: {e}")

    log(
        f"CDN 检测完成："
        f"{success_count}/{len(JS_FILES)} 个 JS 文件成功"
    )

    session.close()

    return success_count


# ============================================================
# Chrome 配置
# ============================================================

def create_driver():
    options = webdriver.ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--lang=zh-CN")
    options.add_argument("--ignore-certificate-errors")

    options.add_argument(f"--user-agent={USER_AGENT}")

    # DOM 就绪后返回，不必等待全部资源加载
    options.page_load_strategy = "eager"

    # 开启 Chrome 网络日志
    options.set_capability(
        "goog:loggingPrefs",
        {"performance": "ALL"}
    )

    return webdriver.Chrome(options=options)


# ============================================================
# Chrome 网络请求诊断
# ============================================================

def inspect_browser_network(driver):
    log("========== Chrome 网络请求诊断 ==========")

    try:
        entries = driver.get_log("performance")
    except Exception as e:
        log(f"无法读取 Chrome 网络日志：{e}")
        return

    failed_count = 0

    for entry in entries:
        try:
            message = json.loads(entry["message"])["message"]
            method = message.get("method", "")
            params = message.get("params", {})

            if method == "Network.loadingFailed":
                error_text = params.get("errorText", "")

                log(
                    f"网络请求失败："
                    f"requestId={params.get('requestId', '')}，"
                    f"原因={error_text}"
                )

                failed_count += 1

            elif method == "Network.responseReceived":
                response = params.get("response", {})
                response_url = response.get("url", "")

                if (
                    "res.cnwest.com" in response_url
                    or "m.snrtv.com" in response_url
                ):
                    status = response.get("status", 0)

                    if status >= 400:
                        log(
                            f"HTTP 异常：{status} "
                            f"{response_url}"
                        )

        except Exception:
            continue

    log(f"浏览器网络请求失败事件：{failed_count}")


# ============================================================
# 提取 m3u8 地址
# ============================================================

def get_valid_m3u8_url(driver, timeout=10):
    start = time.time()

    while time.time() - start < timeout:
        try:
            result = driver.execute_script("""
                const v = document.getElementById('videoBox');

                if (!v) {
                    return null;
                }

                return {
                    src: v.src || '',
                    currentSrc: v.currentSrc || '',
                    attrSrc: v.getAttribute('src') || ''
                };
            """)

            if result:
                candidates = [
                    result.get("currentSrc", ""),
                    result.get("src", ""),
                    result.get("attrSrc", ""),
                ]

                for src in candidates:
                    if (
                        src
                        and ".m3u8" in src.lower()
                        and not src.startswith("blob:")
                    ):
                        return src

        except Exception:
            pass

        time.sleep(0.5)

    return None


# ============================================================
# 获取频道列表
# ============================================================

def get_channels(driver):
    selector = (
        "#programSwiper "
        ".swiper-slide:not(.swiper-slide-duplicate)"
    )

    log("等待频道列表加载...")

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector)
            )
        )

    except TimeoutException:
        log("频道列表等待超时")
        return []

    # 使用 data-num 去重，避免 Swiper 重复节点
    channels = driver.execute_script("""
        const elements = document.querySelectorAll(
            '#programSwiper .swiper-slide'
        );

        const result = [];
        const seen = new Set();

        for (const el of elements) {
            const num = el.getAttribute('data-num');

            if (!num || seen.has(num)) {
                continue;
            }

            seen.add(num);

            result.push({
                num: num,
                text: (el.innerText || '').trim()
            });
        }

        return result;
    """)

    return channels or []


# ============================================================
# 切换频道
# ============================================================

def switch_channel(driver, data_num):
    try:
        result = driver.execute_script("""
            const num = arguments[0];

            const elements = document.querySelectorAll(
                '#programSwiper .swiper-slide'
            );

            for (const el of elements) {
                if (el.getAttribute('data-num') === num) {
                    el.click();
                    return true;
                }
            }

            return false;
        """, str(data_num))

        return bool(result)

    except Exception as e:
        log(f"切换频道失败：{e}")
        return False


# ============================================================
# 抓取陕西广电直播源
# ============================================================

def fetch_snrtv():
    driver = None

    try:
        log("========== 启动 Chrome ==========")

        driver = create_driver()

        driver.set_page_load_timeout(45)
        driver.set_script_timeout(20)

        log(f"正在打开网页：{MAIN_URL}")

        try:
            driver.get(MAIN_URL)

        except TimeoutException:
            log("页面加载超时，继续检查当前 DOM")

        log(f"当前 URL：{driver.current_url}")
        log(f"当前标题：{driver.title}")

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME, "body")
                )
            )
        except TimeoutException:
            log("警告：页面 body 加载超时")

        time.sleep(3)

        try:
            state = driver.execute_script(
                "return document.readyState"
            )

            log(f"页面 readyState：{state}")

            log(
                "页面源码长度："
                f"{len(driver.page_source)}"
            )

        except Exception:
            pass

        channels = get_channels(driver)

        log(f"检测到频道数量：{len(channels)}")

        if not channels:
            log("没有检测到频道列表")

            log("========== 当前页面源码 ==========")

            try:
                print(
                    driver.page_source[:3000],
                    flush=True
                )
            except Exception:
                pass

            log("========== 页面脚本加载状态 ==========")

            try:
                scripts = driver.execute_script("""
                    return Array.from(
                        document.scripts
                    ).map(s => s.src || '[inline script]');
                """)

                for script in scripts:
                    log(f"页面脚本：{script}")

            except Exception:
                pass

            inspect_browser_network(driver)
            return

        # 遍历频道
        for channel in channels:
            data_num = str(channel.get("num", ""))

            channel_name = num_to_name.get(
                data_num,
                f"陕西频道_{data_num}"
            )

            log("")
            log(
                f"========== 获取频道："
                f"{channel_name} ({data_num}) =========="
            )

            # 记录切台前的视频地址
            old_url = None

            try:
                old_url = driver.execute_script("""
                    const v = document.getElementById('videoBox');
                    return v ? (v.currentSrc || v.src || '') : '';
                """)
            except Exception:
                pass

            if not switch_channel(driver, data_num):
                log("未能执行频道切换")
                continue

            # 等待视频地址变化
            new_url = None
            start = time.time()

            while time.time() - start < 15:
                new_url = get_valid_m3u8_url(
                    driver,
                    timeout=1
                )

                if new_url:
                    if new_url != old_url or not old_url:
                        break

                time.sleep(0.5)

            if new_url:
                log(
                    f"成功获取直播源："
                    f"{channel_name} -> {new_url}"
                )

                if not any(
                    url == new_url
                    for _, url in live_sources
                ):
                    live_sources.append(
                        (channel_name, new_url)
                    )
                else:
                    log("该直播地址重复，跳过")

            else:
                log(
                    f"{channel_name} "
                    "未能获取有效 m3u8 地址"
                )

            time.sleep(1)

        inspect_browser_network(driver)

    except WebDriverException as e:
        log(
            f"Chrome 或 Selenium 异常："
            f"{type(e).__name__}: {e}"
        )

    except Exception as e:
        log(
            f"抓取过程异常："
            f"{type(e).__name__}: {e}"
        )

    finally:
        if driver:
            log("正在关闭 Chrome...")

            try:
                driver.quit()
            except Exception:
                pass


# ============================================================
# 生成 M3U 文件
# ============================================================

def generate_m3u():
    log("========== 生成 M3U 文件 ==========")

    all_sources = []
    seen_urls = set()

    for name, url in live_sources + additional_sources:
        if not url or url in seen_urls:
            continue

        seen_urls.add(url)
        all_sources.append((name, url))

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("#EXTM3U\n")

        for channel_name, source in all_sources:
            f.write(
                f"#EXTINF:-1, {channel_name}\n"
            )

            f.write(source + "\n")

    log(f"M3U 文件生成成功：{OUTPUT_FILE}")

    log(f"陕西广电频道：{len(live_sources)} 个")
    log(f"西安备用频道：{len(additional_sources)} 个")
    log(f"最终文件频道总数：{len(all_sources)} 个")


# ============================================================
# 主程序
# ============================================================

def main():
    log("========================================")
    log("陕西广电直播源自动抓取程序启动")
    log("========================================")

    # 第一步：网络诊断
    cdn_success = test_network()

    log(
        f"静态资源可访问数量："
        f"{cdn_success}/{len(JS_FILES)}"
    )

    # 第二步：抓取陕西广电频道
    fetch_snrtv()

    # 第三步：判断抓取结果
    # 0 个频道时，不生成、不覆盖原文件
    if len(live_sources) == 0:
        log("未获取到任何陕西广电直播源！")
        log("本次不生成、不覆盖 ShaanxiTV.m3u")
        log("保留上一次成功生成的文件")
        sys.exit(1)

    # 第四步：只有抓取成功才生成 M3U
    generate_m3u()

    log("========================================")
    log(f"陕西广电直播源获取数量：{len(live_sources)}")
    log("M3U 文件更新成功")
    log("========================================")

    sys.exit(0)


if __name__ == "__main__":
    main()
