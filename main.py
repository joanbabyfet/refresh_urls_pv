import multiprocessing
import random
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent

# 全局统计刷了多少访问量总数
count = 0

# 获取可用代理ip地址列表并返回
def get_proxy():
    proxy_ips = []

    with open('proxy.txt', 'r') as f:
        for item in f:
            proxy_ips.append(item.strip('\n'))
    return proxy_ips

# 初始化浏览器
def init_browser(proxy, ua, windowsize):
    proxy_https = f'--proxy-server=http://{proxy}'
    ws = windowsize.split('x') # 字符串转列表

    options = webdriver.ChromeOptions()
    options.add_argument(proxy_https) # 通过该台代理服务器ip访问
    options.add_argument(ua)  # 指定用户代理
    options.add_argument('--headless')  # 走无头模式
    options.add_argument('--disable-gpu') # 禁用gpu加速, 添加启动参数
    options.add_experimental_option('detach', True)  # 不自动关闭浏览器, 添加实验性质的设置参数
    options.add_experimental_option('prefs', { 
        "profile.default_content_setting_values.notifications": 2 # 禁用浏览器弹窗
    })

    #browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)
    browser = webdriver.Chrome(options = options) # 实例化
    browser.set_window_size(int(ws[0]), int(ws[1])) # 设置窗口大小
    browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", { # 解决 navigator.webdriver=true
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
    """
    })
    browser.set_page_load_timeout(15) # 页面最长加载时间, 超过15秒退出
    return browser

# 请求url
def req_url(url, proxy, ua, windowsize):
    try:
        browser = init_browser(proxy, ua, windowsize)
        browser.get(url) # 开启网页
        
        # delay_seconds = [3, 4, 5]  # 等待秒数
        # delay = random.choice(delay_seconds)  # 随机选取秒数
        time.sleep(3) # 等待n秒页面加载完成
        print(proxy + '\n' + url + '\n' + ua + '\n' + windowsize + '\n' + f'刷新成功 {url}')
    except Exception as e:
        print(proxy + '\n' + url + '\n' + ua + '\n' + windowsize + '\n' + f'刷新失败 {e}')
    browser.close()

def main():
    global count
    url_list        = []
    ua_list         = []
    windowsize_list = []
    with open('urls.txt', 'r') as f:
        for item in f:
            url_list.append(item.strip('\n'))  # 干掉字符串头尾指定字符\n
    with open('ua.txt', 'r') as f:
        for item in f:
            ua_list.append(item.strip('\n'))
    with open('windowsize.txt', 'r') as f:
        for item in f:
            windowsize_list.append(item.strip('\n'))

    while True:
        proxys = get_proxy()
        if proxys:
            # 多进程池, processes = 进程数
            pool = multiprocessing.Pool(processes = len(proxys))
            for proxy in proxys: # 轮询访问目标地址
                for url in url_list:
                    # user_agent = UserAgent()
                    # ua = user_agent.random # 这里提供另1方案, 随机生成
                    ua = f'--user-agent={random.sample(ua_list, 1)[0]}'
                    windowsize = random.sample(windowsize_list, 1)[0]
                    pool.apply_async(req_url, (url, proxy, ua, windowsize)) # 走异步
                    count = count + 1
            pool.close() # 没有任务需要加到队列里
            pool.join() # worker开始运行
        print('当前已刷新浏览量总数:' + str(count))

if __name__ == '__main__': # 主入口
    main()