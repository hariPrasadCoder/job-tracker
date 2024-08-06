
from src.find_people import find_people, login_linkedin
from src.send_connection import send_connection

import requests
from bs4 import BeautifulSoup
import pandas as pd

import urllib
import random

def reach_out(
        job_urls = ['sample'], # https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3671617648,https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3731932698
        job_title = ['sample'],  # Data Scientist,Data Scientist
        company_name = ['sample'],  # Stripe,Etsy
        title_of_person = 'director', #recruiter
        useremail = 'hr2514@columbia.edu', #hr2514@columbia.edu
        userpassword = 'hpprasad',
        # receiver_linkedin_url, 
        custom_text = 'sample', # Hi {firstname}, I'm Hari, I believe that I will be a right fit for the {job_title} at {company_name}. Would you mind passing on my resume to the hiring manager?
        requests_send_cnt = 40
                ):

    # Take Company's people page url from Job url
    applied_jobs_list = job_urls
    job_title_list = job_title
    company_name_list = company_name

    company_url_people_list = {}
    for i in range(len(applied_jobs_list)):
        attempts = 0
        max_attempts = 10

        while attempts < max_attempts:
            try:
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
                print(company_url_people_list)
                break
            except Exception as e:
                print('Attempting again')
                attempts += 1
                if attempts >= max_attempts:
                    print('Error' + str(e))

    # Getting people linkedin urls
    people_linkedin_url = []
    driver = login_linkedin(useremail, userpassword)
    for key, value in company_url_people_list.items():
        try:
            company_url_people = value[0]
            job_title = value[1]
            company_name = value[2]

            user_profiles, driver = find_people(company_url_people, driver)[:10]

            for user_profile in user_profiles:
                people_linkedin_url.append([user_profile, job_title, company_name])
        except:
            print('Error')

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
            if requests_send == requests_send_cnt:
                break
        except:
            print('Error')
    return "Done"

def main():
    print('Hi')
    df = pd.read_csv('jotterwolf_export.csv')
    df['Status'] = df['Status'].fillna('Applied')
    df = df[df['Status'].str.contains('Interviewing')]
    df = df.head(20)

    reach_out(
        job_urls = list(df['Job Link']),
        job_title = list(df['Role']),
        company_name = list(df['Company Name']), 
        title_of_person = 'director', 
        useremail = 'hr2514@columbia.edu', 
        userpassword = 'hpprasad',
        custom_text = "Hi {firstname}, I'm Hari, I believe that I will be a right fit for the {job_title} at {company_name}. Would you mind passing on my resume to the hiring manager? Your small action may change my life. Thanks!",
        requests_send_cnt = 40
    )

if __name__ == "__main__":
    main()