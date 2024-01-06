import onnxruntime as ort
import cv2
import numpy as np
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os
from glob import glob
import shutil
import zipfile

# Define model and providers
pic_form = ['.jpeg', '.jpg', '.png', '.JPEG', '.JPG', '.PNG']
device_name = ort.get_device()



if device_name == 'CPU':
    providers = ['CPUExecutionProvider']
elif device_name == 'GPU':
    providers = ['CUDAExecutionProvider']

# Load model AnimeGANv3_Hayao_STYLE_36.onnx
model = 'AnimeGANv3_Hayao_STYLE_36'
session = ort.InferenceSession(f'{model}.onnx', providers=providers)

# Define functions
def process_image(img, x8=True):
    h, w = img.shape[:2]
    if x8: # resize image to multiple of 32s
        def to_8s(x):
            return 256 if x < 256 else x - x%8
        img = cv2.resize(img, (to_8s(w), to_8s(h)))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)/ 127.5 - 1.0
    return img

def load_test_data(image_path):
    img0 = cv2.imread(image_path)
    img = process_image(img0)
    img = np.expand_dims(img, axis=0)
    return img, img0.shape[:2]


def Convert(img, scale):
    x = session.get_inputs()[0].name
    y = session.get_outputs()[0].name
    fake_img = session.run(None, {x : img})[0]
    images = (np.squeeze(fake_img) + 1.) / 2 * 255
    images = np.clip(images, 0, 255).astype(np.uint8)
    output_image = cv2.resize(images, (scale[1],scale[0]))
    return cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR)

# Setup directories
in_dir = 'output_frames'  # Change this to your input folder path
out_dir = 'output_frames_style'  # Change this to your output folder path

# Function to process images
def process():
    os.makedirs(out_dir, exist_ok=True)
    
    in_files = sorted(glob(f'{in_dir}/*'))
    in_files = [x for x in in_files if os.path.splitext(x)[-1].lower() in pic_form]

    for ims in tqdm(in_files):
        out_name = f"{out_dir}/{os.path.basename(ims).split('.')[0]}_styled.jpg"
        mat, scale = load_test_data(ims)
        res = Convert(mat, scale)
        cv2.imwrite(out_name, res)

    print(f"\nConversion completed. Styled images are saved in {out_dir}\n")

# Main function
if __name__ == "__main__":
    process()
    # print(device_name)