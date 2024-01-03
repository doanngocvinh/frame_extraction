import os
import re
import cv2

def parse_srt(srt_file_path):
    with open(srt_file_path, 'r') as file:
        srt_content = file.read()
    
    # Regular expression for parsing .srt files
    pattern = re.compile(r'\d+\n(\d{2}:\d{2}:\d{2}),\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n(.+?)(?:\n\n|\Z)', re.DOTALL)
    subtitles = []
    
    for match in pattern.finditer(srt_content):
        start_time = match.group(1)
        text = match.group(2).replace('\n', ' ')  # Replace newlines with spaces
        # Remove HTML-like tags from the text
        text = re.sub(r'<[^>]+>', '', text)
        # Insert a newline before ' - '
        text = text.replace(' - ', '\n - ')
        subtitles.append((start_time, text))
        
    return subtitles

def add_subtitle_to_image(image_path, text, output_dir):
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Error: Could not open image: {image_path}")
        return
    
    # Define the text properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_color = (255, 255, 255)  # White color
    line_type = 2
    # Calculate the position for the text to be at the bottom center of the frame
    text_size = cv2.getTextSize(text, font, font_scale, line_type)[0]
    text_x = (frame.shape[1] - text_size[0]) // 2
    text_y = frame.shape[0] - 10

    # Add subtitle to the frame
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, font_color, line_type)

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the frame with subtitle in the output directory
    output_image_path = os.path.join(output_dir, os.path.basename(image_path))
    cv2.imwrite(output_image_path, frame)

# Paths
subtitle_file_path = 'data\Episode01.srt'
frames_dir = 'output_frames'
output_frames_sub_dir = 'output_frames_sub'  # Directory for frames with subtitles

# Parse the SRT file
subtitles = parse_srt(subtitle_file_path)

# Process each frame with the updated parse_srt function
for image_name in os.listdir(frames_dir):
    image_path = os.path.join(frames_dir, image_name)
    
    # Extract start time from the image name
    start_time_match = re.search(r'(\d{2}-\d{2}-\d{2}-\d{3})', image_name)
    if start_time_match:
        start_time = start_time_match.group(1).replace('-', ':')
        start_time = start_time[:-4] + ',' + start_time[-3:]  # Convert to SRT format
        
        # Find the matching subtitle
        for subtitle_start_time, subtitle_text in subtitles:
            if start_time.startswith(subtitle_start_time):
                add_subtitle_to_image(image_path, subtitle_text, output_frames_sub_dir)
                break