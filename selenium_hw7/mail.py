from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from hashlib import sha1
from pymongo import MongoClient
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome()

driver.get('https://account.mail.ru/')
driver.implicitly_wait(5)

elem = driver.find_element_by_xpath('//input[@name="username"]')
elem.send_keys('study.ai_172')
elem.send_keys(Keys.RETURN)

driver.implicitly_wait(5)
elem = driver.find_element_by_xpath('//input[@name="password"]')
elem.send_keys('NextPassword172')
elem.send_keys(Keys.RETURN)

mails_ref = []

# сначала собираем все ссылки на письма
while True:

    driver.implicitly_wait(5)
    elems = driver.find_elements_by_xpath('//div[@class="dataset__items"]/a')

    if elems[-1].get_attribute('href') is None:
        break

    for elem in elems:
        if elem.get_attribute('href') not in mails_ref:
            mails_ref.append(elem.get_attribute('href'))

    actions = ActionChains(driver)
    actions.move_to_element(elems[-1]).perform()

# проходим по ссылкам на письма и собираем информацию из каждого письма
parsed_mails = []
for link in mails_ref:
    driver.get(link)
    driver.implicitly_wait(5)
    parsed_mails.append({'from': driver.find_element_by_xpath('//div[@class="letter__author"]/span').get_attribute('title'),
                         'date': driver.find_element_by_xpath('//div[@class="letter__date"]').text,
                         'title': driver.find_element_by_xpath('//h2[@class="thread__subject thread__subject_pony-mode"]').text,
                         'text': driver.find_element_by_xpath('//div[@class="letter__body"]').text})

# Добавляем данные в БД
db = MongoClient('localhost', 27017)['mails']
collection = db.mails_study_ai_172
i = 0
for elem in parsed_mails:
    elem['_id'] = sha1(str(elem).encode('utf-8')).hexdigest()
    if not collection.find({'_id': elem['_id']}).count():
        collection.insert_one(elem)
        i += 1
print(i, 'are inserted in database')

driver.quit()
