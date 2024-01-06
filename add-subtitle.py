import os
import re
import cv2
from PIL import Image, ImageDraw, ImageFont


def parse_srt(srt_file_path):
    with open(srt_file_path, 'r') as file:
        srt_content = file.read()

    pattern = re.compile(r'\d+\n(\d{2}:\d{2}:\d{2}),\d{3} --> (\d{2}:\d{2}:\d{2}),\d{3}\n(.+?)(?:\n\n|\Z)', re.DOTALL)
    subtitles = []

    for match in pattern.finditer(srt_content):
        start_time = match.group(1)
        end_time = match.group(2)
        text = match.group(3).replace('\n', ' ')  # Replace newlines with spaces
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML-like tags
        text_lines = text.split(' - ')
        text_lines = [line.strip() for line in text_lines if line.strip()]
        subtitles.append((start_time, end_time, text_lines))

    return subtitles


def add_subtitle_to_image(image_path, subtitles, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Error: Could not open image: {image_path}")
        return

    output_image_path = os.path.join(output_dir, os.path.basename(image_path))
    image_timestamp = get_image_timestamp(image_path)

    for start_time, end_time, text_lines in subtitles:
        if start_time <= image_timestamp <= end_time:
            draw_text_with_pillow(image_path, text_lines, output_image_path)
            break
    else:
        print(f"No subtitle found for image: {image_path}")
        save_frame(image_path, output_image_path)

    

def draw_text_with_pillow(image_path, text_lines, output_image_path):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font_color = (255, 255, 255)
    font_path = "FreeMono.ttf"  # Replace with the path to your font file
    font_size = 13
    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    text_y_start = image.size[1] - 32

    line_spacing = 5
    for i, line in enumerate(reversed(text_lines)):
        text_width = draw.textlength(line.strip(), font=font)
        text_x = (image.size[0] - text_width) / 2
        text_y = text_y_start - (i * (font_size + line_spacing))
        draw.text((text_x, text_y), line.strip(), font=font, fill=font_color)
    
    image.save(output_image_path)


# Function to extract timestamp from the image filename should be defined here
def get_image_timestamp(image_path):

    # Extract the filename without extension
    filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Assuming the filename is in the format "frame_start-HH-MM-SS-sss",
    # where HH is hours, MM is minutes, SS is seconds, and sss is milliseconds
    try:
        _, timestamp_part = filename.split('_start-')
        timestamp = timestamp_part.replace('-', ':', 2).replace('-', ',', 1)
        return timestamp
    except ValueError:
        raise ValueError(f"Filename does not contain a valid timestamp: {filename}")

# Function to save the frame might look like this
def save_frame(image_path, output_image_path):
    image = Image.open(image_path)
    image.save(output_image_path)

if __name__ == "__main__":
    # Paths
    subtitle_file_path = 'data\Episode01.srt'
    frames_dir = 'output_frames_style'
    output_frames_sub_dir = 'output_frames_sub'  # Directory for frames with subtitles

    # Parse the SRT file
    subtitles = parse_srt(subtitle_file_path)

    # Process each frame with the updated parse_srt function
    for image_name in os.listdir(frames_dir):
        image_path = os.path.join(frames_dir, image_name)
        
        # Add subtitle to the image and save the results
        add_subtitle_to_image(image_path, subtitles, output_frames_sub_dir)