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
    1: "新闻资讯",
    2: "都市青春",
    3: "银龄",
    4: "秦腔",
    5: "体育休闲",
    7: "移动",
    8: "陕西卫视"
}

# 添加的直播源
additional_sources = [

    ("大爱频道1","https://pulltv1.wanfudaluye.com/live/tv1.m3u8"),
    ("大爱频道2","https://pulltv2.wanfudaluye.com/live/tv2.m3u8"),
    ("西安综合","https://xatv-yt.xiancity.cn/live/1/index.m3u8"),
    ("西安都市","https://xatv-yt.xiancity.cn/live/2/index.m3u8"),
    ("西安商务资讯","https://xatv-yt.xiancity.cn/live/3/index.m3u8"),
    ("西安影视","https://xatv-yt.xiancity.cn/live/4/index.m3u8"),
    ("西安丝路","https://xatv-yt.xiancity.cn/live/5/index.m3u8"),
  #  ("宝鸡一套","http://8.138.90.107/tv/proxy/sx1/zb.php?id=239.110.205.26:9224"),
  #  ("宝鸡二套","http://8.138.90.107/tv/proxy/sx1/zb.php?id=239.110.205.27:9232"),
  #  ("西部影视","http://8.138.90.107/tv/proxy/sx1/zb.php?id=239.110.205.128:7764"),
   # ("陕西影视","http://8.138.90.107/tv/proxy/sx1/zb.php?id=239.110.205.131:7752"),
 #   ("陕视融媒体","http://8.138.90.107/tv/proxy/sx1/zb.php?id=239.110.205.52:9934"),
    ("凤凰中文","http://aktv.top/AKTV/live/aktv/null-3/AKTV.m3u8"),
    ("凤凰资讯","http://aktv.top/AKTV/live/aktv/null-4/AKTV.m3u8"),
    ("香港卫视", "http://zhibo.hkstv.tv/livestream/mutfysrq/playlist.m3u8"),
    ("龍華电影", "http://aktv.top/AKTV/live/aktv/null-23/AKTV.m3u8"),
    ("翡翠台","http://aktv.top/AKTV/live/aktv/null/AKTV.m3u8"),
    ("中天亚洲","http://aktv.top/AKTV/live/aktv/null-12/AKTV.m3u8"),
    ("中天新闻","http://aktv.top/AKTV/live/aktv/null-8/AKTV.m3u8"),
    ("宰相刘罗锅","http://live.nctv.top/6688/yy.php?id=1382745191"),
("神探狄仁杰2","http://live.nctv.top/6688/yy.php?id=1382828767"),
("举起手来-惊险抗日","http://live.nctv.top/6688/yy.php?id=1382736877"),
("神探狄仁杰1","http://live.nctv.top/6688/yy.php?id=1354930934"),
("笑傲江湖","http://live.nctv.top/6688/yy.php?id=1354930909"),
("康熙王朝","http://live.nctv.top/6688/yy.php?id=1382736818"),
("西游记后传","http://live.nctv.top/6688/yy.php?id=1382736846"),
("寻秦记-穿越剧经典","http://live.nctv.top/6688/yy.php?id=1382749900"),
("天道-9.2高分好剧","http://live.nctv.top/6688/yy.php?id=1382735574"),
("父母爱情","http://live.nctv.top/6688/yy.php?id=1354926650"),
("三国演义94年经典版","http://live.nctv.top/6688/yy.php?id=1354936241"),
("少年包青天第三部","http://live.nctv.top/6688/yy.php?id=1382736814"),
("我爱我家","http://live.nctv.top/6688/yy.php?id=1382735557"),
("易中天品三国","http://live.nctv.top/6688/yy.php?id=1354931498"),
("炊事班的故事II","http://live.nctv.top/6688/yy.php?id=1382736885"),
("士兵突击","http://live.nctv.top/6688/yy.php?id=1382828766"),
("法证先锋Ⅱ","http://live.nctv.top/6688/yy.php?id=1354888736"),
("情满四合院","http://live.nctv.top/6688/yy.php?id=1382736848"),
("魔幻手机","http://live.nctv.top/6688/yy.php?id=1382735544"),
("伪装者","http://live.nctv.top/6688/yy.php?id=1354936244"),
("热门喜剧","http://live.nctv.top/6688/yy.php?id=1354931495"),
("大明王朝","http://live.nctv.top/6688/yy.php?id=1382736879"),
("炊事班的故事","http://live.nctv.top/6688/yy.php?id=1382749901"),
("金婚","http://live.nctv.top/6688/yy.php?id=1382736832"),
("超炫科幻大片","http://live.nctv.top/6688/yy.php?id=1382736840"),
("无敌县令","http://live.nctv.top/6688/yy.php?id=1354932390"),
("黑冰","http://live.nctv.top/6688/yy.php?id=1354932427"),
("大唐双龙传","http://live.nctv.top/6688/yy.php?id=1354930979"),
("大汉天子S3","http://live.nctv.top/6688/yy.php?id=1382736810"),
("天下第一","http://live.nctv.top/6688/yy.php?id=1382736838"),
("漫威超级英雄系列","http://live.nctv.top/6688/yy.php?id=1354932402"),
("百家讲坛――之明太祖朱元璋","http://live.nctv.top/6688/yy.php?id=1354936149"),
("热血动作片合集","http://live.nctv.top/6688/yy.php?id=1382735627"),
("忠烈杨家将","http://live.nctv.top/6688/yy.php?id=1382749909"),
("天龙八部","http://live.nctv.top/6688/yy.php?id=1382749944"),
("仙剑奇侠传-神仙姐姐驾到","http://live.nctv.top/6688/yy.php?id=1382749903"),
("大时代","http://live.nctv.top/6688/yy.php?id=1354930891"),
("聊斋志异S1","http://live.nctv.top/6688/yy.php?id=1382736975"),
("法证先锋Ⅲ","http://live.nctv.top/6688/yy.php?id=1382736802"),
("末日系列-外国电影合集","http://live.nctv.top/6688/yy.php?id=1354889019"),
("大汉贤后卫子夫","http://live.nctv.top/6688/yy.php?id=1382735569"),
("大汉天子S2","http://live.nctv.top/6688/yy.php?id=1382736807")
]

try:
    # 打开目标网页
    url = "http://m.snrtv.com/snrtv_tv/index.html"  # 替换为实际的直播页面URL
    driver.get(url)

    # 等待页面完全加载
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, 'videoBox'))  # 确保视频盒子加载完毕
    )

    # 获取默认直播源
    video_element = driver.find_element(By.ID, 'videoBox')
    default_live_url = video_element.get_attribute('src')
    live_sources.append(("农林卫视", default_live_url))  # 使用默认频道名称
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
                if i not in [6]:  # 第6次不加入
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
