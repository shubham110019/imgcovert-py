from flask import Flask, request, jsonify, make_response, Blueprint
from PIL import Image as PILImage
from fpdf import FPDF
import io
import datetime
import base64
import math

img_to_pdf_bp = Blueprint('img_to_pdf', __name__)

@img_to_pdf_bp.route('/imgtopdf', methods=['POST'])
def convert_to_pdf():
    try:
        # Get the uploaded images, selected orientation, and page size
        files = request.files.getlist('image')
        orientation = request.form.get('orientation', 'portrait')
        page_size = request.form.get('page_size', 'A4')  # Default to A4 size

        # Define a dictionary of page sizes with their dimensions
        page_sizes = {
            'A4': (210, 297),
            'Letter': (216, 279),
            'Legal': (216, 356),
            'A3': (297, 420),  # Add A3 size
            'B5': (176, 250),  # Add B5 size
            'Fit': None 
            # Add more page sizes as needed
        }

        # Initialize the PDF object
        selected_page_size = page_sizes.get(page_size, None)
        if selected_page_size:
            pdf = FPDF(orientation=orientation, unit='mm', format=selected_page_size)
        else:
            pdf = FPDF(orientation=orientation, unit='mm')

        # Create a list to hold PDF information
        pdf_urls = []  # Changed to hold URLs

        # Loop through each image and add it to a new page in the PDF
        for file in files:
            image = PILImage.open(file)
            img_width, img_height = image.size

            # Calculate the width and height to fit within the page
            pdf_width = pdf.w - (pdf.l_margin + pdf.r_margin)
            pdf_height = pdf.h - (pdf.t_margin + pdf.b_margin)

            # Calculate the aspect ratio
            aspect_ratio = img_width / img_height

            # Determine whether to fit image width-wise or height-wise
            if aspect_ratio >= 1:
                width = pdf_width
                height = pdf_width / aspect_ratio
            else:
                width = pdf_height * aspect_ratio
                height = pdf_height

            # Add a page to the PDF
            pdf.add_page()

            # Calculate the coordinates to center the image
            x = (pdf.w - width) / 2
            y = (pdf.h - height) / 2

            # Add the image to the PDF
            pdf.image(file, x=x, y=y, w=width, h=height)

        # Create a PDF buffer to store the converted PDF
        pdf_io = io.BytesIO()
        pdf.output(pdf_io)

        # Get the size of the PDF
        pdf_size_bytes = len(pdf_io.getvalue())
        pdf_size = get_human_readable_size(pdf_size_bytes)

        # Get the current date and time as a string
        creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create a response with the PDF data
        response = make_response(pdf_io.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=converted_images.pdf'
        response.headers['Content-Type'] = 'application/pdf'

        # Convert the binary PDF data to base64
        pdf_base64 = base64.b64encode(pdf_io.getvalue()).decode("utf-8")

        # Create a data URL with the base64-encoded PDF
        pdf_url = f'data:application/pdf;base64,{pdf_base64}'  # This simulates the URL.createObjectURL behavior

        pdf_urls.append({
            'pdf_links': pdf_url,  # Send the list of PDF URLs
            'pdf_size': pdf_size,
            'creation_date': creation_date,
        })

        return jsonify({'pdf': pdf_urls})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    

def get_human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    size = round(size_bytes / math.pow(1024, i), 2)
    return f"{size:.2f} {size_names[i]}"
