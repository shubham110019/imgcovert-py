from flask import Flask, request, jsonify, Blueprint
from rembg import remove
from PIL import Image
import os
import base64
from io import BytesIO

bg_remove_bp = Blueprint('bg_remove', __name__)

# Function to convert file size to a human-readable format
def remove_background(input_image):
    with Image.open(input_image) as img:
        output = remove(img)
        return output

# Route to upload and convert CSV to JSON
@bg_remove_bp.route('/remove_bg', methods=['POST'])
def api_remove_background():
    try:
        if 'image' not in request.files:
            return 'No image provided', 400

        input_image = request.files['image']

        if input_image.filename == '':
            return 'No selected image file', 400

        # Convert the original image to base64
        original_image_base64 = base64.b64encode(input_image.read()).decode()

        # Remove background using rembg
        output_image = remove_background(input_image)

        # Convert the processed image to base64
        buffered = BytesIO()
        output_image.save(buffered, format="PNG")
        result_image_base64 = base64.b64encode(buffered.getvalue()).decode()

        download_link = f'data:image/png;base64,{result_image_base64}'

        oldpreview = f'data:image/png;base64,{original_image_base64}'

        response_data = {
            'oldimage': oldpreview,
            'preview': download_link,
            'downloadlink': download_link,
            'format': 'png',
        }

        return jsonify(response_data)

    except Exception as e:
        return str(e), 400
