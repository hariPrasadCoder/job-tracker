import requests
import re
import string
import html
import docx
import spacy
import pdfplumber
import nltk
import random
import openai
import pandas as pd
import concurrent.futures
from functools import lru_cache
from fuzzywuzzy import fuzz
from multiprocessing import Pool
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download stopwords only once when the module is imported
# nltk.download('stopwords')

nlp = spacy.load("en_core_web_sm")

#Function to remove links in preprocessing
def remove_links_async(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    text_without_links = re.sub(url_pattern, '', text)
    return text_without_links

# Extract text and add spaces before new lines
def extract_text_with_spaces(html):
    soup = BeautifulSoup(html, "html.parser")
    text_with_spaces = ' '.join([text.strip() for text in soup.stripped_strings])
    return text_with_spaces

#Function to preprocess text
def preprocess_text(text, custom_stop_words_file=r'C:\Users\Pravallika Molleti\resume-skills-matcher\Resume-skills-matcher\data\stopwords.txt'):
    text = text.lower()
    text = remove_links_async(text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = text.replace('\n', ' ')

    doc = nlp(text)

    # Read custom stop words from file
    with open(custom_stop_words_file, 'r') as file:
        custom_stop_words = [line.strip() for line in file]

    stop_words = set(stopwords.words("english"))
    custom_stop_words_set = set(custom_stop_words)

    cleaned_tokens = []

    for token in doc:
        if token.text.lower() not in stop_words and token.text.lower() not in custom_stop_words_set:
            if token.is_alpha:
                if len(token.text) > 1:
                    if token.pos_ in ['PROPN', 'NOUN', 'VERB'] and len(token.text) > 1:
                        cleaned_tokens.append(token.text)

    cleaned_text = ' '.join(cleaned_tokens)
    return cleaned_text

#Function to extract tect from pdf or doc resume
def extract_text_from_pdf_or_doc(file_path):
    try:
        text = ''

        if file_path.lower().endswith('.pdf'):
            # Extract text from a PDF file using pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text()

        elif file_path.lower().endswith('.docx'):
            # Extract text from a Word (docx) file
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text
        else:
            print("Unsupported file format. Only PDF and DOCX files are supported.")
            return None

        # Remove leading and trailing whitespaces
        text = text.strip()
        text = text.replace('\n', ' ')

        return text

    except Exception as e:
        print(f"Error processing file: {e}")
        return None

#Function to extract job description from url
def extract_text_from_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    }

    try:
        if url.startswith('https://www.linkedin.com/jobs/collections/'):
            id = url.split('currentJobId=')[1].split('&')[0]
            url = 'https://www.linkedin.com/jobs/view/' + str(id)

        elif url.startswith('https://www.linkedin.com/jobs/search/'):
            id = url.split('currentJobId=')[1].split('&')[0]
            url = 'https://www.linkedin.com/jobs/view/' + str(id)

        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        job_description = str(soup.find('div', class_='description__text description__text--rich').find('div'))
        job_description = extract_text_with_spaces(job_description)

        job_title = soup.find('h1', class_='top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title').text.strip()

        return job_title, job_description
    except Exception as e:
        print("Error while retrieving text from the URL:", str(e))
        return ('None', 'None')  

#Function to calculate Bag Of Words
def calculate_bow(resume_text, job_description):
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform([resume_text, job_description])
    return vectors

#Function to calculate cosine similarity
def calculate_similarity(vectors):
    similarity = cosine_similarity(vectors)
    return similarity[0][1]

#Function to caluclate similar job titles
def calculate_word_similarity(job_name_ref, job_title):
    return fuzz.ratio(job_name_ref.lower(), job_title.lower())


# Function to preprocess job descriptions
def preprocess_job_descriptions(df):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        job_descriptions = list(executor.map(preprocess_text, df['Job Description']))

    df['Job Description'] = job_descriptions
    return df

@lru_cache(maxsize=None)
# Function to extract words and calculate TF-IDF words from similar jobs from the job_description.csv document corpus
def calculate_tfidf_similarity_cached(url, file_path=r'C:\Users\Pravallika Molleti\resume-skills-matcher\Resume-skills-matcher\data\Job_descriptions.csv', similarity_threshold=40, max_features=1000):
    df = pd.read_csv(file_path)
    
    # Take a random sample of 30-40 rows
    sample_size = random.randint(30, 40)
    df_sample = df.sample(n=sample_size, random_state=42)

    # Extract job title dynamically from the URL
    job_name, _ = extract_text_from_url(url)

    # Calculate similarity scores
    df_sample['Similarity'] = df_sample['Job Title'].apply(lambda x: calculate_word_similarity(job_name, x))
    max_similarity = df_sample['Similarity'].max()

    # Filter data early based on similarity threshold
    if max_similarity >= similarity_threshold:
        # Sort the DataFrame by similarity in descending order
        df_sample = df_sample.sort_values(by='Similarity', ascending=False)

        # Use loc to avoid the warning and reindexing
        df_filtered = df_sample.loc[df_sample['Similarity'] >= similarity_threshold].copy()
    else:
        # If the maximum similarity is less than the threshold, consider all job descriptions
        df_filtered = df_sample.copy()

    # Parallelized preprocessing of job descriptions
    df_filtered = preprocess_job_descriptions(df_filtered)

    # TF-IDF Calculation
    vectorizer = TfidfVectorizer(stop_words='english', max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(df_filtered['Job Description'])

    # Get feature names (terms)
    feature_names = vectorizer.get_feature_names_out()

    # Create a DataFrame to display TF-IDF scores
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)
    tfidf_df['Job Title'] = df_filtered['Job Title']

    # Sum the TF-IDF scores for each term across all documents
    term_importance = tfidf_matrix.sum(axis=0).A1

    # Sort terms based on their total TF-IDF score in ascending order
    sorted_terms_df = pd.DataFrame({'Term': feature_names, 'TF-IDF Sum': term_importance}) \
        .sort_values(by='TF-IDF Sum', ascending= False)

    # Extract the terms from the DataFrame
    all_terms = sorted_terms_df['Term'].tolist()

    return all_terms

#Function to reorder skills in the order of TF-IDF score
def reorder_skills(skill_list,url):
    all_terms = calculate_tfidf_similarity_cached(url)
    ordered_skills = [skill for skill in all_terms if skill in skill_list]
    not_present_skills = [skill for skill in skill_list if skill not in all_terms]
    ordered_skills.extend(not_present_skills)
    return ordered_skills

#Function to sort the ordered skills by pos by putting skills at top (proper nouns as per pos)
def sort_skills_by_pos(word_list):
    # Function to get POS tags for each word
    def get_pos(word):
        doc = nlp(word)
        return (word, doc[0].pos_) if doc else (word, 'OTHER')

    # Create a list of tuples (word, pos)
    word_pos_list = [get_pos(word) for word in word_list]

    # Custom order for POS tags
    custom_pos_order = {'PROPN': 0, 'NOUN': 2, 'OTHER': 1, 'VERB': 3, }

    # Sort the list based on the custom order
    sorted_word_pos_list = sorted(word_pos_list, key=lambda x: custom_pos_order.get(x[1], custom_pos_order['OTHER']))

    # Extract the sorted words
    sorted_word_list = [word for word, _ in sorted_word_pos_list]

    return sorted_word_list

def capitalize_words(words_list):
    capitalized_list = []
    for word in words_list:
        if len(word) <= 3:
            capitalized_list.append(''.join([letter.capitalize() for letter in word]))
        else:
            capitalized_list.append(word.capitalize())
    return capitalized_list