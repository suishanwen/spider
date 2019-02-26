from selenium import webdriver
from conf.config import Const


def get_chrome():
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_experimental_option("prefs", {"download.default_directory": Const.DOWNLOAD_PATH,
                                             "download.prompt_for_download": False, })
    driver = webdriver.Chrome(
        chrome_options=option)
    enable_download_in_headless_chrome(driver, Const.DOWNLOAD_PATH)
    return driver


def enable_download_in_headless_chrome(driver, download_dir):
    # add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)
