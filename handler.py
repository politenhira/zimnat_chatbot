from web_scrapper import WebScraper
from data_cleaner import TextCleaner
from onboarding import UserFlow
from flask import jsonify
from document_analyzer import Utility
import os


class Handler:
    async def scrap_data(self, request):
        try:
            base_url = os.getenv("WEBSITE_URL")
            web_scraper = WebScraper(base_url)
            web_scraper.crawl_and_scrape()
            return jsonify({"msg": "Done scrapping the website..."}), 200
        except Exception as e:
            print(e)
            return jsonify({'error': 'An error occurred while scrapping and crawling the website'}), 500

    async def clean_data(self):
        try:
            dirty_data_file = os.getenv("SCRAP_DATA_FILE")
            clean_data_file = os.getenv("CLEAN_DATA_FILE")
            content_directory = os.getenv("CONTENT_RAW_DIR")
            # clean text
            text_cleaner = TextCleaner(content_directory)
            # # Process text file
            text_cleaner.process_text_file(dirty_data_file, clean_data_file)
            return jsonify({"msg": "Done cleaning the raw_data..."}), 200
        except Exception as e:
            return jsonify({'error': 'An error occurred while cleaning the raw_data'}), 500

    async def user_flow(self, request):
        try:
            flow = UserFlow()
            input = request.json['input']
            response = await flow.process(user_input=input)
            return jsonify({"response": response}), 200
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failing to determine where we are lets do this again'})
    
    async def upload_file(self, request, app):
        try:
            if 'file' not in request.files:
                return jsonify({'message': 'No file part found, please try again!'}), 400
    
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'message': 'No selected file, please try again!'}), 400
            
            if file:
                filename = file.filename
                upload_folder = os.path.join(app.root_path, 'uploads')
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                return jsonify({'message': 'Document received successfully🫡, I will analyze the document and notify you the results.'}), 200
        except Exception as e:
            return jsonify({'message': 'An error occurred while uploading the file'}), 500
        
        
    async def process_document(self, filename):
        filepath = "uploads/" + filename
        vectorpath = "uploads/vectors"
        utility = Utility(filepath=filepath, vectorpath=vectorpath, filename=filename)
        response = await utility.answer()
        print(response)
        return str(response)
