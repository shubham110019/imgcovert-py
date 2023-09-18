from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from rembg import remove
from PIL import Image
import os
import base64
from io import BytesIO
import concurrent.futures
import json
import time
import uuid  # Import the uuid module

bg_remove_bp = Blueprint('bg_remove', __name__)

# Directory to save JSON file
SAVE_DIR = 'api_data'

# Create the directory if it doesn't exist
os.makedirs(SAVE_DIR, exist_ok=True)

# Path to the main JSON file
MAIN_JSON_FILE = os.path.join(SAVE_DIR, 'data_api.json')

# Function to save the date, website domain name, and unique ID to the main JSON file
def save_data_to_json(unique_id, upload_date, website_domain):
    data = {
        'id': unique_id,
        'upload_date': upload_date,
        'website_domain': website_domain
    }

    # Load existing data or initialize with an empty list
    existing_data = []

    if os.path.exists(MAIN_JSON_FILE):
        try:
            with open(MAIN_JSON_FILE, 'r') as json_file:
                existing_data = json.load(json_file)
        except json.JSONDecodeError:
            # Handle the case where the file is not valid JSON
            pass

    existing_data.append(data)  # Append the new data to the list

    with open(MAIN_JSON_FILE, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

# Create the main JSON file if it doesn't exist
if not os.path.exists(MAIN_JSON_FILE):
    with open(MAIN_JSON_FILE, 'w') as json_file:
        json.dump([], json_file)

# Route to upload and convert WebP image, remove the background, and send to users
@bg_remove_bp.route('/remove_bg', methods=['POST'])
def api_remove_background():
    try:
        if 'image' not in request.files:
            return 'No image provided', 400

        input_image = request.files['image']

        if input_image.filename == '':
            return 'No selected image file', 400

        # Convert the original WebP image to base64
        original_image_base64 = base64.b64encode(input_image.read()).decode()

        # Convert the WebP image to a format that PIL can handle (e.g., PNG)
        input_image_pil = Image.open(input_image)
        input_image_pil = input_image_pil.convert("RGBA")

        # Get the size (width and height) of the uploaded image
        image_width, image_height = input_image_pil.size

        # Define a function for background removal
        def remove_background(input_image_pil):
            return remove(input_image_pil)

        # Use concurrent.futures for parallel processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            output_image = executor.submit(remove_background, input_image_pil).result()

        # Convert the processed image to WebP format
        buffered = BytesIO()
        output_image.save(buffered, format="WebP")
        result_image_base64 = base64.b64encode(buffered.getvalue()).decode()

        download_link = f'data:image/webp;base64,{result_image_base64}'

        oldpreview = f'data:image/png;base64,{original_image_base64}'

        # Extract the website domain name from the request URL
        website_domain = request.url_root

        # Generate a unique ID
        unique_id = str(uuid.uuid4())

        # Create a dictionary containing the response data
        response_data = {
            'id': unique_id,
            'upload_date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'oldimage': oldpreview,
            'preview': download_link,
            'downloadlink': download_link,
            'format': 'webp',
            'image_size': {
                'width': image_width,
                'height': image_height
            }
        }

        # Save the data to the main JSON file
        save_data_to_json(unique_id, response_data['upload_date'], website_domain)

        return jsonify(response_data)

    except Exception as e:
        return str(e), 400
