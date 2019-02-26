from selenium import webdriver
from conf.config import Const
import selenium.common.exceptions
import time
from util.logger import Logger


class Chrome():
    def __init__(self):
        self.chrome = self.get_chrome()

    def get_chrome(self):
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        option.add_argument('--no-sandbox')
        option.add_experimental_option("prefs", {"download.default_directory": Const.DOWNLOAD_PATH,
                                                 "download.prompt_for_download": False, })
        driver = webdriver.Chrome(
            chrome_options=option)
        self.enable_download_in_headless_chrome(driver, Const.DOWNLOAD_PATH)
        return driver

    @classmethod
    def enable_download_in_headless_chrome(self, driver, download_dir):
        # add missing support for chrome "send_command"  to selenium webdriver
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
        command_result = driver.execute("send_command", params)

    def find_class(self, class_name, count=1):
        result = ''
        try:
            result = self.chrome.find_element_by_class_name(class_name)
        except selenium.common.exceptions.NoSuchElementException:
            Logger.warn("未找到class[%s]，刷新页面%d次" % (class_name, count))
            count += 1
            if count < 10:
                self.chrome.refresh()
                time.sleep(5)
                return self.find_class(class_name, count)
            else:
                Logger.error("连续刷新页面%d次未找到class[%s]" % (count, class_name))
                exit()
        return result

    def get(self, url):
        Logger.info("请求url:%s" % url)
        self.chrome.get(url)

    def quit(self):
        self.chrome.quit()

    def current_url(self):
        return self.chrome.current_url
