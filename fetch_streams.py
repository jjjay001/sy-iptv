from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


# ============================================================
# Chrome 配置
# ============================================================

options = webdriver.ChromeOptions()

options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')

# 页面本身是移动端 640px 宽
# 不要再使用 1920x1080
options.add_argument('--window-size=640,1000')

options.add_argument('--disable-extensions')
options.add_argument('--disable-background-networking')

print("正在启动 Chrome...")

try:

    driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)

    # 再强制设置一次窗口尺寸
    driver.set_window_size(640, 1000)

    print("Chrome 启动成功")

except Exception as e:

    print(
        f"Chrome 启动失败: "
        f"{type(e).__name__}: {e}"
    )

    raise


# ============================================================
# 直播源
# ============================================================

live_sources = []


# ============================================================
# 陕西频道名称
# ============================================================

channel_ys = {
    1: "农林卫视",
    2: "新闻资讯",
    3: "都市青春",
    4: "银龄",
    5: "秦腔",
    6: "体育休闲",
    8: "移动"
}


# ============================================================
# 额外直播源
# ============================================================

additional_sources = [

    (
        "西安综合",
        "https://xatv-yt.xiancity.cn/live/1/index.m3u8"
    ),

    (
        "西安都市",
        "https://xatv-yt.xiancity.cn/live/2/index.m3u8"
    ),

    (
        "西安商务资讯",
        "https://xatv-yt.xiancity.cn/live/3/index.m3u8"
    ),

    (
        "西安影视",
        "https://xatv-yt.xiancity.cn/live/4/index.m3u8"
    ),

    (
        "西安丝路",
        "https://xatv-yt.xiancity.cn/live/5/index.m3u8"
    ),

]


# ============================================================
# 获取当前直播 URL
# ============================================================

def get_video_url():

    try:

        video = driver.find_element(
            By.ID,
            "videoBox"
        )

        return video.get_attribute("src")

    except Exception:

        return None


# ============================================================
# 获取 Swiper 信息
# ============================================================

def print_swiper_info():

    print("")
    print("========== programSwiper 信息 ==========")

    try:

        swiper = driver.find_element(
            By.ID,
            "programSwiper"
        )

        info = driver.execute_script(
            """
            const el = arguments[0];

            const rect = el.getBoundingClientRect();

            const wrapper =
                el.querySelector('.swiper-wrapper');

            const slides =
                el.querySelectorAll('.swiper-slide');

            return {
                rect: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                },

                scrollWidth: el.scrollWidth,
                scrollHeight: el.scrollHeight,

                slideCount: slides.length,

                wrapperHTML:
                    wrapper
                    ? wrapper.outerHTML.substring(0, 3000)
                    : null
            };
            """,
            swiper
        )

        print(info)

    except Exception as e:

        print(
            f"获取 Swiper 信息失败: "
            f"{type(e).__name__}: {e}"
        )

    print("========== programSwiper 信息结束 ==========")
    print("")


# ============================================================
# 滑动 Swiper
# ============================================================

def swipe_swiper(distance=-250):

    swiper = WebDriverWait(
        driver,
        10
    ).until(
        EC.presence_of_element_located(
            (By.ID, "programSwiper")
        )
    )

    # --------------------------------------------------------
    # 获取元素位置
    # --------------------------------------------------------

    rect = driver.execute_script(
        """
        const r = arguments[0].getBoundingClientRect();

        return {
            x: r.x,
            y: r.y,
            width: r.width,
            height: r.height
        };
        """,
        swiper
    )

    print(
        "Swiper位置: "
        f"x={rect['x']}, "
        f"y={rect['y']}, "
        f"width={rect['width']}, "
        f"height={rect['height']}"
    )


    # --------------------------------------------------------
    # 确保 Swiper 在可视区域
    # --------------------------------------------------------

    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: 'center',
            inline: 'center'
        });
        """,
        swiper
    )

    time.sleep(0.5)


    # --------------------------------------------------------
    # 使用 Swiper 元素作为滑动对象
    # --------------------------------------------------------

    action = ActionChains(driver)

    action.move_to_element(swiper)

    action.click_and_hold()

    action.pause(0.3)

    action.move_by_offset(
        distance,
        0
    )

    action.pause(0.3)

    action.release()

    action.perform()

    print(
        f"Swiper 滑动完成，距离: {distance}"
    )


# ============================================================
# 主程序
# ============================================================

try:

    url = (
        "http://m.snrtv.com/"
        "snrtv_tv/index.html"
    )

    print("")
    print(
        f"正在打开网页: {url}"
    )

    # --------------------------------------------------------
    # 打开网页
    # --------------------------------------------------------

    try:

        driver.get(url)

        print("网页请求完成")

    except TimeoutException:

        print(
            "网页加载超过30秒，继续执行"
        )


    # --------------------------------------------------------
    # 等待 videoBox
    # --------------------------------------------------------

    print(
        "等待 videoBox..."
    )

    video_element = WebDriverWait(
        driver,
        15
    ).until(
        EC.presence_of_element_located(
            (By.ID, "videoBox")
        )
    )

    print(
        "videoBox 找到"
    )


    # --------------------------------------------------------
    # 默认直播源
    # --------------------------------------------------------

    default_live_url = (
        video_element.get_attribute("src")
    )

    print(
        f"找到默认直播源: "
        f"{default_live_url}"
    )


    if default_live_url:

        live_sources.append(
            (
                "陕西卫视",
                default_live_url
            )
        )


    # --------------------------------------------------------
    # 等待 programSwiper
    # --------------------------------------------------------

    print(
        "等待 programSwiper..."
    )

    swiper = WebDriverWait(
        driver,
        15
    ).until(
        EC.presence_of_element_located(
            (By.ID, "programSwiper")
        )
    )

    print(
        "programSwiper 找到"
    )


    # --------------------------------------------------------
    # 等待 Swiper 内部 slide
    # --------------------------------------------------------

    try:

        WebDriverWait(
            driver,
            10
        ).until(
            lambda d:
            len(
                d.find_elements(
                    By.CSS_SELECTOR,
                    "#programSwiper .swiper-slide"
                )
            ) > 0
        )

    except TimeoutException:

        print(
            "没有检测到 swiper-slide"
        )


    # --------------------------------------------------------
    # 打印 Swiper 信息
    # --------------------------------------------------------

    print_swiper_info()


    # ========================================================
    # 开始切换频道
    # ========================================================

    channel_count = 8


    for i in range(
        1,
        channel_count + 1
    ):

        print("")
        print(
            f"========== "
            f"频道 {i} "
            f"=========="
        )


        # ----------------------------------------------------
        # 切换之前的 URL
        # ----------------------------------------------------

        old_url = get_video_url()

        print(
            f"滑动前 URL: "
            f"{old_url}"
        )


        # ----------------------------------------------------
        # 滑动
        # ----------------------------------------------------

        try:

            swipe_swiper(
                distance=-250
            )

        except Exception as e:

            print(
                f"Swiper 滑动失败: "
                f"{type(e).__name__}: {e}"
            )

            continue


        # ----------------------------------------------------
        # 等待频道切换
        # ----------------------------------------------------

        print(
            "等待直播源切换..."
        )

        new_url = None


        # 最多等待 8 秒
        for wait_count in range(16):

            time.sleep(0.5)

            new_url = get_video_url()

            print(
                f"  检测 {wait_count + 1}/16: "
                f"{new_url}"
            )

            if (
                new_url
                and
                new_url != old_url
            ):

                break


        # ----------------------------------------------------
        # 判断结果
        # ----------------------------------------------------

        if (
            new_url
            and
            new_url != old_url
        ):

            print(
                f"频道 {i} 获取成功:"
            )

            print(
                f"  {new_url}"
            )


            # ------------------------------------------------
            # 第7次不保存
            # ------------------------------------------------

            if i not in [7]:

                live_sources.append(
                    (
                        i,
                        new_url
                    )
                )

            default_live_url = new_url


        else:

            print(
                f"频道 {i}: "
                "直播源没有变化"
            )


        time.sleep(1)


# ============================================================
# 异常
# ============================================================

except Exception as e:

    print("")
    print(
        f"发生错误: "
        f"{type(e).__name__}: {e}"
    )


# ============================================================
# 关闭 Chrome
# ============================================================

finally:

    print("")
    print(
        "正在关闭 Chrome..."
    )

    try:

        driver.quit()

        print(
            "Chrome 已关闭"
        )

    except Exception as e:

        print(
            f"关闭 Chrome 时发生错误: "
            f"{type(e).__name__}: {e}"
        )


# ============================================================
# 生成 M3U
# ============================================================

print("")
print(
    "正在生成 ShaanxiTV.m3u..."
)


with open(
    "ShaanxiTV.m3u",
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "#EXTM3U\n"
    )


    # --------------------------------------------------------
    # 陕西广电
    # --------------------------------------------------------

    for channel_id, source in live_sources:

        channel_name = channel_ys.get(
            channel_id,
            "陕西卫视"
        )

        f.write(
            f"#EXTINF:-1, {channel_name}\n"
        )

        f.write(
            f"{source}\n"
        )


    # --------------------------------------------------------
    # 西安电视台
    # --------------------------------------------------------

    for channel_name, source in additional_sources:

        f.write(
            f"#EXTINF:-1, {channel_name}\n"
        )

        f.write(
            f"{source}\n"
        )


# ============================================================
# 输出结果
# ============================================================

print("")
print(
    "========================================"
)

print(
    "已生成 ShaanxiTV.m3u 文件"
)

print(
    f"共获取陕西广电直播源: "
    f"{len(live_sources)} 个"
)

print(
    "========================================"
)


for channel_id, source in live_sources:

    print(
        f"{channel_id}: {source}"
    )
