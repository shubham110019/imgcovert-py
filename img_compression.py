from flask import Flask, request, jsonify, make_response, Blueprint
from PIL import Image
import io
import base64
import datetime
import math

img_compression_bp = Blueprint('img_compression', __name__)

@img_compression_bp.route('/imgcompress', methods=['POST'])
def compress_images():
    compressed_images = []

    try:
        files = request.files.getlist('image')
        quality = int(request.form.get('quality', 70))  # Set default quality to 70

        for file in files:
            image = Image.open(file)

            # Compress the image
            output_io = io.BytesIO()
            image.save(output_io, format='JPEG', quality=quality)
            output_io.seek(0)

            # Encode the compressed image to base64
            encoded_image = base64.b64encode(output_io.getvalue()).decode('utf-8')


            image_size = get_human_readable_size(output_io.getbuffer().nbytes)
            compression_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            compressed_images.append({
                'image': encoded_image,
                'size': image_size,
                'quality': quality,
                'date': compression_date,
            })

        return jsonify({'compressed_images': compressed_images})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
