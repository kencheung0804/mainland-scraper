import re
from datetime import datetime, date
from itertools import combinations
from typing import Optional, Union

from selenium.webdriver.chrome.webdriver import WebDriver

from constants.index import Number
from utils.check import check_is_residential, check_dates_within
import uuid
import time


def extract_date_and_img_from_page(driver: WebDriver, house_type: str) -> tuple[date, str]:
    driver.implicitly_wait(30)
    if check_is_residential(house_type):
        raw_post_date = \
            driver.find_element_by_css_selector('div.gray9.fybh-zf > span:nth-child(2)').text.split(' ')[-1].split("：")[
                -1]
    else:
        raw_post_date = driver.find_element_by_css_selector(
            f"body > div.wid1200.clearfix > div.w1200.clearfix > div.zf_new_left.floatl > div.content-item.fydes-item "
            f"> div.cont.clearfix > div:last-child > span.rcont").text

    try:
        post_date = datetime.strptime(raw_post_date, '%Y-%m-%d').date()
    except:
        post_date = datetime.strptime(raw_post_date, '%Y/%m/%d').date()

    driver.set_window_size(1920, 1200)
    time.sleep(0.5)
    raw_img = driver.get_screenshot_as_base64()
    return post_date, raw_img


def find_right_combination(driver: WebDriver, house_type: str, min_limit: Number, max_limit: Number, input_date: date,
                           min_limit_for_each: Optional[Number] = None, max_limit_for_each: Optional[Number] = None) -> \
        tuple[Union[list[Number], None], Union[list[str], None]]:
    # driver is already on the main page
    has_next = True

    passed_house_list = []

    while has_next:
        # find all the links and prices -> dict
        driver.implicitly_wait(30)
        if check_is_residential(house_type):
            prices_in_page = driver.find_elements_by_css_selector("span.price")
            meter_in_page = driver.find_elements_by_css_selector('dd.info.rel > p:nth-child(2)')
        else:
            meter_in_page = driver.find_elements_by_css_selector('p.tel_shop')
            if house_type == 'commercial':
                prices_in_page = driver.find_elements_by_css_selector("dd.price_right > span.red > b")
            else:
                prices_in_page = driver.find_elements_by_css_selector("dd.price_right > span:nth-child(2)")

        for i in range(len(prices_in_page)):
            p = int(float(prices_in_page[i].text.split('元')[0]))
            raw_meter = meter_in_page[i].text.split('㎡')[0]
            m = int(float(re.findall('\d+', raw_meter)[-1]))
            price = p / m
            if max_limit_for_each > price > min_limit_for_each:
                try:
                    driver.implicitly_wait(30)
                    house_link = driver.find_element_by_css_selector(
                        f"div.{'houseList' if check_is_residential(house_type) else 'shop_list'} > dl:nth-child({i + 1}) > dt > a")
                    house_link.click()
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.implicitly_wait(30)
                    post_date, raw_img = extract_date_and_img_from_page(driver, house_type)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    passed_house_list.append({'price': price, 'raw_img': raw_img, 'post_date': post_date})

                    if len(passed_house_list) >= 3:
                        combinations_generator = combinations(passed_house_list, 3)

                        for comb in combinations_generator:
                            # match price
                            price_list = [each.get('price') for each in comb]
                            avg_price = (sum(price_list) * .9) / len(price_list)
                            if (avg_price < max_limit) and (avg_price > min_limit):
                                image_list = []
                                for each in comb:
                                    if not check_dates_within(input_date, each['post_date']):
                                        break
                                    else:
                                        image_list.append(each['raw_img'])

                                if len(image_list) == 3:
                                    return price_list, image_list
                except:
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                        driver.switch_to.window(driver.window_handles[-1])

        # generate all combinations

        # # generate all combinations
        # combinations_generator = combinations(passed_house_list, 3)
        #
        # for comb in combinations_generator:
        #     # match price
        #     price_list = [each.get('price') for each in comb]
        #     avg_price = (sum(price_list) * .9) / len(price_list)
        #     if (avg_price < max_limit) and (avg_price > min_limit):
        #         # if found matched price, validate the date of all properties
        #         image_list = []
        #         for each in comb:
        #             idx_in_page = each.get('index')
        #             driver.implicitly_wait(30)
        #             house_link = driver.find_element_by_css_selector(
        #                 f"div.{'houseList' if check_is_residential(house_type) else 'shop_list'} > dl:nth-child({idx_in_page}) > dt > a")
        #             house_link.click()
        #             driver.implicitly_wait(30)
        #             driver.switch_to.window(driver.window_handles[-1])
        #             driver.implicitly_wait(30)
        #             post_date, raw_img = extract_date_and_img_from_page(driver, house_type)
        #             driver.close()
        #             driver.switch_to.window(driver.window_handles[0])
        #             if not check_dates_within(input_date, post_date):
        #                 break
        #             else:
        #                 image_list.append(raw_img)
        #
        #         if len(image_list) == 3:
        #             return price_list, image_list

        driver.implicitly_wait(30)
        next_page_list = driver.find_elements_by_xpath("//a[contains( text( ), '下一页')]")

        if len(next_page_list) > 0:
            next_page_list[0].click()
        else:
            has_next = False
    return None, None
