from flask import Flask, request, render_template, jsonify
from PIL import Image
import io
import datetime
import base64
import math

app = Flask(__name__)

@app.route('/')
def upload_page():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_images():
    converted = []

    try:
        files = request.files.getlist('image')
        target_format = request.form.get('format', 'JPEG')

        for file in files:
            image = Image.open(file)

            if target_format.lower() == 'svg':
                svg_content = convert_image_to_svg(image)
                encoded_svg = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
                image_type = 'SVG'
                width_height = f"{image.width}x{image.height}"
            else:
                converted_image = convert_image_format(image, target_format)
                width, height = converted_image.size
                width_height = f"{width}x{height}"

                output_io = io.BytesIO()
                converted_image.save(output_io, format=target_format)
                output_io.seek(0)

                encoded_image = base64.b64encode(output_io.getvalue()).decode('utf-8')
                image_type = target_format

            image_size = get_human_readable_size(len(svg_content) if target_format.lower() == 'svg' else output_io.getbuffer().nbytes)

            conversion_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            converted.append({
                'image': encoded_svg if target_format.lower() == 'svg' else encoded_image,
                'size': image_size,
                'format': image_type,
                'dimensions': width_height,
                'upload_type': file.content_type,
                'date': conversion_date,
            })

        return jsonify({'converted': converted})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def convert_image_format(image, target_format):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image

def get_human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    size = round(size_bytes / math.pow(1024, i), 2)
    return f"{size:.2f} {size_names[i]}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
