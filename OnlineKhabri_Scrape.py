import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai

# Set up Google's Generative AI API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

ai_prompt = "Imagine you are a seasoned news article editor tasked with enhancing the uniqueness and personalization of the given article while preserving the core information. Your goal is to infuse a distinct tone and style into the article, making it engaging and relatable to the audience. Focus on rephrasing sentences, adding vivid descriptions, and injecting your own insights to enrich the narrative. Remember to maintain the integrity of the original content while crafting a fresh and captivating story. Keep the article length the same as in input."

category_urls = {
    'Business': 'https://timesofindia.indiatimes.com/rssfeeds/1898055.cms',
    'National': 'https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms',
    'International': 'https://timesofindia.indiatimes.com/rssfeeds/296589292.cms',
    'Sports': 'https://timesofindia.indiatimes.com/rssfeeds/4719148.cms',
    'Entertainment': 'https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms',
    'Tech': 'https://timesofindia.indiatimes.com/rssfeeds/66949542.cms',
    'Science': 'https://timesofindia.indiatimes.com/rssfeeds/-2128672765.cms',
    'Environment': 'https://timesofindia.indiatimes.com/rssfeeds/2647163.cms'
}
# Function to scrape article links from a given RSS feed URL
def scrape_article_links(url):
    article_links = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')
        items = soup.find_all('item')
        for item in items:
            pub_date_str = item.find('pubDate').text
            pub_date = datetime.strptime(pub_date_str[:-6], '%Y-%m-%dT%H:%M:%S')
            if pub_date.date() == datetime.today().date():
                link = item.find('link').text
                article_links.append(link)
    return article_links

# Function to scrape content from article link
def scrape_article_content(link):
    response = requests.get(link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', class_='_s30J clearfix')
        if content_div:
            return content_div.text.strip()
    return None

# Function to generate content using Google's Generative AI API
def generate_content(input_text, prompt):
    model = genai.GenerativeModel("gemini-pro-vision")
    response = model.generate_content([input_text, prompt])
    return response.text

# Streamlit app
st.set_page_config(page_title="Article Scraper", page_icon=":newspaper:")
st.title("Article Scraper with AI Content Generation")
st.write("This app scrapes articles from selected categories and uses Google's Generative AI to generate content.")

# Select category
selected_category = st.selectbox("Select category:", list(category_urls.keys()))

# Select number of articles
num_articles = st.number_input("Number of articles:", min_value=1)

# Button to execute scraping and content generation
if st.button("Scrape and Generate Content"):
    # Scrape articles
    article_links = scrape_article_links(category_urls[selected_category])
    if len(article_links) < num_articles:
        st.warning("Number of articles selected is greater than available articles for the selected category.")
    else:
        st.success("Scraping articles...")

        # Scrape and generate content for each article
        articles_to_display = article_links[:num_articles]
        for index, link in enumerate(articles_to_display):
            content = scrape_article_content(link)
            if content:
                # Generate content using AI
                generated_content = generate_content(content, ai_prompt)
                st.subheader(f"Generated Content for Article {index+1}")
                st.write(generated_content)
            else:
                st.warning(f"Failed to scrape content for article {index+1}")
