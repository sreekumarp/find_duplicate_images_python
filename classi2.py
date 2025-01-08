import os
import shutil
from torchvision import models, transforms
from PIL import Image
import torch
import torch.nn as nn

# Define the categories
CATEGORIES = ["Document", "Screenshot", "Meme", "Photograph"]

# Ignore folder
IGNORE_FOLDER = "Error"

# Transform for input images
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Load the pre-trained AlexNet model
model = models.alexnet(pretrained=True)
model.classifier[6] = nn.Linear(4096, len(CATEGORIES))  # Update the output layer to match the number of categories
model.eval()

# Function to classify images
def classify_image(image_path, model):
    try:
        image = Image.open(image_path).convert('RGB')
        image_tensor = transform(image).unsqueeze(0)
        outputs = model(image_tensor)
        _, predicted = torch.max(outputs, 1)
        return CATEGORIES[predicted.item()]
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

# Function to create subfolders
def create_subfolders(target_dir, categories):
    for category in categories:
        category_path = os.path.join(target_dir, category)
        os.makedirs(category_path, exist_ok=True)

# Function to process images in the directory
def process_directory(source_dir, target_dir, model, categories, ignore_folder):
    total_files = sum([len(files) for r, d, files in os.walk(source_dir) if IGNORE_FOLDER not in r])
    processed_files = 0

    for root, dirs, files in os.walk(source_dir):
        # Skip the ignore folder
        if IGNORE_FOLDER in root:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")) and not file.lower().endswith((".xxjpg")):
                try:
                    print(f"Processing file: {file_path}")
                    category = classify_image(file_path, model)

                    if category:
                        category_path = os.path.join(target_dir, category)
                        os.makedirs(category_path, exist_ok=True)

                        # Move the file to the category folder
                        shutil.move(file_path, os.path.join(category_path, file))
                    
                    processed_files += 1
                    percentage_completed = (processed_files / total_files) * 100
                    print(f"Completed: {percentage_completed:.2f}%")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

        # Rename the folder as _Done after processing all files
        if not files:
            new_folder_name = root + "_Classified"
            os.rename(root, new_folder_name)

if __name__ == "__main__":
    # Directory paths
    SOURCE_DIR = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\Processed1\\"

    # Iterate through each subfolder in the source directory
    for subdir in os.listdir(SOURCE_DIR):
        subdir_path = os.path.join(SOURCE_DIR, subdir)
        if os.path.isdir(subdir_path):
            try:
                print(f"Processing folder: {subdir_path}")
                TARGET_DIR = subdir_path
                # Create subfolders in the target directory
                create_subfolders(TARGET_DIR, CATEGORIES)

                # Process images and classify them
                process_directory(subdir_path, TARGET_DIR, model, CATEGORIES, IGNORE_FOLDER)

                # Rename the folder as _Classified after processing all files
                new_folder_name = subdir_path + "_Classified"
                os.rename(subdir_path, new_folder_name)
                print(f"Finished processing folder: {subdir_path}")
            except Exception as e:
                print(f"Error processing folder {subdir_path}: {e}")
