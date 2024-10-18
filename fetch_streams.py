import requests

# XHR 请求的 URL，这里需要根据实际情况修改
url = "live.snrtv.com"  # 假设的 API 端点

# 发送请求
try:
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功

    # 解析 JSON 数据
    data = response.json()

    # 提取直播源
    streams = data.get('streams', [])
    for stream in streams:
        print(f"直播源: {stream['url']}")  # 假设每个流都有一个 'url' 字段

except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
except ValueError as e:
    print(f"解析失败: {e}")
