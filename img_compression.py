from flask import Flask, request, jsonify, make_response, Blueprint
from PIL import Image
import io
import base64
import datetime
import math

img_compression_bp = Blueprint('img_compression', __name__)

@img_compression_bp.route('/imgcompress', methods=['POST'])
def compress_images():
    compress = []

    try:
        files = request.files.getlist('image')
        quality = int(request.form.get('quality', 70))  # Set default quality to 70

        for file in files:
            image = Image.open(file)

            # Determine the format of the uploaded image
            image_format = image.format

            # Compress the image
            output_io = io.BytesIO()
            image.save(output_io, format=image_format, quality=quality)
            output_io.seek(0)

            # Encode the compressed image to base64
            encoded_image = base64.b64encode(output_io.getvalue()).decode('utf-8')

            download_link = f'data:image/{image_format};base64,{encoded_image}'


            image_size = get_human_readable_size(output_io.getbuffer().nbytes)
            compression_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            compress.append({
                # 'image': encoded_image,
                'size': image_size,
                'quality': quality,
                'date': compression_date,
                'format': image_format,
                'downloadlink':download_link,
                'preview':download_link,
            })

        return jsonify({'compress': compress})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def get_human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    size = round(size_bytes / math.pow(1024, i), 2)
    return f"{size:.2f} {size_names[i]}"
