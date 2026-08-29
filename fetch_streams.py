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
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-extensions')
options.add_argument('--disable-background-networking')
options.add_argument('--disable-software-rasterizer')

print("正在启动 Chrome...")

try:
    driver = webdriver.Chrome(options=options)

    # 页面加载最多等待 30 秒
    driver.set_page_load_timeout(30)

    # JS 最多等待 30 秒
    driver.set_script_timeout(30)

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


# 陕西频道名称
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
# 打印 videoBox 父级结构
# ============================================================

def print_page_structure():

    print("")
    print("========== videoBox 页面结构 ==========")

    try:

        structure = driver.execute_script("""
            const video = document.getElementById('videoBox');

            if (!video) {
                return 'videoBox 不存在';
            }

            let result = [];
            let el = video;

            for (let i = 0; i < 8 && el; i++) {

                result.push({
                    tag: el.tagName,
                    id: el.id || '',
                    className: typeof el.className === 'string'
                        ? el.className
                        : '',
                    width: el.offsetWidth,
                    height: el.offsetHeight,
                    outerHTML: el.outerHTML.substring(0, 300)
                });

                el = el.parentElement;
            }

            return JSON.stringify(result, null, 2);
        """)

        print(structure)

    except Exception as e:

        print(
            f"获取页面结构失败: "
            f"{type(e).__name__}: {e}"
        )

    print("========== 页面结构结束 ==========")
    print("")


# ============================================================
# 获取直播源
# ============================================================

try:

    url = "http://m.snrtv.com/snrtv_tv/index.html"

    print("")
    print(f"正在打开网页: {url}")

    # --------------------------------------------------------
    # 打开网页
    # --------------------------------------------------------

    try:

        driver.get(url)

        print("网页请求完成")

    except TimeoutException:

        # 页面里的视频资源可能一直加载
        # 但 DOM 已经可能加载完成
        print(
            "网页加载超过30秒，"
            "继续执行"
        )

    except Exception as e:

        print(
            f"打开网页发生异常: "
            f"{type(e).__name__}: {e}"
        )


    # --------------------------------------------------------
    # 等待 videoBox
    # --------------------------------------------------------

    print("等待 videoBox...")

    try:

        video_element = WebDriverWait(
            driver,
            15
        ).until(
            EC.presence_of_element_located(
                (By.ID, 'videoBox')
            )
        )

        print("videoBox 找到")

    except TimeoutException:

        print(
            "15秒内没有找到 videoBox"
        )

        # 输出页面 HTML 方便排查
        try:

            print(
                driver.execute_script(
                    "return document.body.innerHTML.substring(0, 5000);"
                )
            )

        except Exception:
            pass

        raise


    # --------------------------------------------------------
    # 获取默认直播源
    # --------------------------------------------------------

    default_live_url = (
        video_element.get_attribute('src')
    )

    if default_live_url:

        live_sources.append(
            (
                "陕西卫视",
                default_live_url
            )
        )

        print(
            f"找到默认直播源: "
            f"{default_live_url}"
        )

    else:

        print(
            "videoBox 存在，"
            "但是没有获取到 src"
        )


    # --------------------------------------------------------
    # 打印页面结构
    # --------------------------------------------------------

    print_page_structure()


    # ========================================================
    # 获取浏览器窗口尺寸
    # ========================================================

    try:

        window_size = driver.execute_script("""
            return {
                width: window.innerWidth,
                height: window.innerHeight
            };
        """)

        screen_width = window_size["width"]
        screen_height = window_size["height"]

        print(
            f"浏览器窗口尺寸: "
            f"{screen_width} x {screen_height}"
        )

    except Exception as e:

        print(
            f"获取窗口尺寸失败: {e}"
        )

        # 默认值
        screen_width = 1920
        screen_height = 1080


    # ========================================================
    # 滑动参数
    # ========================================================

    # 原来你的代码：
    #
    # start_x = screen_width * 3 / 4
    # y_position = screen_height / 3
    #
    # 这里稍微调整一下，避免窗口边缘问题。

    start_x = int(screen_width * 0.70)
    y_position = int(screen_height * 0.35)

    move_distance = -150


    print("")
    print(
        f"滑动起点: "
        f"({start_x}, {y_position})"
    )

    print(
        f"滑动距离: "
        f"{move_distance}"
    )

    print("")


    # ========================================================
    # 频道切换
    # ========================================================

    channel_count = 8


    for i in range(
        1,
        channel_count + 1
    ):

        print(
            f"===== 滑动到频道 {i} ====="
        )

        try:

            # ------------------------------------------------
            # 每次重新创建 ActionChains
            # ------------------------------------------------

            action = ActionChains(driver)


            # ------------------------------------------------
            # 关键：
            #
            # move_by_offset 是相对于当前鼠标位置。
            #
            # 如果连续使用：
            #
            # 第一次：+start_x
            # 第二次：再 +start_x
            #
            # 很容易超出窗口。
            #
            # 所以每次重新将鼠标移动到一个固定位置。
            # ------------------------------------------------

            try:

                # Selenium 的鼠标位置可能已经发生偏移。
                # 使用 JavaScript 将页面滚动到顶部，
                # 保证目标区域稳定。

                driver.execute_script(
                    "window.scrollTo(0, 0);"
                )

            except Exception:
                pass


            # ------------------------------------------------
            # 方案：
            # 先通过 ActionChains 从当前位置移动到目标点。
            #
            # 使用 move_by_offset。
            # 如果第一次成功，后面仍可能存在偏移问题，
            # 所以每次 ActionChains 完成后 reset。
            # ------------------------------------------------

            action.move_by_offset(
                start_x,
                y_position
            )

            action.click_and_hold()

            action.move_by_offset(
                move_distance,
                0
            )

            action.release()

            action.perform()

            print("滑动完成")


            # ------------------------------------------------
            # 等待页面 JS 处理频道切换
            # ------------------------------------------------

            time.sleep(3)


            # ------------------------------------------------
            # 获取当前 videoBox
            # ------------------------------------------------

            video_element = WebDriverWait(
                driver,
                10
            ).until(
                EC.presence_of_element_located(
                    (By.ID, 'videoBox')
                )
            )


            # ------------------------------------------------
            # 获取当前直播源
            # ------------------------------------------------

            current_live_url = (
                video_element.get_attribute('src')
            )

            print(
                f"当前 URL: "
                f"{current_live_url}"
            )


            # ------------------------------------------------
            # 判断 URL 是否发生变化
            # ------------------------------------------------

            if (
                current_live_url
                and
                current_live_url != default_live_url
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

                # 更新当前 URL
                default_live_url = (
                    current_live_url
                )

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


        # ----------------------------------------------------
        # 防止 ActionChains 状态残留
        # ----------------------------------------------------

        try:
            action.reset_actions()
        except Exception:
            pass

        time.sleep(1)


# ============================================================
# 异常处理
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
    print("正在关闭 Chrome...")

    try:

        driver.quit()

        print("Chrome 已关闭")

    except Exception as e:

        print(
            f"关闭 Chrome 时发生错误: "
            f"{type(e).__name__}: {e}"
        )


# ============================================================
# 生成 M3U
# ============================================================

print("")
print("正在生成 ShaanxiTV.m3u...")


with open(
    'ShaanxiTV.m3u',
    'w',
    encoding='utf-8'
) as f:

    # --------------------------------------------------------
    # M3U 头
    # --------------------------------------------------------

    f.write(
        '#EXTM3U\n'
    )


    # --------------------------------------------------------
    # 陕西广电频道
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # 额外直播源
    # --------------------------------------------------------

    for channel_name, source in additional_sources:

        f.write(
            f'#EXTINF:-1, {channel_name}\n'
        )

        f.write(
            f'{source}\n'
        )


# ============================================================
# 完成
# ============================================================

print("")
print(
    "已生成 ShaanxiTV.m3u 文件"
)

print(
    f"共获取陕西广电直播源: "
    f"{len(live_sources)} 个"
)

for channel_id, source in live_sources:

    print(
        f"  {channel_id}: {source}"
    )
