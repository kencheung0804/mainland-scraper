import requests
from bs4 import BeautifulSoup
from utils.common import generate_init_headers
from pypinyin import lazy_pinyin
from constants.index import ScrapeDict, ScrapeError, Number
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import Union, Optional
from utils.check import check_is_residential
import logging
from fake_useragent import UserAgent

def scrape_city_link_dict() -> ScrapeDict:
    # get all cities' main page link
    try:
        response = requests.get('https://www.fang.com/SoufunFamily.htm', headers=generate_init_headers())
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_cities = soup.find('div', id='c02').findChildren('a')
        city_link_dict = {}
        for raw_city in raw_cities:
            city_pinyin = ''.join(lazy_pinyin(raw_city.text)).upper()
            city_link_dict[city_pinyin] = raw_city.get('href')
        return city_link_dict
    except Exception:
        error_msg = "Cannot scrape the city list with requests. Please run the program again."
        logging.error(error_msg)
        print(error_msg)
        raise ScrapeError(error_msg)


def init_new_driver(headless_mode: Optional[bool] = False,
                    danger_mode: Optional[bool] = True) -> WebDriver:
    ua = UserAgent()
    options = Options()
    options.add_argument(f'user-agent={ua.chrome}')
    options.add_argument("--log-level=3")

    if headless_mode:
        options.add_argument("--headless")
    caps = DesiredCapabilities().CHROME
    if danger_mode:
        caps["pageLoadStrategy"] = "none"
    else:
        caps["pageLoadStrategy"] = "normal"
    driver = webdriver.Chrome(options=options)

    return driver


def find_link_el_for_house_type(driver: WebDriver, house_type: str) -> Union[WebElement, None]:
    try:
        driver.implicitly_wait(30)
        if check_is_residential(house_type):
            el_list = driver.find_elements_by_xpath("//a[contains( text( ), '租房')]")
            if (len(el_list)) and house_type == 'sa':
                el_list[0].click()
                driver.implicitly_wait(30)
                el_list = driver.find_elements_by_xpath("//a[contains( text( ), '品牌公寓')]")
        if house_type == 'office':
            el_list = driver.find_elements_by_xpath("//a[contains( text( ), '写字楼')]")
        elif house_type == 'commercial':
            el_list = driver.find_elements_by_xpath("//a[contains( text( ), '商铺')]")
            el_list[0].click()
            driver.implicitly_wait(30)
            el_list = driver.find_elements_by_css_selector(
                "div.search_nav > ul.clearfix > li:first-child > a:first-child")
        if len(el_list):
            if house_type == 'sa':
                return el_list[-1]
            elif house_type == 'commercial':
                return el_list[-1]
            else:
                return el_list[0]
        else:
            return None
    except ScrapeError:
        error_msg = f'This is likely due to slow network error. You can try again manually later on this row for {house_type}!'
        logging.error(error_msg)
        print(error_msg)
        raise ScrapeError(error_msg)


def choose_params(driver: WebDriver, house_type: str, region_name: str, min_price: Optional[Number] = None,
                  max_price: Optional[Number] = None):
    try:
        driver.implicitly_wait(30)
        reg_els = driver.find_elements_by_css_selector('#rentid_D04_01 > dd > a' if check_is_residential(
            house_type) else 'li:nth-child(1) > ul.clearfix.choose_screen.floatl > li > a')
        reg_els_num = len(reg_els)

        region_found = False
        reg_index = 0

        while (not region_found) and (reg_index < reg_els_num):
            reg = reg_els[reg_index]
            if reg.text != "不限":
                reg_pinyin = ''.join(lazy_pinyin(reg.text)).upper()
                if reg_pinyin == region_name.upper():
                    region_found = True
                    reg.click()
            reg_index += 1
        driver.implicitly_wait(30)

        if house_type == 'office':
            determine_date_text = driver.find_element_by_css_selector(
                "li > ul.clearfix.choose_screen.floatl.choose_label > li:first-child > label > a").text
            if '天' in determine_date_text:
                min_price /= 30
                max_price /= 30

            min_input_element = driver.find_element_by_id(
                "minprice" if check_is_residential(house_type) else "cminPrice")
            min_input_element.send_keys(f'{int(min_price)}')

            max_input_element = driver.find_element_by_id(
                "maxprice" if check_is_residential(house_type) else "cmaxPrice")
            max_input_element.send_keys(f'{int(max_price)}')

            driver.implicitly_wait(30)
            driver.find_element_by_id("pricBtn" if check_is_residential(house_type) else "pConfirmButton").click()


    except ScrapeError:
        error_msg = f'This is likely due to slow network error. You can try again manually later on this row for {house_type}!'
        logging.error(error_msg)
        print(error_msg)
        raise ScrapeError(error_msg)
