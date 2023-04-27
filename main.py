from fastapi import FastAPI, UploadFile, File, Form
from src.cv_to_text import cv_to_text
from src.scrape_linkedin import scrape_linkedin
from src.match_percentage import match_percentage
import shutil

app = FastAPI()

@app.post("/jobs")
async def hello(job_title: str = Form(...), location: str = Form(...), file: UploadFile = File(...)):
    num_of_pages = 2
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