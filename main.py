from fastapi import FastAPI, UploadFile, File, Form
from src.cv_to_text import cv_to_text
from src.scrape_linkedin import scrape_linkedin
from src.match_percentage import match_percentage
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import re

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

    if url.startswith('https://www.linkedin.com/jobs/collections/'):
        id = url.split('currentJobId=')[1]
        url = 'https://www.linkedin.com/jobs/view/' + str(id)

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    job_description = str(soup.find('div', class_='description__text description__text--rich').find('div'))

    salary_range = extract_currency_values(job_description.replace(',',''))
    if len(salary_range)>0:
        salary_range = '$'+salary_range[0] + '- $' + salary_range[1]
    else:
        salary_range = 'No Salary Info Found'

    image_raw_link = soup.find('div', class_='top-card-layout__card relative p-2 papabear:p-details-container-padding').findAll('img', class_="artdeco-entity-image")[0]['data-delayed-url']
    image_link = image_raw_link.replace('amp;','')

    location = soup.find('div', class_='topcard__flavor-row').findAll('span',class_='topcard__flavor topcard__flavor--bullet')[0].text.replace("\n","").strip()

    company_name = soup.find('div', class_='topcard__flavor-row').find('a',class_='topcard__org-name-link topcard__flavor--black-link').text.replace("\n","").strip()

    job_title = soup.find('h1', class_ = 'top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title').text

    job_link = url

    job_details = pd.DataFrame(columns = ['company_name', 'job_title', 'company_logo', 'job_description', 'location', 'job_link'])
    job_details['company_name'] = [company_name]
    job_details['job_title'] = [job_title]
    job_details['company_logo'] = [image_link]
    job_details['job_description'] = [job_description]
    job_details['salary_range'] = [salary_range]
    job_details['location'] = [location]
    job_details['job_link'] = [job_link]

    job_details = job_details.to_dict(orient="records")
        
    return job_details
