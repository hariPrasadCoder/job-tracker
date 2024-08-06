# connect python with webdriver-chrome
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
# import pyautogui as pag
from time import sleep
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from selenium.common.exceptions import NoSuchElementException 
from webdriver_manager.chrome import ChromeDriverManager   
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def login_linkedin(useremail, userpassword):
    service = Service("src//chromedriver")
    options = webdriver.ChromeOptions()
    # options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(service=service, options=options)
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service)

    # s=Service('chromedriver')
    # driver = webdriver.Chrome(service=s)
    url = "http://linkedin.com/login"

            # path to driver web driver		
    driver.get(url)

    sleep(2)


    # Getting the login element
    username = driver.find_element(By.ID,"username")

    # Sending the keys for username	
    username.send_keys(useremail)

    sleep(2)

    # Getting the password element								
    password = driver.find_element(By.ID,"password")

    # Sending the keys for password
    password.send_keys(userpassword)

    sleep(2)

    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    


    sleep(2)

    return driver


def find_people(company_url, driver):

    driver.get(company_url)

    sleep(5)


    parent_element = driver.find_element(By.CLASS_NAME, 'scaffold-finite-scroll__content')

    linkedin_links = parent_element.find_elements(By.XPATH, '//a[contains(@href, "linkedin.com/in")]')

    user_profiles = []
    for link in linkedin_links:
        href = link.get_attribute('href')
        user_profiles.append(href)

    return user_profiles, driver