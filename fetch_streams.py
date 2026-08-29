from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


# =========================
# Chrome 配置
# =========================

options = webdriver.ChromeOptions()

options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-extensions')
options.add_argument('--disable-background-networking')
options.add_argument('--disable-software-rasterizer')

print("正在启动 Chrome...")

try:
    driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)

    print("Chrome 启动成功")

except Exception as e:
    print(f"Chrome 启动失败: {type(e).__name__}: {e}")
    raise


# =========================
# 直播源
# =========================

live_sources = []

channel_ys = {
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


# =========================
# 获取陕西卫视直播源
# =========================

try:

    url = "http://m.snrtv.com/snrtv_tv/index.html"

    print(f"正在打开网页: {url}")

    try:
        driver.get(url)
        print("网页请求完成")

    except TimeoutException:
        print("网页加载超过30秒，继续执行")

    # =========================
    # 等待 videoBox
    # =========================

    print("等待 videoBox...")

    video_element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.ID, 'videoBox')
        )
    )

    print("videoBox 找到")

    # 获取默认直播源
    default_live_url = video_element.get_attribute('src')

    if default_live_url:

        live_sources.append(
            ("陕西卫视", default_live_url)
        )

        print(
            f"找到默认直播源: "
            f"{default_live_url}"
        )

    else:
        print("videoBox 存在，但是没有获取到 src")


    # =========================
    # 切换频道
    # =========================

    channel_count = 8

    for i in range(1, channel_count + 1):

        print(f"===== 滑动到频道 {i} =====")

        try:

            # 每次重新获取 videoBox
            video_element = WebDriverWait(
                driver,
                10
            ).until(
                EC.presence_of_element_located(
                    (By.ID, 'videoBox')
                )
            )

            # 每次重新创建 ActionChains
            action = ActionChains(driver)

            # 以 videoBox 为起点
            # 避免 move_by_offset 累积导致越界
            action.move_to_element(video_element)

            action.click_and_hold()

            action.move_by_offset(
                -100,
                0
            )

            action.release()

            action.perform()

            print("滑动完成")

            # 等待频道切换
            time.sleep(3)

            # 重新获取 videoBox
            video_element = WebDriverWait(
                driver,
                10
            ).until(
                EC.presence_of_element_located(
                    (By.ID, 'videoBox')
                )
            )

            current_live_url = (
                video_element.get_attribute('src')
            )

            print(
                f"当前 URL: "
                f"{current_live_url}"
            )

            # =========================
            # 判断直播源是否发生变化
            # =========================

            if (
                current_live_url
                and current_live_url != default_live_url
            ):

                # 第7次不加入
                if i not in [7]:

                    live_sources.append(
                        (
                            i,
                            current_live_url
                        )
                    )

                print(
                    f"{i}: 当前直播源: "
                    f"{current_live_url}"
                )

                # 更新当前直播源
                default_live_url = current_live_url

            else:

                print(
                    f"{i}: "
                    "未检测到新直播源"
                )

        except Exception as e:

            print(
                f"频道 {i} 滑动失败: "
                f"{type(e).__name__}: {e}"
            )

        time.sleep(1)


except Exception as e:

    print(
        f"发生错误: "
        f"{type(e).__name__}: {e}"
    )


finally:

    print("正在关闭 Chrome...")

    try:
        driver.quit()

    except Exception as e:

        print(
            f"关闭 Chrome 时发生错误: "
            f"{e}"
        )


# =========================
# 生成 M3U
# =========================

with open(
    'ShaanxiTV.m3u',
    'w',
    encoding='utf-8'
) as f:

    f.write('#EXTM3U\n')

    # 陕西广电频道
    for channel_id, source in live_sources:

        channel_name = channel_ys.get(
            channel_id,
            "陕西卫视"
        )

        f.write(
            f'#EXTINF:-1, {channel_name}\n'
        )

        f.write(
            f'{source}\n'
        )

    # 西安电视台等额外源
    for channel_name, source in additional_sources:

        f.write(
            f'#EXTINF:-1, {channel_name}\n'
        )

        f.write(
            f'{source}\n'
        )


print("\n已生成 ShaanxiTV.m3u 文件")
