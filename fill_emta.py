import time

import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


#  do before div_for_emta for csv file

sleep_time = 1
long_sleep_time = 20


def set_driver(driver_path, url_path):
    # Set up the Chrome driver (you can also use Firefox, Safari, etc.)
    # Set the path to the ChromeDriver executable

    # Create a Service object for the ChromeDriver
    service = Service(executable_path=driver_path)
    # Create a new Chrome browser instance using the Service object
    driver = webdriver.Chrome(service=service)

    # Navigate to the webpage that contains the element
    driver.get(url_path)
    time.sleep(sleep_time)
    return driver


def authorization(driver, isikukood):
    # login
    smart_id_tab = driver.find_element(By.XPATH, '//*[@id="nav-item-tara_smartid"]/a')
    smart_id_tab.click()
    time.sleep(sleep_time)
    login_button = driver.find_element(By.XPATH, '//*[@id="tab-tara_smartid"]/form/div/button')
    login_button.click()
    time.sleep(sleep_time)
    isikukood_field = driver.find_element(By.ID, 'sid-personal-code')
    isikukood_field.send_keys(isikukood)
    isikukood_button = driver.find_element(By.XPATH,
                            "//button[@class='c-btn c-btn--primary' and contains(text(),'Продолжить')]")
    isikukood_button.click()
    time.sleep(long_sleep_time)


def open_decl(driver):
    find_decl = driver.find_element(By.XPATH,
        "/html/body/ng-component/ng-component/div/div[2]/principal-client/div/div/div/div[2]/div/ul/li/a")
    find_decl.click()
    time.sleep(sleep_time)


def findLine88(wait):
    # Find the 8.8 element by its text content
    row_decl = wait.until(EC.presence_of_element_located((By.XPATH,
        '//h4[contains(text(), "8.8 Доход, полученный в иностранном государстве, не облагаемый налогом в Эстонии")]')))
    # Interact with the row_decl element once it appears
    row_decl.click()


def add_new_row(driver):
    # Find the button element by its id and click on it "Новая строка"
    button_new = driver.find_element(By.ID, 'foreign-other-income-new-row-button')
    button_new.click()
    time.sleep(sleep_time)


def fill_reg_nr(driver, our_reg_nr):
    reg_nr = driver.find_element(By.ID, 'add_foreignOtherIncome_code')
    reg_nr.send_keys(our_reg_nr)
    reg_nr.send_keys(Keys.TAB)


def fill_company(driver, our_company):
    name = driver.find_element(By.ID, 'add_foreignOtherIncome_name')
    name.send_keys(our_company)


def fill_country(driver, our_country):
    country = driver.find_element(By.ID, 'add_foreignOtherIncome_country')
    country.click()
    country_input = driver.find_element(By.ID, 'select-user-input-element')
    country_input.send_keys(our_country)
    country_select = driver.find_element(By.ID, 'add_foreignOtherIncome_country-0')
    country_select.click()


def fill_type(driver):
    type_income = driver.find_element(By.ID, 'add_foreignOtherIncome_incomeType')
    type_income.click()
    # дивиденды, полученные от финансовых активов, приобретенных на денежные средства
    # находящихся на инвестиционном счете,
    # с которых в иностранном государстве уплачен или удержан подоходный налог
    type_income_select = driver.find_element(By.ID, 'add_foreignOtherIncome_incomeType-5')
    type_income_select.click()


def fill_currency(driver, our_currency):
    currency = driver.find_element(By.ID, 'add_foreignOtherIncome_currency')
    currency.click()
    currency_input = driver.find_element(By.ID, 'select-user-input-element')
    currency_input.send_keys(our_currency)
    currency_select = driver.find_element(By.ID, 'add_foreignOtherIncome_currency-0')
    currency_select.click()


def fill_amount(driver, our_amount):
    amount = driver.find_element(By.ID, 'add_foreignOtherIncome_income')
    amount.send_keys(our_amount)


def fill_date_payout(driver, our_date_p):
    date_payout = driver.find_element(By.ID, 'add_foreignOtherIncome_payoutDate')
    date_payout.send_keys(our_date_p)
    date_payout.send_keys(Keys.TAB)


def fill_tax(driver, our_tax):
    tax = driver.find_element(By.ID, 'add_foreignOtherIncome_incomeTax')
    tax.send_keys(our_tax)


def fill_date_tax(driver, our_date_tax):
    date_tax = driver.find_element(By.ID, 'add_foreignOtherIncome_taxDate')
    date_tax.send_keys(our_date_tax)
    date_tax.send_keys(Keys.TAB)


def save_row(driver):
    time.sleep(sleep_time)
    button_save = driver.find_element(By.ID, 'add-foreign-other-income-save-button')
    button_save.click()


def parse_csv_and_fill(driver, file_csv):
    df = pd.read_csv(file_csv)
    # loop over the rows of the DataFrame
    for index, row in df.iterrows():
        our_reg_nr = row['reg_nr']
        our_company = row['company']
        our_country = row['country']
        our_currency = row['currency']
        our_amount = row['dividend']
        our_date_p = row['date_']
        our_tax = row['tulumaks']
        our_date_tax = row['date_']
        fill_data(driver, our_reg_nr, our_company, our_country, our_currency, our_amount,
              our_date_p, our_tax, our_date_tax)


def fill_data(driver, our_reg_nr, our_company, our_country, our_currency, our_amount,
              our_date_p, our_tax, our_date_tax):
    add_new_row(driver)
    time.sleep(sleep_time)

    fill_reg_nr(driver, our_reg_nr)
    time.sleep(sleep_time)

    fill_company(driver, our_company)
    time.sleep(sleep_time)

    fill_country(driver, our_country)
    time.sleep(sleep_time)

    fill_type(driver)
    time.sleep(sleep_time)

    fill_currency(driver, our_currency)
    time.sleep(sleep_time)

    fill_amount(driver, our_amount)
    time.sleep(sleep_time)

    fill_date_payout(driver, our_date_p)
    time.sleep(sleep_time)

    fill_tax(driver, our_tax)
    time.sleep(sleep_time)

    fill_date_tax(driver, our_date_tax)
    time.sleep(sleep_time)

    save_row(driver)


def main():
    # isikukood = "47901050281"
    isikukood = '37708280352'
    driver_path = '/Users/docha/Downloads/chromedriver_mac64/chromedriver'
    url_path = 'https://tuludeklaratsioon.emta.ee/fidek22-client/declaration'
    driver = set_driver(driver_path, url_path)
    wait = WebDriverWait(driver, 30)

    authorization(driver, isikukood)

    try:
        open_decl(driver)
    except Exception as e:
        print(f'Error: {e}. Skipping open_decl')

    findLine88(wait)

    file_csv = '/Users/docha/PycharmProjects/akcii_bank_parsing/div.csv'
    parse_csv_and_fill(driver, file_csv)

    time.sleep(long_sleep_time)

    # Close the browser window when done
    driver.quit()


if __name__ == "__main__":
    main()
