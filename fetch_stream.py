
function LiveStreamGrabber(url, rangeStart = 0, rangeEnd = null, timeout = 5000) {
    this.url = http://live.snrtv.com/;  // 直播源地址
    this.rangeStart = rangeStart;  // 字节范围起始
    this.rangeEnd = rangeEnd;  // 字节范围结束
    this.timeout = timeout;  // 超时时间
    this.loader = null;  // 用于存储 XMLHttpRequest 实例
    this.stats = {
        tfirst: 0,
        loaded: 0
    };
}

// 核心抓取方法
LiveStreamGrabber.prototype.loadStream = function() {
    var self = this;
    var loader = this.loader = new XMLHttpRequest();  // 创建 XMLHttpRequest 实例

    // 设置请求状态变更时的回调
    loader.onreadystatechange = function() {
        if (loader.readyState === 4) {  // 请求完成
            if (loader.status >= 200 && loader.status < 300) {  // 如果请求成功
                console.log("Stream Data Loaded:", loader.response);
            } else {  // 如果请求失败
                console.error("Failed to fetch stream:", loader.status, loader.statusText);
            }
        }
    };

    // 设置加载进度回调
    loader.onprogress = function(event) {
        if (self.stats.tfirst === 0) {
            self.stats.tfirst = Date.now();  // 记录首次接收时间
        }
        self.stats.loaded = event.loaded;  // 更新已加载字节数
        console.log(`Loaded ${event.loaded} bytes`);
    };

    // 打开连接
    loader.open("GET", this.url, true);

    // 如果指定了字节范围，则添加 Range 请求头
    if (this.rangeEnd) {
        loader.setRequestHeader("Range", `bytes=${this.rangeStart}-${this.rangeEnd - 1}`);
    }

    // 设置响应类型为 arraybuffer，用于处理二进制流
    loader.responseType = 'arraybuffer';

    // 设置请求超时回调
    this.requestTimeout = window.setTimeout(function() {
        loader.abort();  // 中止请求
        console.error("Request timed out");
    }, this.timeout);

    // 发送请求
    try {
        loader.send();
    } catch (error) {
        console.error("Error while sending request:", error.message);
    }
};

// 使用示例
var streamGrabber = new LiveStreamGrabber('https://example.com/live-stream', 0, null, 10000);
streamGrabber.loadStream();
    if live_url:
        print("Latest live URL:", live_url)
        # 可以将地址保存到文件
        with open("live_url.txt", "w") as file:
            file.write(live_url)
    else:
        print("Could not fetch the live URL")
