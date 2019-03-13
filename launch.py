import processor
import time
import threading

from util import mysql
from util.logger import Logger
from model.Spiders import Spiders
from model.Channel import Channel

if __name__ == '__main__':
    while True:
        Logger.info("主线程活动，启动抓取程序...")
        active_thread = threading.activeCount()
        # active_thread 程序默认为4
        if active_thread > 4:
            Logger.info("还有线程未抓取完成，继续休眠1小时...")
            time.sleep(3600)
            continue
        channels = []
        try:
            channels = mysql.get_channels()
        except Exception as e:
            Logger.error("查询channels失败,%s", str(e))
        for spider_name in Spiders:
            spider = Spiders.get(spider_name)
            spider.channels = []
            for channel in channels:
                _channel = Channel()
                _channel.from_dict(channel)
                if spider_name == _channel.spider:
                    spider.channels.append(_channel)
            if len(spider.channels) > 0:
                threading.Thread(target=processor.__main__, args=(spider,)).start()
        Logger.info("所有channel启动完成，休眠12小时...")
        time.sleep(3600 * 12)
