import os
import cv2
import numpy as np
import shutil
import torch

# Load YOLO model
MODEL_PATH = "D:\\Projects\\face_sorter\\yolov5s.pt"  # Pre-trained YOLOv5 model (download from official source)
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH)

def detect_yellow_shirt(image_path):
    # Load image
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Perform detection
    results = model(image_rgb)
    detections = results.xyxy[0].cpu().numpy()

    # Filter results for people
    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        if int(cls) == 0:  # Class 0 in YOLOv5 is typically "person"
            person_roi = image[int(y1):int(y2), int(x1):int(x2)]
            if is_wearing_yellow(person_roi):
                return True  # Yellow shirt person detected
    return False  # No yellow shirt detected

def is_wearing_yellow(roi):
    # Convert ROI to HSV and detect yellow regions
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    yellow_lower = np.array([20, 100, 100])  # Adjust thresholds as needed
    yellow_upper = np.array([30, 255, 255])
    mask = cv2.inRange(hsv_roi, yellow_lower, yellow_upper)
    return cv2.countNonZero(mask) > 500  # Threshold for significant yellow presence

def process_folder(folder_path):
    valid_extensions = (".jpg", ".jpeg")
    found_folder = os.path.join(folder_path, "found_images")
    os.makedirs(found_folder, exist_ok=True)

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(valid_extensions) and not file.lower().endswith(".xxjpg"):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                if detect_yellow_shirt(file_path):
                    print(f"Match found: {file_path}")
                    # Move the file to the "found_images" folder
                    shutil.move(file_path, os.path.join(found_folder, file))

SOURCE_DIR = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\check\\"
# Example usage
folder_path = SOURCE_DIR # Replace with the path to your folder

process_folder(folder_path)
