import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import os
from dotenv import load_dotenv

load_dotenv()


class TextCleaner:
    def __init__(self, content_path):
        self.content_path = content_path
        # Download NLTK resources (if not already downloaded)
        nltk.download('stopwords')
        nltk.download('punkt')
        nltk.download('wordnet')

    def clean_text(self, text):
        # Convert to lowercase
        text = text.lower()

        # Remove noise
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', '', text)

        # Tokenization
        tokens = word_tokenize(text)

        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]

        # Lemmatization
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]

        return ' '.join(tokens)

    def process_text_file(self, input_filename, output_filename):
        with open(os.path.join(self.content_path, input_filename), 'r', encoding='utf-8') as file:
            data = file.read()

        unique_lines = set(data.split('\n'))
        cleaned_data = '\n'.join(unique_lines)
        cleaned_data = self.clean_text(cleaned_data)
        clean_data_dir = self.make_dir_if_not_exists(f"{self.content_path}")
        with open(os.path.join(clean_data_dir, output_filename), 'w', encoding='utf-8') as file:
            file.write(cleaned_data)

    def make_dir_if_not_exists(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path
