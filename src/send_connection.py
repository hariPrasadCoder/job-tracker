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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def check_exists_by_xpath(driver,xpath):

    try:

        driver.find_element(By.XPATH,xpath)

    except NoSuchElementException:

        return False

    return True
def check_exists(element,driver,sel):

    try:

        driver.find_element(element,sel)

    except NoSuchElementException:

        return False

    return True

def send_connection(receiver_linkedin_url, useremail, userpassword, custom_text, driver):
    # service = Service("src//chromedriver")
    # options = webdriver.ChromeOptions()
    # driver = webdriver.Chrome(service=service, options=options)

    # # s=Service('chromedriver')
    # # driver = webdriver.Chrome(service=s)
    # url = "http://linkedin.com/"

    #         # path to driver web driver		
    # driver.get(url)

    # # Getting the login element
    # username = driver.find_element(By.ID,"session_key")

    # # Sending the keys for username	
    # username.send_keys(useremail)

    # # Getting the password element								
    # password = driver.find_element(By.ID,"session_password")

    # # Sending the keys for password
    # password.send_keys(userpassword)

    # actions = ActionChains(driver)
    # actions.send_keys(Keys.ENTER)
    # actions.perform()


    # sleep(2)

    # for i in first_column:
    driver.get(receiver_linkedin_url)

    sleep(5)


    parent_element = driver.find_element(By.CLASS_NAME, 'scaffold-layout__main')


    try:
        # Click on "More actions"
        more_actions_button = parent_element.find_element(By.CSS_SELECTOR, '[aria-label="More actions"]')
        more_actions_button.click()
    except NoSuchElementException:
            pass

    sleep(2)

    # Click on "Invite the person to connect"
    invite_connect_button = parent_element.find_element(By.CSS_SELECTOR, '[aria-label*="Invite"][aria-label*="connect"]')
    invite_connect_button.click()

    sleep(2)


    # Click on "Add a note"
    add_note_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Add a note"]')
    add_note_button.click()

    sleep(2)

    # Type text into the note field
    note_field = driver.find_element(By.ID, "custom-message")
    note_field.send_keys(custom_text)

    sleep(2)

    # Click on "Send now"
    send_now_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Send now"]')
    send_now_button.click()

    sleep(2)

    print("Done")