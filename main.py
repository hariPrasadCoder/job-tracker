from fastapi import FastAPI, UploadFile, File, Form
from src.cv_to_text import cv_to_text
from src.scrape_linkedin import scrape_linkedin
from src.match_percentage import match_percentage
import shutil
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = FastAPI()

@app.post("/jobs")
async def hello(job_title: str = Form(...), location: str = Form(...), file: UploadFile = File(...)):
    num_of_pages = 20
    with open('resume.pdf', 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    f = open('resume.pdf','rb')

    ## CV to texts
    CV_Clear = cv_to_text(f)

    # Scrape linkedin data
    info_table = scrape_linkedin(job_title, location, num_of_pages)
    print(info_table)

    # # Finding match percentage
    final_info_table = match_percentage(info_table, CV_Clear)
    print(final_info_table)

    final_json = final_info_table.to_dict(orient="records")
        
    return final_json

@app.post("/extract_jobinfo")
async def hello(url: str = Form(...)):
    headers = {'User-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    job_description = soup.find('div', class_='description__text description__text--rich').text

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
    job_details['location'] = [location]
    job_details['job_link'] = [job_link]

    job_details = job_details.to_dict(orient="records")
        
    return job_details