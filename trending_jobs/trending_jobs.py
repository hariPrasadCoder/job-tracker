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
import openai

num_of_pages = 1
CV_Clear = ''
applied_jobs_list = []
job_titles = [
                # 'Data Scientist',
                # 'Data Analyst', 
                # 'Software Engineer', 
                'Data Engineer', 
                'Machine Learning Engineer',
                'Supply Chain',
                'Analyst', 
                'Product Manager', 
                'Project Manager',
                'Data Science internship',
                'Software Enginner internship',
                'Data Analyst internship',
                'Data Engineer internship',
                'Machine Learning Engineer internship',
                'Product Manager internship',
                'Project Manager internship',
                'Analyst internship',
                'Supply Chain internship'
                ]
locations = ['United States', 
             'Austin',
             'San Francisco',
             'New York',
             'Seattle',
             'Chicago',
            #  'Denver',
             'Boston',
            #  'Portland',
             'Los Angeles',
             'Washington, D.C.',
            #  'New Orleans',
            #  'Miami',
            #  'Raleigh',
            #  'San Diego',
             'Dallas',
            #  'Charleston',
            #  'Nashville',
            #  'Houston',
            #  'Philadelphia',
             'Atlanta',
            #  'Colorado Springs',
            #  'Tampa',
            #  'Minneapolis',
             'San Antonio',
            #  'Madison',
             'Phoenix',
            #  'Charlotte',
            #  'Las Vegas',
            #  'Jacksonville',
            #  'Pittsburgh',
            #  'Salt Lake City',
            #  'Savannah',
            #  'Baltimore',
            #  'Kansas City',
            #  'Oklahoma City',
            #  'Omaha',
            #  'Indianapolis',
            #  'Columbus',
            #  'Honolulu',
            #  'Milwaukee',
            #  'San Jose',
            #  'Detroit',
            #  'Albuquerque',
            #  'Tucson',
            #  'Virginia Beach',
            #  'Memphis',
            #  'Durham',
            #  'Sacramento',
            #  'Fort Worth',
            #  'Ann Arbor',
            #  'Alexandri'
            ]
# job_titles = ['Data Scientist', 'Mechanical Engineer']
# locations = ['United States', 'India']

trending_jobs_df = pd.DataFrame()
for job_title in job_titles:
    for location in locations:
        print(job_title + ' -- ' + location)
        # Scrape linkedin data
        info_table = scrape_linkedin(job_title, location, num_of_pages, applied_jobs_list)
        print(info_table)

        # # Finding match percentage
        final_info_table = match_percentage(info_table, CV_Clear)
        final_info_table['Category'] = job_title
        print(final_info_table)
        trending_jobs_df = pd.concat([trending_jobs_df, final_info_table])
    trending_jobs_df.to_csv('trending_jobs.csv', index=False)