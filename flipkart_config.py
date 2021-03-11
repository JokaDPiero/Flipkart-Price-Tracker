from selenium import webdriver
DIRECTORY = 'C:/Users/KIIT/Downloads/Github/Flipkart Price Tracker/reports'

BASE_URL = "https://www.flipkart.com/"


def get_firefox_web_driver(options):
    return webdriver.Firefox(executable_path =r"C:/Users/KIIT/Downloads/Github/Flipkart Price Tracker/geckodriver.exe", firefox_options=options)


def get_web_driver_options():
    return webdriver.FirefoxOptions()


