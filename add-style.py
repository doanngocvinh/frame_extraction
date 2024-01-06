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
    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']

# Load model
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
in_dir = 'out_frames'
out_dir = 'out_frames_style'

# Function to process images
def process():
    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

    if len(file_paths) == 0:
        print('\nNo files were selected. Try again..\n')
        return

    for f in file_paths:
        shutil.copy(f, in_dir)

    in_files = sorted(glob(f'{in_dir}/*'))
    in_files = [x for x in in_files if os.path.splitext(x)[-1].lower() in pic_form]

    for ims in tqdm(in_files):
        out_name = f"{out_dir}/{os.path.basename(ims).split('.')[0]}.jpg"
        mat, scale = load_test_data(ims)
        res = Convert(mat, scale)
        cv2.imwrite(out_name, res)
        cv2.imshow('Result Picture', res)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Compress the output results into a zip file
    with zipfile.ZipFile(f"{out_dir}.zip", 'w') as zipf:
        for root, dirs, files in os.walk(out_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(out_dir, '..')))

    print(f"\nResults are saved and zipped in {out_dir}.zip\n")

# Main function
if __name__ == "__main__":
    print('\nSelect some photos to upload\n')
    process()