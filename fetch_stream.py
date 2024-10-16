
import requests
from bs4 import BeautifulSoup

def get_live_url():
    # 替换为陕西广播电视台的直播页面URL
    url = "http://live.snrtv.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 发送请求并获取响应
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # 假设直播流地址在 <video> 标签的 src 属性中
        live_url = soup.find('video')['src']  # 具体解析根据页面结构调整
        return live_url
    else:
        print("Failed to retrieve the page")
        return None

if __name__ == "__main__":
    live_url = get_live_url()
    if live_url:
        print("Latest live URL:", live_url)
        # 可以将地址保存到文件
        with open("live_url.txt", "w") as file:
            file.write(live_url)
    else:
        print("Could not fetch the live URL")
