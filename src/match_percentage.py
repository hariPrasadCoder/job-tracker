import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def extract_currency_values(string):
    pattern = r"\$\d+(?:\.\d+)?"
    matches = re.findall(pattern, string)
    values = [match.strip("$") for match in matches]
    return values

def match_percentage(info_table, CV_Clear):
    # Finding match percentage
    headers = {'User-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
    match_percents = []
    image_links = []
    locations = []
    job_descriptions = []
    salary_ranges = []
    for l in info_table['Link']: 
        try:
            # extract job description from 2nd webpage (ie, main page for each job post)
            r = requests.get(l, headers=headers)
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
            
            # calculate match percentage 
            Match_Test = [CV_Clear,job_description]
            cv = CountVectorizer()
            count_matrix = cv.fit_transform(Match_Test)
            MatchPercentage = cosine_similarity(count_matrix)[0][1]*100

            match_percents.append(MatchPercentage)
            image_links.append(image_link)
            locations.append(location)
            job_descriptions.append(job_description)
            salary_ranges.append(salary_range)
        except:
            print('Error with parsing job description')
            match_percents.append(0)
            image_links.append('Unable to scrape')
            locations.append('Unable to scrape')
            job_descriptions.append('Unable to scrape')
            salary_ranges.append('Unable to scrape')

    match_percent = pd.DataFrame()
    match_percent['Matching_percentage'] = match_percents
    match_percent['Logo'] = image_links
    match_percent['Location'] = locations
    match_percent['Job_description'] = job_descriptions
    match_percent['Salary_range'] = salary_ranges
    final_info_table = pd.concat([info_table, match_percent], axis=1)
    final_info_table = final_info_table.sort_values(by = 'Matching_percentage', axis = 0, ascending=False)

    final_info_table = final_info_table.nlargest(10,['Matching_percentage'])

    return final_info_table