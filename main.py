from flask import Flask, request, render_template, session
from handler import Handler
from text_extractor import content_extractor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = '1bd9436-5a5d-4f16-92a0-4ef938555d33-nini-poop-me'

# this renderes the chatbot interface
@app.route("/")
def hello():
    return render_template("index.html")

# this endpoint starts the web scrapper
@app.route('/start/scrapper/', methods=['GET'])
async def scrap_data():
    res, status = await Handler().scrap_data(request)
    return res, status

# this endpoint starts cleans the scrapped data
@app.route('/clean/data/', methods=['GET'])
async def clean_data():
    res, status = await Handler().clean_data()
    return res, status

# this endpoint extracts text content from raw documents
@app.route('/extract/data/', methods=['GET'])
async def extract_data():
    content_extractor()
    return ('Content extracted successfully'
            , 200)


# this endpint clears session and chats
@app.route('/hey/suki/clear', methods=['GET'])
async def clear_suki():
    session.clear()
    return '', 200


# this endpint accepts documnets uploaed by user
@app.route('/suki/upload', methods=['POST'])
async def upload_document():
   res, status = await Handler().upload_file(request, app)
   return res, status

# main entry point for Suki chat
@app.route('/hey/suki', methods=['POST'])
async def suki():
    res, status = await Handler().user_flow(request)
    return res, status


if __name__ == "__main__":
    app.run(debug=True)
