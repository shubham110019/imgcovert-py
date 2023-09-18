from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from rembg import remove
from PIL import Image
import os
import base64
from io import BytesIO
import concurrent.futures

bg_remove_bp = Blueprint('bg_remove', __name__)

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

        response_data = {
            'oldimage': oldpreview,
            'preview': download_link,
            'downloadlink': download_link,
            'format': 'webp',
            'image_size': {
                'width': image_width,
                'height': image_height
            }
        }

        return jsonify(response_data)

    except Exception as e:
        return str(e), 400
