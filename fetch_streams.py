import requests
from bs4 import BeautifulSoup

# 设置目标URL
url = "http://m.snrtv.com/index.php?m=playlist_tv&channel=nl"  # 假设这个是陕西广播电视台的直播页面URL

# 获取网页内容
response = requests.get(url)
if response.status_code == 200:
    page_content = response.text
else:
    print(f"无法访问页面, 状态码: {response.status_code}")
    exit()

# 解析网页
soup = BeautifulSoup(page_content, 'html.parser')

# 假设直播源链接在页面的某个标签里，比如 <video> 或 <iframe> 等
live_source = soup.find('video')  # 根据实际情况调整

if live_source:
    live_url = live_source['src']
    print(f"找到直播源: {live_url}")
    
    # 写入.m3u文件
    with open("sxtv_live.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("#EXTINF:-1,陕西广播电视台直播\n")
        f.write(f"{live_url}\n")
    print("m3u文件已生成: sxtv_live.m3u")
else:
    print("未找到直播源")
