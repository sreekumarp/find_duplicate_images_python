import os
import cv2
import numpy as np
import shutil
import torch

# Load YOLO model
MODEL_PATH = "D:\\Projects\\face_sorter\\yolov5s.pt"  # Pre-trained YOLOv5 model (download from official source)
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH)

def detect_yellow_shirt(image_path):
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Warning: Failed to load image {image_path}. Skipping...")
            return False

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Perform detection
        results = model(image_rgb)
        detections = results.xyxy[0].cpu().numpy()

        # Filter results for people
        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            if int(cls) == 0:  # Class 0 in YOLOv5 is typically "person"
                # Extract the upper body region (top half of the bounding box)
                person_roi = image[int(y1):int(y1 + (y2 - y1) / 2), int(x1):int(x2)]
                if is_wearing_yellow(person_roi):
                    return True  # Yellow shirt detected
        return False  # No yellow shirt detected
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

def is_wearing_yellow(roi):
    try:
        if roi is None or roi.size == 0:
            return False

        # Convert ROI to HSV
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Define yellow color range
        yellow_lower = np.array([20, 100, 100])  # Lower bound of yellow in HSV
        yellow_upper = np.array([30, 255, 255])  # Upper bound of yellow in HSV
        
        # Create a mask for yellow regions
        mask = cv2.inRange(hsv_roi, yellow_lower, yellow_upper)
        
        # Check if the yellow area is significant
        yellow_pixels = cv2.countNonZero(mask)
        roi_area = roi.shape[0] * roi.shape[1]
        yellow_ratio = yellow_pixels / roi_area if roi_area > 0 else 0

        # Consider it a match if >20% of the area is yellow
        return yellow_ratio > 0.2
    except Exception as e:
        print(f"Error detecting yellow in ROI: {e}")
        return False

def process_folder(folder_path):
    valid_extensions = (".jpg", ".jpeg")
    found_folder = os.path.join(folder_path, "found_images")
    os.makedirs(found_folder, exist_ok=True)

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(valid_extensions) and not file.lower().endswith(".xxjpg"):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                try:
                    if detect_yellow_shirt(file_path):
                        print(f"Yellow shirt detected: {file_path}")
                        # Move the file to the "found_images" folder
                        shutil.copy(file_path, os.path.join(found_folder, file))
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")


SOURCE_DIR = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\Processed1\\"
# Example usage
folder_path = SOURCE_DIR # Replace with the path to your folder
process_folder(folder_path)
