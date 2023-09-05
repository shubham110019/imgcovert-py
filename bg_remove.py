from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from rembg import remove
from PIL import Image
import os
import base64
from io import BytesIO

bg_remove_bp = Blueprint('bg_remove', __name__)

@bg_remove_bp.route('/remove_bg', methods=['POST'])
def api_remove_background():
    try:
        if 'image' not in request.files:
            return 'No image provided', 400

        input_image = request.files['image']

        if input_image.filename == '':
            return 'No selected image file', 400

        # Perform background removal
        output_image = remove_background(input_image)

        # Convert the output image to base64
        buffered = BytesIO()
        output_image.save(buffered, format="PNG")
        result_image_base64 = base64.b64encode(buffered.getvalue()).decode()

        download_link = f'data:image/png;base64,{result_image_base64}'

        response_data = {
            'preview': download_link,
            'downloadlink': download_link,
            'format': 'png',
        }

        return jsonify(response_data)

    except Exception as e:
        return str(e), 400

def remove_background(input_image):
    with Image.open(input_image) as img:
        output = remove(img)
        return output
