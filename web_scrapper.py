import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import string


class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = self.extract_domain(base_url)
        self.content_directory = self.get_content_directory()

    def extract_domain(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc

    def ensure_directory_exists(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def get_content_directory(self):
        content_directory = os.getenv("CONTENT_RAW_DIR")
        self.ensure_directory_exists(content_directory)
        return content_directory

    def is_readable(self, text):
        # Check if the text contains only readable characters
        return all(char in string.printable or char.isspace() for char in text)

    def initial_crawler(self):
        try:
            response = requests.get(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()

            # Filter out non-readable characters
            text_content = ''.join(filter(self.is_readable, text_content))

            with open(os.path.join(self.content_directory,  os.getenv("SCRAP_DATA_FILE")), 'w', encoding='utf-8') as file:
                file.write(text_content)

            return set([link.get('href') for link in soup.find_all('a')])
        except requests.RequestException as e:
            print(f"Error scraping base {self.base_url}: {e}")

    def scrap_deeplinks(self, link):
        try:
            response = requests.get(link)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()

            # Filter out non-readable characters
            text_content = ''.join(filter(self.is_readable, text_content))

            # Append the scraped raw_data to the text file
            with open(os.path.join(self.content_directory, os.getenv("SCRAP_DATA_FILE")), 'a', encoding='utf-8') as file:
                file.write(text_content)
                file.write('\n\n')  # Add a separator between deep links

        except requests.RequestException as e:
            print(f"Error scraping {link}: {e}")

    def crawl_and_scrape(self):
        # Initial crawl
        links = self.initial_crawler()

        # Filter links
        filtered_links = {link for link in links if self.domain in link}

        # Scrape deep links
        for link in filtered_links:
            self.scrap_deeplinks(link)