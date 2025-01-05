import os
import hashlib
import shutil
from PIL import Image
import imagehash
from tqdm import tqdm

def calculate_image_hash(image_path):
    """Calculate a perceptual hash for an image."""
    try:
        with Image.open(image_path) as img:
            return imagehash.average_hash(img)
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def find_and_move_duplicates_in_subfolder(subfolder):
    """Find and move duplicate images or handle errors in a specific subfolder."""
    duplicates_folder = os.path.join(subfolder, "Duplicates")
    error_folder = os.path.join(subfolder, "Error")

    # Create subfolders for duplicates and errors if not exist
    os.makedirs(duplicates_folder, exist_ok=True)
    os.makedirs(error_folder, exist_ok=True)

    hash_map = {}
    for file in tqdm(os.listdir(subfolder), desc=f"Processing {subfolder}"):
        file_path = os.path.join(subfolder, file)

        # Skip directories
        if not os.path.isfile(file_path):
            continue

        # Process only image files
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            file_hash = calculate_image_hash(file_path)

            if file_hash is None:
                # Move files with errors to the error folder
                try:
                    dest_path = os.path.join(error_folder, file)
                    shutil.move(file_path, dest_path)
                    print(f"Error file moved: {file_path} -> {dest_path}")
                except Exception as e:
                    print(f"Error moving file {file_path}: {e}")
                continue

            if file_hash in hash_map:
                # Move duplicates to the duplicates folder
                try:
                    dest_path = os.path.join(duplicates_folder, file)
                    shutil.move(file_path, dest_path)
                    print(f"Duplicate moved: {file_path} -> {dest_path}")
                except Exception as e:
                    print(f"Error moving file {file_path}: {e}")
            else:
                hash_map[file_hash] = file_path

def main():
    # Hardcoded input folder
    base_folder = "F:\duplicates"

    # Ensure the folder exists
    if not os.path.exists(base_folder):
        print(f"Folder {base_folder} does not exist.")
        return

    # Iterate through all subfolders
    for subfolder in os.listdir(base_folder):
        subfolder_path = os.path.join(base_folder, subfolder)

        if os.path.isdir(subfolder_path):
            print(f"Processing subfolder: {subfolder_path}")
            find_and_move_duplicates_in_subfolder(subfolder_path)

if __name__ == "__main__":
    main()
