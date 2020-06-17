from selenium import webdriver
from selenium import common
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
import json

chrome_options = Options()
chrome_options.add_argument("start-maximized")
driver = webdriver.Chrome(options=chrome_options)

driver.implicitly_wait(5)
driver.get('https://www.mvideo.ru/')

action = ActionChains(driver)

while True:
    try:
        elem = driver.find_element_by_xpath('//div[contains(text(), "Хиты продаж")]/ancestor::'
                                            'div[@class="section"]//a[@class="next-btn sel-hits-button-next"]')
        action.move_to_element(elem).click().perform()
    except common.exceptions.NoSuchElementException:
        break

goods = driver.find_elements_by_xpath('//div[contains(text(), "Хиты продаж")]/ancestor::'
                                      'div[@class="section"]//li[@class="gallery-list-item height-ready"]')

goods_list = [json.loads(good.find_element_by_xpath('.//h4/a').get_attribute('data-product-info')) for good in goods]

# складываем в БД
db = MongoClient('localhost', 27017)['mvidio']
collection = db.top_sales
collection.insert_many(goods_list)

driver.quit()
