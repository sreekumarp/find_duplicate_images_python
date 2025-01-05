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

def rename_duplicate_image(file_path, original_folder, file_name):
    """Rename duplicate image by adding a postfix to it."""
    base_name, ext = os.path.splitext(file_name)
    counter = 1
    new_name = f"{base_name}_Dupli{counter}{ext}"
    new_file_path = os.path.join(original_folder, new_name)

    while os.path.exists(new_file_path):
        counter += 1
        new_name = f"{base_name}_Dupli{counter}{ext}"
        new_file_path = os.path.join(original_folder, new_name)

    # Rename the duplicate file
    os.rename(file_path, new_file_path)
    print(f"Duplicate renamed: {file_path} -> {new_file_path}")

def find_and_rename_duplicates_in_subfolder(subfolder):
    """Find and rename duplicate images in a specific subfolder."""
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
                # Handle files with errors (optional, like in the original script)
                print(f"Error processing file: {file_path}")
                continue

            if file_hash in hash_map:
                # Rename duplicate instead of moving
                original_file_path = hash_map[file_hash]
                rename_duplicate_image(file_path, subfolder, file)
            else:
                hash_map[file_hash] = file_path

def main():
    # Hardcoded input folder
    base_folder = "path/to/your/hardcoded/folder"

    # Ensure the folder exists
    if not os.path.exists(base_folder):
        print(f"Folder {base_folder} does not exist.")
        return

    # Iterate through all subfolders
    for subfolder in os.listdir(base_folder):
        subfolder_path = os.path.join(base_folder, subfolder)

        if os.path.isdir(subfolder_path):
            print(f"Processing subfolder: {subfolder_path}")
            find_and_rename_duplicates_in_subfolder(subfolder_path)

if __name__ == "__main__":
    main()
