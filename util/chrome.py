from selenium import webdriver
from conf.config import Const


def get_chrome():
    option = webdriver.ChromeOptions()
    # option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    prefs = {"download.default_directory": Const.DOWNLOAD_PATH, "download.prompt_for_download": False, }
    option.add_experimental_option("prefs", prefs)
    # option.add_argument("--headless")
    return webdriver.Chrome(
        chrome_options=option)
    # return webdriver.Chrome()
