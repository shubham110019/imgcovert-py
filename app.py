from flask import Flask, request, render_template, jsonify, make_response
from flask_cors import CORS  # Import the CORS module
from image_conversion import image_conversion_bp
from img_to_pdf import img_to_pdf_bp
from img_compression import img_compression_bp
from csv_file import csv_file_bp
from bg_remove import bg_remove_bp
import json  # Import the json module

app = Flask(__name__)
CORS(app)

# Define the path to the main JSON file
MAIN_JSON_FILE = './api_data/data_api.json'


# Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

@app.route('/')
def upload_page():
    return render_template('index.html')


# Register the blueprints
app.register_blueprint(image_conversion_bp)
app.register_blueprint(img_to_pdf_bp)
app.register_blueprint(img_compression_bp)
app.register_blueprint(csv_file_bp)
app.register_blueprint(bg_remove_bp)

@app.route('/api/bgdata', methods=['GET'])
def api_data():
    try:
        with open(MAIN_JSON_FILE, 'r') as json_file:
            data = json.load(json_file)
        return jsonify(data)
    except Exception as e:
        return str(e), 400

def get_human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    size = round(size_bytes / math.pow(1024, i), 2)
    return f"{size:.2f} {size_names[i]}"

if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0')
