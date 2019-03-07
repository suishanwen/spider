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
                processor.__main__(_args, channel["pk_org"], channel["pk_channel"])
            Logger.info("所有channel执行完成，休眠12小时...")
        time.sleep(3600 * 12)
