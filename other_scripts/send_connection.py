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
# plinks=pd.read_csv("linkedin_extracted_links.csv")

# first_column = list(plinks. iloc[1:, 0] )


service = Service("//Users//hariprasad.renganath//Documents//Github_personal//auto-job-application//chromedriver")
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

# s=Service('chromedriver')
# driver = webdriver.Chrome(service=s)
url = "http://linkedin.com/"

        # path to driver web driver		
driver.get(url)

custom_text = "Hi, I'm Hari! Looking forward to connecting with you"

# Getting the login element
username = driver.find_element(By.ID,"session_key")

# Sending the keys for username	
username.send_keys("hr2514@columbia.edu")

# Getting the password element								
password = driver.find_element(By.ID,"session_password")

# Sending the keys for password
password.send_keys("hpprasad")

actions = ActionChains(driver)
actions.send_keys(Keys.ENTER)
actions.perform()


sleep(2)

text="Your personalised note goes here :)"
# for i in first_column:
driver.get('https://www.linkedin.com/in/jiawen-ye-87244996/')

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


