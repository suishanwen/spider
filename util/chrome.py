from selenium import webdriver


def get_chrome():
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    # return webdriver.Chrome(
    #     chrome_options=option)
    return webdriver.Chrome()
