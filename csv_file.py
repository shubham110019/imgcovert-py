from flask import Flask, request, jsonify, Blueprint
import csv
import json
import base64
from io import StringIO
import chardet
import os
import datetime
import math  # Import math module for size conversion

csv_file_bp = Blueprint('csv_file', __name__)

# Function to convert file size to a human-readable format
def get_human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    size = round(size_bytes / math.pow(1024, i), 2)
    return f"{size:.2f} {size_names[i]}"

# Route to upload and convert CSV to JSON
@csv_file_bp.route('/csvtojson', methods=['POST'])
def upload_csv_and_convert_to_json():
    try:
        # Check if the 'csv_file' field exists in the request
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        csv_file = request.files['csv_file']

        # Check if the file is empty
        if csv_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Check if the file is a CSV file
        if not csv_file.filename.endswith('.csv'):
            return jsonify({'error': 'Uploaded file is not a CSV'}), 400

        # Detect the encoding of the CSV file
        csv_content = csv_file.read()
        csv_encoding = chardet.detect(csv_content)['encoding']

        # Read the CSV file with the detected encoding and convert it to JSON
        csv_data = []
        with StringIO(csv_content.decode(csv_encoding)) as file_stream:
            csv_reader = csv.DictReader(file_stream)
            for row in csv_reader:
                csv_data.append(row)

        # Convert CSV data to base64
        csv_data_base64 = base64.b64encode(json.dumps({'data': csv_data}).encode('utf-8')).decode('utf-8')

        # Create a download link for the base64 data
        download_link = f'data:application/json;base64,{csv_data_base64}'

        # Calculate file size in bytes
        file_size_bytes = len(csv_content)

        # Convert file size to a human-readable format
        file_size_human_readable = get_human_readable_size(file_size_bytes)

        # Calculate the creation date
        creation_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Add creation date and file size (human-readable) to response data
        response_data = {
            'download_link': download_link,
            'creation_date': creation_date,
            'file_size_bytes': file_size_bytes,
            'file_size': file_size_human_readable,
            'format': 'json',
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
