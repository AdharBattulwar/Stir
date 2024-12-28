from flask import Flask, jsonify, render_template
from main import run_selenium_script  # Import the function from main.py
from pymongo import MongoClient
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# MongoDB setup
MongoDbURI = os.getenv("MONGODB_URI")
client = MongoClient(MongoDbURI)
db = client['Stir']
collection = db['trends']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    # Call the Selenium script function
    result = run_selenium_script()

    if result:
        # Convert ObjectId to string if necessary
        result['_id'] = str(result['_id'])

        # Prepare data for response
        response = {
            'date_time': result['date_time'],
            'trends': result['trend_names'],
            'ip_address': result['ip_address'],
            'mongo_record': result
        }
    else:
        response = {
            'date_time': datetime.datetime.utcnow(),
            'trends': [],
            'ip_address': 'N/A',
            'mongo_record': {}
        }
    
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)