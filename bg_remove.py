from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from rembg import remove
from PIL import Image
import os
import base64
from io import BytesIO

bg_remove_bp = Blueprint('bg_remove', __name__)

# Route to upload and convert CSV to JSON
@bg_remove_bp.route('/remove_bg', methods=['POST'])
def api_remove_background():
    try:
        if 'image' not in request.files:
            return 'No image provided', 400

        input_image = request.files['image']

        if input_image.filename == '':
            return 'No selected image file', 400

        # Check if the file type is allowed (e.g., JPEG, PNG)
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        if '.' not in input_image.filename or input_image.filename.split('.')[-1].lower() not in allowed_extensions:
            return 'Invalid file type. Only JPEG and PNG are supported.', 400

        # Process the image
        output_image = remove_background(input_image)

        # Convert the processed image to base64
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
        # Log the exception for debugging
        print(str(e))
        return 'An error occurred while processing the image', 500
    
# Function to remove background from an image
def remove_background(input_image):
    with Image.open(input_image) as img:
        output = remove(img)
        return output

if __name__ == '__main__':
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(bg_remove_bp)
    app.run(host='0.0.0.0', port=5000)  # Use a production-ready server like Gunicorn in a production environment.
