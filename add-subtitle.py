import os
import re
import cv2


def parse_srt(srt_file_path):
    with open(srt_file_path, 'r') as file:
        srt_content = file.read()
    
    # Regular expression for parsing .srt files
    pattern = re.compile(r'\d+\n(\d{2}:\d{2}:\d{2}),\d{3} --> (\d{2}:\d{2}:\d{2}),\d{3}\n(.+?)(?:\n\n|\Z)', re.DOTALL)
    subtitles = []
    
    for match in pattern.finditer(srt_content):
        start_time = match.group(1)
        end_time = match.group(2)
        text = match.group(3).replace('\n', ' ')  # Replace newlines with spaces
        # Remove HTML-like tags from the text
        text = re.sub(r'<[^>]+>', '', text)
        # Split the text at ' - ' to create a list of lines
        text_lines = text.split('-')
        # Filter out any empty strings from the list of text lines
        text_lines = [line for line in text_lines if line.strip()]
        subtitles.append((start_time, end_time, text_lines))
        
    return subtitles


def add_subtitle_to_image(image_path, subtitles, output_dir):
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Error: Could not open image: {image_path}")
        return
    
    # Get the timestamp of the image
    image_timestamp = get_image_timestamp(image_path)
    
    # Find the subtitle to display based on the image timestamp
    subtitle_found = False
    for start_time, end_time, text_lines in subtitles:
        if start_time <= image_timestamp <= end_time:
            # Draw the subtitle on the image
            draw_text(frame, text_lines)
            subtitle_found = True
            break
    
    if not subtitle_found:
        print(f"No subtitle found for image: {image_path}")

    # Save the frame with or without subtitle in the output directory
    save_frame(frame, image_path, output_dir)

def draw_text(frame, text_lines):
    # Define the text properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4
    font_color = (255, 255, 255)  # White color
    line_type = 2
    line_spacing = 30  # Adjust line spacing as needed

    # Filter out any empty strings from the list of text lines
    text_lines = [line for line in text_lines if line]

    # Starting Y position from the bottom of the image
    text_y_start = frame.shape[0] - 10

    # Draw each line of text
    for i, line in enumerate(reversed(text_lines)):
        # Calculate position for each line of text
        text_size = cv2.getTextSize(line, font, font_scale, line_type)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = text_y_start - i * (text_size[1] + line_spacing)

        # Add each line of subtitle to the frame
        cv2.putText(frame, line, (text_x, text_y), font, font_scale, font_color, line_type)



def save_frame(frame, image_path, output_dir):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save the frame with subtitle in the output directory
    output_image_path = os.path.join(output_dir, os.path.basename(image_path))
    cv2.imwrite(output_image_path, frame)
    

def get_image_timestamp(image_path):
    # Extract the filename without extension
    filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Split the filename to get the part with the timestamp
    _, timestamp_part = filename.split('_start-')
    
    # Replace dashes with colons and the last dash with a comma to match SRT format
    timestamp = timestamp_part.replace('-', ':', 2).replace('-', ',', 1)
    
    return timestamp


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