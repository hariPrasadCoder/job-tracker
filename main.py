from fastapi import FastAPI
from src.cv_to_text import cv_to_text
from src.scrape_linkedin import scrape_linkedin
from src.match_percentage import match_percentage

app = FastAPI()

@app.get("/jobs")
async def hello():
    job_title = 'Data Engineer'
    location = 'New York'
    num_of_pages = 2
    # f = open('resume.pdf','rb')

    ## CV to texts
    CV_Clear = cv_to_text()

    # Scrape linkedin data
    info_table = scrape_linkedin(job_title, location, num_of_pages)
    print(info_table)

    # # Finding match percentage
    final_info_table = match_percentage(info_table, CV_Clear)
    print(final_info_table)

    final_json = final_info_table.to_json(orient="split")
        
    return final_json