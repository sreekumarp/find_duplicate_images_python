import os
import cv2
import numpy as np
import torch

# Load YOLO model
MODEL_PATH = "D:\\Projects\\face_sorter\\yolov5s.pt"  # Pre-trained YOLOv5 model (download from official source)
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH)

def detect_yellow_shirt_with_kid(image_path):
    # Load image
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Perform detection
    results = model(image_rgb)
    detections = results.xyxy[0].cpu().numpy()

    # Filter results for people
    people = []
    kids = []
    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        if int(cls) == 0:  # Class 0 in YOLOv5 is typically "person"
            person_roi = image[int(y1):int(y2), int(x1):int(x2)]
            if is_wearing_yellow(person_roi):
                people.append((x1, y1, x2, y2))
        elif int(cls) == 1:  # Assume class 1 is "child" (adjust based on the model's labels)
            kids.append((x1, y1, x2, y2))

    # Check proximity between detected people and kids
    for person in people:
        px1, py1, px2, py2 = person
        for kid in kids:
            kx1, ky1, kx2, ky2 = kid
            if is_near(px1, py1, px2, py2, kx1, ky1, kx2, ky2):
                return f"Person with a yellow shirt and a kid detected: {person}, {kid}"

    return "No person with a yellow shirt and a kid detected."

def is_wearing_yellow(roi):
    # Convert ROI to HSV and detect yellow regions
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    yellow_lower = np.array([20, 100, 100])  # Adjust thresholds as needed
    yellow_upper = np.array([30, 255, 255])
    mask = cv2.inRange(hsv_roi, yellow_lower, yellow_upper)
    return cv2.countNonZero(mask) > 500  # Threshold for significant yellow presence

def is_near(px1, py1, px2, py2, kx1, ky1, kx2, ky2):
    # Check if bounding boxes are close enough
    person_center = ((px1 + px2) / 2, (py1 + py2) / 2)
    kid_center = ((kx1 + kx2) / 2, (ky1 + ky2) / 2)
    distance = np.sqrt((person_center[0] - kid_center[0])**2 + (person_center[1] - kid_center[1])**2)
    return distance < 100  # Adjust proximity threshold as needed

def process_folder(folder_path):
    valid_extensions = (".jpg", ".jpeg")
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(valid_extensions) and not file.lower().endswith(".xxjpg"):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                result = detect_yellow_shirt_with_kid(file_path)
                print(result)
                
SOURCE_DIR = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\check\\"
# Example usage
folder_path = SOURCE_DIR # Replace with the path to your folder
process_folder(folder_path)
