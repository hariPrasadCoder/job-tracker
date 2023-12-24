import streamlit as st
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
import openai
from bs4 import BeautifulSoup


def scrape_linkedin_profile(url, useremail, userpassword):
    # Set up Selenium Chrome driver
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    driver.get("http://linkedin.com/")
    
    try:
        elementID = driver.find_element(By.ID, "session_key")
        elementID.send_keys(useremail)

        elementID = driver.find_element(By.ID, 'session_password')
        elementID.send_keys(userpassword)

        elementID.submit()

        driver.implicitly_wait(5)

        try:
            dismiss_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Dismiss"]')
            dismiss_button.click()
        except (NoSuchElementException, ElementNotInteractableException):
            pass

        
    except Exception as e:
        st.error(f"Error: {e}")
        return None
    
    driver.get(url)

    profile_data = {
        "headline": None,
        "about_section": None,
        "projects": None,
        "feature_me": None,
        "education": None,
        "experience": None,
    }

    try:
        profile_data["headline"] = driver.find_element(By.CLASS_NAME, 'text-body-medium').text.strip()
    except NoSuchElementException:
        pass  

    try:
        profile_data["about_section"] = driver.find_element(By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section[4]/div[3]/div/div/div/span[1]').text.strip()
    except NoSuchElementException:
        pass 

    ul_tag = driver.find_elements(By.CSS_SELECTOR, 'section[data-view-name="profile-card"]')

    for tag in ul_tag:
        try:
            text = tag.text
            if text.startswith("Experience"):
                profile_data["experience"] = text
            elif text.startswith("Education"):
                profile_data["education"] = text
            elif text.startswith("Featured"):
                profile_data["feature_me"] = text
            elif text.startswith("Projects"):
                profile_data["projects"] = text
        except Exception as e:
            st.warning(f"Error processing section: {e}")

    return profile_data

def generate_gpt_suggestions(text, section_name):
    prompt = f"Optimize the {section_name} section for your LinkedIn profile:\n{text}\nImprove and refine the following text to make it more professional and expressive for your LinkedIn profile. Consider the following guidelines:\n\n"

    if section_name.lower() == "headline":
        prompt += "- Craft a compelling headline that showcases your expertise and passion in a concise manner.\n"

    elif section_name.lower() == "about_section":
        prompt += "- Write a brief and impactful 'About' section that highlights your key strengths, experience, and goals.\n"

    elif section_name.lower() == "projects":
        prompt += "- Clearly name each project and provide detailed, technical descriptions to showcase your skills and achievements in points for each project .\n"

    elif section_name.lower() == "experience":
        prompt += "- Specify the company name and provide clear, crisp descriptions of your roles and contributions using technical language for each experience.\n"

    elif section_name.lower() == "featured":
        prompt += "- Clearly name each featured item (blog posts, projects, etc.) and provide concise, technical descriptions for each featured project.\n"

    elif section_name.lower() == "education":
        prompt += "- Include the college/university name and present your educational achievements and skills in a clear and concise manner  for each education detail.\n"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300, 
        temperature=0.7,
        stop=None,
    )
    return response.choices[0].text.strip()