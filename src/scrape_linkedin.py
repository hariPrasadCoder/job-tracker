import requests
from bs4 import BeautifulSoup
import urllib
from datetime import datetime
import pandas as pd

def scrape_linkedin(job_title, location, num_of_pages, applied_jobs_list):
    # Scrape linkedin data

    info = []
    headers = {'User-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

    for page in range(num_of_pages):
        getVars = {'keywords' : job_title, 'location' : location ,'sort' : 'date', 'start': str(page*10), 'f_TPR':'r604800'}
        url = ('https://www.linkedin.com/jobs/search?' + urllib.parse.urlencode(getVars))
        r = requests.get(url, headers=headers, verify=False)
        html = r.content
        soup = BeautifulSoup(html, "html.parser")
        jobs = soup.find_all('div', class_ = 'base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')
        for job in jobs:
            title = str(job.find('h3', class_='base-search-card__title').text.strip())
            company = str(job.find('h4', class_='base-search-card__subtitle').text.strip())
            post_date = datetime.strptime(job.find('time')['datetime'], '%Y-%m-%d').date()

            link = job.find('a', class_='base-card__full-link')['href']
            inp = link.split('?')[0].split('/')[-1]
            inp = ''.join(' ' if not ch.isdigit() else ch for ch in inp).strip()
            id = inp.split()[-1]
            link = 'https://www.linkedin.com/jobs/view/' + str(id)
            
            info.append([title,company,post_date,link])
        

    cols = ['Job_title','Company','Job_posted_date','Link']
    info_table = pd.DataFrame(info, columns = cols)
    info_table = info_table.drop_duplicates(subset=['Job_title', 'Company'])
    info_table =  info_table[~info_table['Link'].isin(applied_jobs_list)]
    # sort by post date
    info_table = info_table.sort_values(by = 'Job_posted_date', ascending = False).reset_index(drop=True)

    return info_table
