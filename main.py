from fastapi import FastAPI, UploadFile, File, Form
from src.cv_to_text import cv_to_text
from src.scrape_linkedin import scrape_linkedin
from src.match_percentage import match_percentage
from src.find_people import find_people
from src.send_connection import send_connection
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
import time
from time import sleep
import pandas as pd
from io import BytesIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import re
import openai
import urllib
import random

def extract_currency_values(string):
    pattern = r"\$\d+(?:\.\d+)?"
    matches = re.findall(pattern, string)
    values = [match.strip("$") for match in matches]
    return values

app = FastAPI()

@app.post("/jobs")
async def hello(job_title: str = Form(...), location: str = Form(...), file: UploadFile = File(...), applied_jobs: str = Form(...)):
    num_of_pages = 4

    applied_jobs_list = applied_jobs.split(',')
    pdf_file = BytesIO(await file.read())
    extracted_text = BytesIO()

    with pdf_file, extracted_text:
        laparams = LAParams()
        extract_text_to_fp(pdf_file, extracted_text, laparams=laparams)
        extracted_text.seek(0)
        text = extracted_text.read().decode()

    CV_Clear = text.replace("\n","").replace('●', "")
    print(CV_Clear)

    # Scrape linkedin data
    info_table = scrape_linkedin(job_title, location, num_of_pages, applied_jobs_list)
    print(info_table)

    # # Finding match percentage
    final_info_table = match_percentage(info_table, CV_Clear)
    print(final_info_table)

    final_json = final_info_table.to_dict(orient="records")
        
    return final_json

@app.post("/extract_jobinfo")
async def hello(url: str = Form(...)):
    headers = {'User-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

    if url.startswith('https://www.linkedin.com/jobs/'):
        if url.startswith('https://www.linkedin.com/jobs/collections/'):
            id = url.split('currentJobId=')[1].split('&')[0]
            url = 'https://www.linkedin.com/jobs/view/' + str(id)

        elif url.startswith('https://www.linkedin.com/jobs/search/'):
            id = url.split('currentJobId=')[1].split('&')[0]
            url = 'https://www.linkedin.com/jobs/view/' + str(id)

        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        job_description = str(soup.find('div', class_='description__text description__text--rich').find('div'))

        salary_range = extract_currency_values(job_description.replace(',',''))
        if len(salary_range)>1:
            salary_range = '$'+salary_range[0] + '- $' + salary_range[1]
        else:
            salary_range = 'No Salary Info Found'

        image_raw_link = soup.find('div', class_='top-card-layout__card relative p-2 papabear:p-details-container-padding').findAll('img', class_="artdeco-entity-image")[0]['data-delayed-url']
        image_link = image_raw_link.replace('amp;','')

        location = soup.find('div', class_='topcard__flavor-row').findAll('span',class_='topcard__flavor topcard__flavor--bullet')[0].text.replace("\n","").strip()

        company_name = soup.find('div', class_='topcard__flavor-row').find('a',class_='topcard__org-name-link topcard__flavor--black-link').text.replace("\n","").strip()

        job_title = soup.find('h1', class_ = 'top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title').text

        job_link = url


    elif url.startswith('https://www.glassdoor.com/job-listing'):
        # Glassdoor scraping logic
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        time.sleep(3)


        try:
            # Try to click the "Show More" button
            driver.find_element(By.XPATH, '//div[@class="css-1rzz8ht ecgq1xb2"]').click()
            job_description = driver.find_element(By.XPATH, '//div[@class="desc css-58vpdc ecgq1xb5"]').get_attribute('outerHTML')
        except ElementNotInteractableException:
            # If the button is not interactable, extract the job description without clicking
            job_description = driver.find_element(By.XPATH, '//div[@class="desc css-58vpdc ecgq1xb5"]').get_attribute('outerHTML')

        # Handle the case where estimated salary is not available for all jobs
        if extract_currency_values(job_description):
            salary_range = extract_currency_values(job_description.replace(',', ''))
            if len(salary_range) > 1:
                salary_range = '$' + salary_range[0] + ' - $' + salary_range[1]
            else:
                salary_range = 'No Salary Info Found'
        else:
            try:
                salary_range = driver.find_element(By.XPATH, '//div[@class="css-1v5elnn e11nt52q2"]/span[@class="small css-10zcshf e1v3ed7e1"]').text.replace('K', ',000')
                salary_range = re.sub(r'\[.*?\]', '', salary_range).strip()
                if ':' in salary_range:
                    salary_range = salary_range.split(':')[1]
            except NoSuchElementException:
                salary_range = 'No Salary Info Found'

        image_link = driver.find_element(By.XPATH, '//span[@class="css-13u5hxa epu0oo22"]/img').get_attribute('src')
        
        location = driver.find_element(By.XPATH, '//div[@class="css-1v5elnn e11nt52q2"]/span[@data-test="location"]').text.strip()

        company_name = driver.find_element(By.XPATH, '//div[@data-test="employer-name"]/div').text.strip().split('\n')[0]
        
        job_title = driver.find_element(By.XPATH, '//div[@data-test="job-title"]').text.strip()

        job_link = url

        driver.quit()


    elif url.startswith('https://www.indeed.com/viewjob'):
        # Indeed scraping logic
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        time.sleep(3)

        job_description = driver.find_element(By.CSS_SELECTOR, 'div[class*="jobsearch-JobComponent-description"]').get_attribute('outerHTML')
        
        # Handle the case where estimated salary is not available for all jobs
        try:
            salary_element = driver.find_element(By.CSS_SELECTOR, 'div#salaryInfoAndJobType span.css-2iqe2o')
            salary_range = salary_element.text
        except NoSuchElementException:
            if extract_currency_values(job_description):
                salary_values = extract_currency_values(job_description.replace(',', ''))
                if len(salary_values) > 1:
                    salary_range = '$' + salary_values[0] + ' - $' + salary_values[1]
                else:
                    salary_range = 'No Salary Info Found'
            else:
                salary_range = 'No Salary Info Found'
                
        image_link = None

        location = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="inlineHeader-companyLocation"] div').text
        
        company_name = driver.find_element(By.CSS_SELECTOR, 'span[class*="css-"][class*="e1wnkr"]').text.strip()
        
        job_title = driver.find_element(By.CSS_SELECTOR, 'div[class*="jobsearch-JobInfoHeader-title-container"]').text.strip()
        
        job_link = url

        driver.quit()


    else:
        return {"error": "Unsupported job URL format"}


    # Create and return job details
    job_details = pd.DataFrame(columns=['company_name', 'job_title', 'company_logo', 'job_description', 'location', 'job_link'])
    job_details['company_name'] = [company_name]
    job_details['job_title'] = [job_title]
    job_details['company_logo'] = [image_link]
    job_details['job_description'] = [job_description]
    job_details['salary_range'] = [salary_range]
    job_details['location'] = [location]
    job_details['job_link'] = [job_link]

    job_details = job_details.to_dict(orient="records")

    return job_details    


@app.post("/chatgpt")
async def hello(job_title: str = Form(...), job_desc: str = Form(...), resume: UploadFile = File(...), job_link: str = Form(...), key: str = Form(...),):
    pdf_file = BytesIO(await resume.read())
    extracted_text = BytesIO()

    with pdf_file, extracted_text:
        laparams = LAParams()
        extract_text_to_fp(pdf_file, extracted_text, laparams=laparams)
        extracted_text.seek(0)
        text = extracted_text.read().decode()

    CV_Clear = text.replace("\n","").replace('●', "")
    print(CV_Clear)

    openai.api_key = key
    messages = [ {"role": "system", "content": 
                "You are a intelligent assistant."} ]
    
    ##====== First Prompt ========
    message = f"""
    My resume - {CV_Clear}

    Job description that I am trying to apply - {job_desc}

    Generate a 200 word pitch for me to introduce myself to the interviewer by highlighting the common points between my resume and job description.
    """

    messages.append(
            {"role": "user", "content": message},
        )
    
    chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    pitch = chat.choices[0].message.content
    print(pitch)
    messages.append({"role": "assistant", "content": pitch})


    ##======== Second Prompt =========
    message = f"""
    create 5 commonly asked questions in an interview for a {job_title} role and use my resume to answer it
    """

    messages.append(
            {"role": "user", "content": message},
        )
    
    chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    q_a = chat.choices[0].message.content
    print(q_a)
    messages.append({"role": "assistant", "content": q_a})

    chatgpt = pd.DataFrame()
    chatgpt['pitch'] = [str(pitch)]
    chatgpt['q_a'] = [str(q_a)]
    chatgpt['job_link'] = [str(job_link)]

    print(chatgpt)

    chatgpt = chatgpt.to_dict(orient="records")

    return chatgpt

@app.post("/reach_out")
async def hello(
                job_urls: str = Form(...), # https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3671617648,https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3731932698
                job_title: str = Form(...),  # Data Scientist,Data Scientist
                company_name: str = Form(...),  # Stripe,Etsy
                title_of_person: str = Form(...), #recruiter
                useremail: str = Form(...), #hr2514@columbia.edu
                userpassword: str = Form(...), #hpprasad
                # receiver_linkedin_url: str = Form(...), 
                custom_text: str = Form(...) # Hi {firstname}, I'm Hari, I believe that I will be a right fit for the {job_title} at {company_name}. Would you mind passing on my resume to the hiring manager?
                ):

    # Take Company's people page url from Job url
    applied_jobs_list = job_urls.split(',')
    job_title_list = job_title.split(',')
    company_name_list = company_name.split(',')

    company_url_people_list = {}
    for i in range(len(applied_jobs_list)):
        applied_job = applied_jobs_list[i]
        job_title = job_title_list[i]
        company_name = company_name_list[i]
        headers = {'User-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

        if applied_job.startswith('https://www.linkedin.com/jobs/collections/'):
            id = applied_job.split('currentJobId=')[1].split('&')[0]
            applied_job = 'https://www.linkedin.com/jobs/view/' + str(id)

        elif applied_job.startswith('https://www.linkedin.com/jobs/search/'):
            id = applied_job.split('currentJobId=')[1].split('&')[0]
            applied_job = 'https://www.linkedin.com/jobs/view/' + str(id)

        r = requests.get(applied_job, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        company_url = soup.find('div', class_='sub-nav-cta__sub-text-container').find('a',class_='sub-nav-cta__optional-url')['href'].split('?')[0]

        getVars = {'keywords' : title_of_person}
        company_url_people = f'{company_url}/people/?{urllib.parse.urlencode(getVars, safe=",")}'

        company_url_people_list[i] = [company_url_people,job_title,company_name]

    # Getting people linkedin urls
    people_linkedin_url = []
    for key, value in company_url_people_list.items():
        company_url_people = value[0]
        job_title = value[1]
        company_name = value[2]

        user_profiles, driver = find_people(company_url_people, useremail, userpassword)[:10]

        for user_profile in user_profiles:
            people_linkedin_url.append([user_profile, job_title, company_name])

    print(people_linkedin_url)

    # Sending connection requests to people
    random.shuffle(people_linkedin_url)
    requests_send = 0
    for i in people_linkedin_url:
        person_linkedin_url = i[0]
        job_title = i[1]
        company_name = i[2]
        try:
            send_connection(person_linkedin_url, custom_text, job_title, company_name, driver)
            requests_send += 1
            if requests_send == 10:
                break
        except:
            print('Error')
    return "Done"
