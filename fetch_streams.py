from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
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
# 频道名称映射
channel_ys = {
    1: "农林卫视",
    2: "新闻资讯",
    3: "都市青春",
    4: "银龄",
    5: "秦腔",
    6: "体育休闲",
    8: "移动"
}

# 添加的直播源
additional_sources = [

   # ("CCTV1","http://148.135.93.213:81/live.php?id=CCTV1"),
    ("大爱频道1","https://pulltv1.wanfudaluye.com/live/tv1.m3u8"),
   # ("CCTV13","http://148.135.93.213:81/live.php?id=CCTV13"),
    ("西安综合","https://xatv-yt.xiancity.cn/live/1/index.m3u8"),
    ("西安都市","https://xatv-yt.xiancity.cn/live/2/index.m3u8"),
    ("西安商务资讯","https://xatv-yt.xiancity.cn/live/3/index.m3u8"),
    ("西安影视","https://xatv-yt.xiancity.cn/live/4/index.m3u8"),
    ("西安丝路","https://xatv-yt.xiancity.cn/live/5/index.m3u8"),
   # ("凤凰中文","http://aktv.top/AKTV/live/aktv/null-3/AKTV.m3u8"),
   # ("凤凰资讯","http://aktv.top/AKTV/live/aktv/null-4/AKTV.m3u8"),
  #  ("寰宇新闻","http://aktv.top/AKTV/live/aktv/null-9/AKTV.m3u8"),
   # ("香港卫视", "http://zhibo.hkstv.tv/livestream/mutfysrq/playlist.m3u8"),
   # ("龍華电影", "http://aktv.top/AKTV/live/aktv/null-23/AKTV.m3u8"),
   # ("翡翠台","http://aktv.top/AKTV/live/aktv/null/AKTV.m3u8"),
   # ("老高与小沫","https://www.goodiptv.club/douyu/236461"),
    ("group-title=\"影视轮播\",济公","https://lunbo.freetv.top/yy/1355265814"),
    ("group-title=\"影视轮播\",宰相刘罗锅","https://lunbo.freetv.top/yy/1382745191"),
    ("group-title=\"影视轮播\",血色浪漫","https://lunbo.freetv.top/yy/1354926676"),
    ("group-title=\"影视轮播\",福贵","https://lunbo.freetv.top/yy/1354926537"),
    ("group-title=\"影视轮播\",少年包青天","https://lunbo.freetv.top/yy/38498680"),
("group-title=\"影视轮播\",神探狄仁杰2","https://lunbo.freetv.top/yy/1382828767"),
("group-title=\"影视轮播\",举起手来-惊险抗日","https://lunbo.freetv.top/yy/1382736877"),
("group-title=\"影视轮播\",神探狄仁杰1","https://lunbo.freetv.top/yy/1354930934"),
("group-title=\"影视轮播\",笑傲江湖","https://lunbo.freetv.top/yy/1354930909"),
("group-title=\"影视轮播\",康熙王朝","https://lunbo.freetv.top/yy/1382736818"),
("group-title=\"影视轮播\",西游记后传","https://lunbo.freetv.top/yy/1382736846"),
("group-title=\"影视轮播\",西游记张卫健版","https://lunbo.freetv.top/yy/1354936155"),
("group-title=\"影视轮播\",寻秦记-穿越剧经典","https://lunbo.freetv.top/yy/1382749900"),
("group-title=\"影视轮播\",天道-9.2高分好剧","https://lunbo.freetv.top/yy/1382735574"),
("group-title=\"影视轮播\",父母爱情","https://lunbo.freetv.top/yy/1354926650"),
("group-title=\"影视轮播\",三国演义94年经典版","https://lunbo.freetv.top/yy/1354936241"),
("group-title=\"影视轮播\",少年包青天第三部","https://lunbo.freetv.top/yy/1382736814"),
("group-title=\"影视轮播\",我爱我家","https://lunbo.freetv.top/yy/1382735557"),
("group-title=\"影视轮播\",易中天品三国","https://lunbo.freetv.top/yy/1354931498"),
("group-title=\"影视轮播\",炊事班的故事II","https://lunbo.freetv.top/yy/1382736885"),
("group-title=\"影视轮播\",士兵突击","https://lunbo.freetv.top/yy/1382828766"),
("group-title=\"影视轮播\",法证先锋Ⅱ","https://lunbo.freetv.top/yy/1354888736"),
("group-title=\"影视轮播\",情满四合院","https://lunbo.freetv.top/yy/1382736848"),
("group-title=\"影视轮播\",魔幻手机","https://lunbo.freetv.top/yy/1382735544"),
("group-title=\"影视轮播\",伪装者","https://lunbo.freetv.top/yy/1354936244"),
("group-title=\"影视轮播\",大明王朝","https://lunbo.freetv.top/yy/1382736879"),
("group-title=\"影视轮播\",炊事班的故事","https://lunbo.freetv.top/yy/1382749901"),
("group-title=\"影视轮播\",金婚","https://lunbo.freetv.top/yy/1382736832"),
("group-title=\"影视轮播\",无敌县令","https://lunbo.freetv.top/yy/1354932390"),
("group-title=\"影视轮播\",黑冰","https://lunbo.freetv.top/yy/1354932427"),
("group-title=\"影视轮播\",大汉天子S1","https://lunbo.freetv.top/yy/1382749902"),
("group-title=\"影视轮播\",大汉天子S2","https://lunbo.freetv.top/yy/1382736807"),
("group-title=\"影视轮播\",大汉天子S3","https://lunbo.freetv.top/yy/1382736810"),
("group-title=\"影视轮播\",天下第一","https://lunbo.freetv.top/yy/1382736838"),
("group-title=\"影视轮播\",百家讲坛――之明太祖朱元璋","https://lunbo.freetv.top/yy/1354936149"),
("group-title=\"影视轮播\",忠烈杨家将","https://lunbo.freetv.top/yy/1382749909"),
("group-title=\"影视轮播\",仙剑奇侠传","https://lunbo.freetv.top/yy/1382749903"),
("group-title=\"影视轮播\",大时代","https://lunbo.freetv.top/yy/1354930891"),
("group-title=\"影视轮播\",聊斋志异S1","https://lunbo.freetv.top/yy/1382736975"),
("group-title=\"影视轮播\",法证先锋Ⅲ","https://lunbo.freetv.top/yy/1382736802"),
("group-title=\"影视轮播\",大汉贤后卫子夫","https://lunbo.freetv.top/yy/1382735569")
]

try:
    # 打开目标网页
    url = "http://m.snrtv.com/snrtv_tv/index.html"  # 替换为实际的直播页面URL
    driver.get(url)

    # 等待页面完全加载
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, 'videoBox'))  # 确保视频盒子加载完毕
    )

    # 获取默认直播源
    video_element = driver.find_element(By.ID, 'videoBox')
    default_live_url = video_element.get_attribute('src')
    live_sources.append(("陕西卫视", default_live_url))  # 使用默认频道名称
    print(f"找到默认直播源: {default_live_url}")

    # 获取页面的尺寸信息
    window_size = driver.execute_script("return { width: window.innerWidth, height: window.innerHeight };")
    screen_width = window_size['width']
    screen_height = window_size['height']

    # 每次滑动的起点和纵向位置
    start_x = screen_width * 3 / 4  # 从屏幕中间靠右 1/4 处开始
    y_position = screen_height / 3  # 纵向位置位于屏幕上三分之一
    move_distance = -100  # 设置每次滑动的距离

    # 通过鼠标拖动事件滑动切换频道
    action = ActionChains(driver)

    channel_count = 8  # 假设有8个频道
    for i in range(1, channel_count + 1):
        move = move_distance  
        print(f"滑动到频道 {i}")
        try:
            # 执行滑动操作
            action.move_by_offset(start_x, y_position).click_and_hold().move_by_offset(move, 0).release().perform()

            time.sleep(3)  # 等待页面完全加载

            # 获取当前直播源
            video_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'videoBox'))
            )
            current_live_url = video_element.get_attribute('src')

            # 获取频道 ID
            channel_id = i  # 使用整数作为频道 ID

            # 不将第五次和第八次的直播源加入到live_sources列表中
            if current_live_url != default_live_url:
                if i not in [7]:  # 第7次不加入
                    live_sources.append((channel_id, current_live_url))
                print(f"{channel_id}: 当前直播源: {current_live_url}")
                default_live_url = current_live_url  # 更新默认直播源为当前直播源
            else:
                print(f"{channel_id}: 未检测到新直播源，当前仍为默认频道")

        except Exception as e:
            print(f"滑动操作失败: {e}")

        # 在每次滑动后，重置ActionChains以防止链条问题
        action.reset_actions()

except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭浏览器
    driver.quit()

# 生成 .m3u 文件
with open('ShaanxiTV.m3u', 'w', encoding='utf-8') as f:
    f.write('#EXTM3U\n')
    
    for channel_id, source in live_sources:
        channel_name = channel_ys.get(channel_id, "陕西卫视")  # 获取频道名称
        # 写入频道信息，-1 表示持续时间未知
        f.write(f'#EXTINF:-1, {channel_name}\n')
        f.write(f'{source}\n')

# 后写入额外的直播源
    for channel_name, source in additional_sources:
        f.write(f'#EXTINF:-1, {channel_name}\n')
        f.write(f'{source}\n')

print("已生成 ShaanxiTV.m3u 文件")
