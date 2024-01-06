import os
import re
from PIL import Image
from fpdf import FPDF

# Directory containing images
image_folder = 'output_frames_sub'

# Custom sort function to extract scene number from filename
def sort_key_func(file_path):
    # Use a regular expression to find numbers after 'scene_'
    numbers = re.findall(r'scene_(\d+)', file_path)
    return int(numbers[0]) if numbers else 0

# List of image paths
image_files = [os.path.join(image_folder, image) for image in os.listdir(image_folder) if image.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

# Sort the images by name or any other criteria
image_files.sort(key=sort_key_func)

# Initialize PDF
pdf = FPDF(orientation='L')  # 'L' for Landscape orientation

# Add images to PDF
for image_path in image_files:
    image = Image.open(image_path)
    
    # Convert image mode to RGB if it's not (required for colored images)
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Get image dimensions
    width, height = image.size
    
    # Define PDF width and height
    pdf_width = 297  # A4 landscape width in mm
    pdf_height = 210  # A4 landscape height in mm
    
    # Calculate width and height ratio
    width_ratio = pdf_width / width
    height_ratio = pdf_height / height
    scale = min(width_ratio, height_ratio)
    
    # Scale image dimensions
    new_width = width * scale
    new_height = height * scale
    
    # Add page with custom size
    pdf.add_page()
    pdf.set_auto_page_break(0, margin=0)

    # Add image to page
    pdf.image(image_path, x=(pdf_width - new_width) / 2, y=(pdf_height - new_height) / 2, w=new_width, h=new_height)

# Save the result
pdf.output("output/comic.pdf")

print("PDF created successfully!")