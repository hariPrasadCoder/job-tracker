# Description: Streamlit app to provide Resume Review using OpenAI GPT-3
# Author: Pravallika Molleti

__title__ = "Resume Reviewer"
__author__ = "Pravallika Molleti"

import streamlit.components.v1 as components
import pdfkit
from datetime import datetime
import os
import openai
import streamlit as st
import io
from pdfminer.high_level import extract_text
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import base64


# Authenticate with OpenAI API using your API key
# openai.api_key = os.getenv('OPEN_AI_KEY')

# openai.api_key = "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"

config = pdfkit.configuration(wkhtmltopdf=r"C:\Users\Pravallika Molleti\AI RESUME REVIEWER\AI-Resume-Reviewer\wkhtmltopdf.exe")


#Function to extract HTML from PDF
async def extract_html_from_pdf(file):
    file_contents = await file.read()  
    pdf_bytesio = io.BytesIO(file_contents)
    html_bytesio = io.BytesIO()
    laparams = LAParams()
    extract_text_to_fp(pdf_bytesio, html_bytesio, laparams=laparams)
    html_text = html_bytesio.getvalue().decode("utf-8")
    return html_text



# Function to generate resume review
def generate_resume_review(resume_text, length=300):
    # Set up the prompt for OpenAI
    prompt = f"""
Act as a career counselor and provide personalized recommendations to improve the 
quality of my resume: '{resume_text}'.  
All of the categories should have a specific example from resume of how it can be improved:

1. **Summary:**
    - analyze and give a personalized example from resume to improve
   - If a summary is not present, suggest adding a brief summary highlighting key achievements and career goals.

2. **Structure, Hierarchy, and Formatting:**
- - analyze and give a personalized example from resume to improve
   - Check for clear sections (Work Experience, Education, Projects, Skills, etc.) with appropriate headings and subheadings.
   - if no bulleted points point it out also emphasize uniformity by giving personalized examples
   - if no consistent hierarchy point it out by giving personalized examples

3. **Impact and Quantifiable Results:**
- - analyze and give a personalized example from resume to improve
   - Evaluate each work experience bullet point for specific achievements and quantifiable results.
   - Suggest using action verbs and power words to emphasize accomplishments by giving personalized examples

4. **Vocabulary Enhancement:**
- - analyze and give a personalized example from resume to improve
   - Recommend incorporating industry-specific keywords and terminology.
   - Identify and replace weak or repetitive words with more impactful synonyms by giving personalized examples

5. **Grammar and Sentence Structure:**
- - analyze and give a personalized example from resume to improve
   - Proofread for grammatical errors, typos, and sentence structure.
   - Encourage the use of active voice and avoidance of passive voice constructions by giving personalized examples

6. **Skill Set Enhancement:**
- - analyze and give a personalized example from resume to improve
   - Highlight key skills relevant to the target job.
   - Suggest including additional certifications or completed courses to strengthen the skill set  by provided list of personalized skill words

7. **Additional Sections:**
- - analyze and give a personalized example from resume to improve
   - Recommend adding relevant sections like Awards and Recognition, Leadership Experience, or Publications.
   - Consider including volunteer work, internships, or extracurricular activities that showcase skills.

In continuation to the above, ask a list of details question by question to tailor the recommendations further:

- Number of years of total experience?
- Leadership experience: Have you led any teams? If so, provide details.
- Awards and recognition: Have you received any? Include details.
- Impact metrics: Quantify the impact of your work experience.
- other tools you have used.

The above is just an example of the format. You can use your recommendations and also ask more questions if necessary'"""

    prompt += f"If inputs don't seem like resume content, simply reply with exactly 'Error! Please provide a resume'."

    # Call OpenAI API for chat completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract and return the generated text
    resume_review = response.choices[0].message['content']
    return resume_review

# Function to generate an improvised resume taking the recommendations
def gen_new_resume(resume_text, recommendations):
    prompt = f"""
             The below is my resume:
              '{resume_text}',
             The below are the suggestions you have to follow on improving the above resume in a professional format which sfter should not require any further edits.
              '{recommendations}'
             As part of the resume improvement process, please consider the following suggestions to enhance the professionalism and structure of the existing resume:

1. Begin with the provided resume_text and follow these guidelines for modifications:
   - Maintain the current structure and links of the resume_text.
   - Ensure proper alignment for sections such as user name, contact details, and related profiles.
   - Center-align user name, details, and related profile contacts.
   - Any dates or years like period of time align them to the right of the page.
   - Keep the hierarchical arrangement with a focus on maintaining the original order.

2. Follow the sequence: Summary, Work Experience, Education, Projects, and Skills(skills always distanced by comma and not on bulleted points) .
   - Place the suggestions based summary at the top, followed by Work Experience, Education (based on preference), Projects, and Skills.
   - Do not omit any content from the original resume; include all relevant information and links.

3. Pay special attention to key details from the original resume; elaborate on them based on the recommendations and keep them to points same like parent resume.

4. Generate the HTML text of the updated resume adhering to the provided guidelines.

Please note that the goal is to maintain the structure of the original resume while incorporating professional formatting improvements. Ensure that the final HTML reflects these modifications and give only HTML text """

    # Call OpenAI API for chat completion
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])

    # Extract and return the generated text
    new_resume = response.choices[0].message['content']
    return new_resume


# Function to generate PDF from HTML content
def generate_pdf(html_content, filename="test2_generated_resume.pdf"):
    # Save the HTML content to a temporary file
    temp_html_path = "temp_resume.html"
    with open(temp_html_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    # Define options for pdfkit
    options = {
        'page-size': 'Letter',  # You can adjust the page size (A4, Letter, etc.)
        'margin-top': '1mm',
        'margin-right': '1mm',
        'margin-bottom': '5mm',
        'margin-left': '1mm',
    }

    # Generate PDF using pdfkit and return as base64
    pdf_content = pdfkit.from_file(temp_html_path, False, options=options)
    pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

    # Clean up temporary HTML file
    os.remove(temp_html_path)

    return pdf_base64

# Utility function to create a download link for binary files
def get_binary_file_downloader_html(bin_file, label='Download PDF'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}" target="_blank">{label}</a>'
    return href

