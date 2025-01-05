import os
import hashlib
import shutil
from PIL import Image
import imagehash
from pytesseract import image_to_string
from tqdm import tqdm

# Hardcoded paths
INPUT_DIRECTORY = "F:\duplicates"  # Replace with the path to the directory you want to scan
OUTPUT_FOLDER = "F:\duplicates2"  # Replace with the path for output folder
DUPLICATES_FOLDER = os.path.join(OUTPUT_FOLDER, "Duplicates")
ERROR_FOLDER = os.path.join(OUTPUT_FOLDER, "Error")
DOCUMENT_FOLDER = os.path.join(OUTPUT_FOLDER, "Document")

def calculate_image_hash(image_path):
    """Calculate a perceptual hash for an image."""
    try:
        with Image.open(image_path) as img:
            return imagehash.average_hash(img)
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def calculate_file_hash(file_path, chunk_size=1024 * 1024):
    """Calculate a SHA256 hash for a file."""
    hash_func = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None
    return hash_func.hexdigest()

def contains_text(image_path, text_threshold=10):
    """Check if the image contains significant text content."""
    try:
        with Image.open(image_path) as img:
            text = image_to_string(img)
        # Count the number of words detected
        return len(text.strip().split()) > text_threshold
    except Exception as e:
        print(f"Error performing OCR on {image_path}: {e}")
        return False

def move_file(file_path, dest_folder):
    """Move a file to the specified destination folder."""
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    dest_path = os.path.join(dest_folder, os.path.basename(file_path))
    shutil.move(file_path, dest_path)
    print(f"Moved: {file_path} -> {dest_path}")

def find_and_categorize_files(directory, include_images=True):
    """Find duplicates and categorize files into subfolders."""
    hash_map = {}
    duplicates = []

    for root, _, files in os.walk(directory):
        for file in tqdm(files, desc="Processing files"):
            file_path = os.path.join(root, file)

            # Process images separately
            if include_images and file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                if contains_text(file_path):  # Check for text in the image
                    move_file(file_path, DOCUMENT_FOLDER)
                    continue
                
                file_hash = calculate_image_hash(file_path)
            else:
                file_hash = calculate_file_hash(file_path)

            # Handle errors during processing
            if file_hash is None:
                move_file(file_path, ERROR_FOLDER)
                continue

            # Detect duplicates
            if file_hash in hash_map:
                duplicates.append(file_path)
                move_file(file_path, DUPLICATES_FOLDER)
            else:
                hash_map[file_hash] = file_path

    return duplicates

def main():
    print(f"Scanning and categorizing files in {INPUT_DIRECTORY}...")
    duplicates = find_and_categorize_files(INPUT_DIRECTORY, include_images=True)

    print("\nOperation completed.")
    if duplicates:
        print(f"Duplicate files have been moved to {DUPLICATES_FOLDER}.")
    print(f"Error files have been moved to {ERROR_FOLDER}.")
    print(f"Images with text have been moved to {DOCUMENT_FOLDER}.")

if __name__ == "__main__":
    main()
