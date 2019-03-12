import processor
import time
import threading

from util import mysql
from util.logger import Logger
from page.NhcPublic import NhcPublic
from page.NhcSt import NhcSt

if __name__ == '__main__':
    while True:
        Logger.info("主线程活动，启动抓取程序...")
        active_thread = threading.activeCount()
        # active_thread 程序默认为4
        if active_thread > 4:
            time.sleep(3600)
            Logger.info("还有线程未抓取完成，继续休眠1小时...")
        channels = []
        try:
            channels = mysql.get_channels()
        except Exception as e:
            Logger.error("查询channels失败,%s", str(e))
        for channel in channels:
            rule_code = channel["rulecode"]
            _args = ""
            if rule_code == "NhcSt":
                _args = NhcSt()
            elif rule_code == "NhcPublic":
                _args = NhcPublic()
            if _args:
                threading.Thread(target=processor.__main__,
                                 args=(_args, channel["pk_org"], channel["pk_channel"],)).start()
        Logger.info("所有channel启动完成，休眠12小时...")
        time.sleep(3600 * 12)
