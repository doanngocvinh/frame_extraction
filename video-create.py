import cv2
import os
import re
from glob import glob

# Parameters
image_folder = 'output_frames_sub'  # Replace with your image folder path
video_name = 'output/3-fps.avi'  # Name of the resulting video file
frame_rate = 3  # Frames per second

# Custom sort function to extract scene number from filename
def sort_key_func(file_path):
    # Use a regular expression to find numbers after 'scene_'
    numbers = re.findall(r'scene_(\d+)', file_path)
    return int(numbers[0]) if numbers else 0

# List of image paths
image_files = [os.path.join(image_folder, image) for image in os.listdir(image_folder) if image.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

# Sort the images by name or any other criteria
image_files.sort(key=sort_key_func)

# Obtain the dimensions of the first image (assuming all images have the same dimensions)
frame = cv2.imread(image_files[0])
height, width, layers = frame.shape
size = (width, height)

# Initialize the video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can use 'MP4V' for .mp4 output
video_writer = cv2.VideoWriter(video_name, fourcc, frame_rate, size)

# Loop through each image and write it as a video frame
for image_file in image_files:
    frame = cv2.imread(image_file)
    video_writer.write(frame)

# Release the video writer
video_writer.release()