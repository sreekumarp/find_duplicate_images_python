import os
import hashlib
import shutil
from PIL import Image
import imagehash
from tqdm import tqdm

def calculate_image_hash(image_path, error_folder):
    """Calculate a perceptual hash for an image."""
    try:
        with Image.open(image_path) as img:
            return imagehash.average_hash(img)
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        move_to_error_folder(image_path, error_folder)
        return None

def move_to_error_folder(file_path, error_folder):
    """Move the file to the Error subfolder."""
    if not os.path.exists(error_folder):
        os.makedirs(error_folder)
    shutil.move(file_path, os.path.join(error_folder, os.path.basename(file_path)))
    print(f"Moved {file_path} to {error_folder}")

def rename_duplicate_image(file_path, original_file_path, original_folder, file_name):
    """Rename duplicate image by adding a postfix to it."""
    base_name, ext = os.path.splitext(os.path.basename(original_file_path))
    counter = 1
    new_name = f"{base_name}_Orig_Dupli{counter}{ext}"
    new_file_path = os.path.join(original_folder, new_name)

    while os.path.exists(new_file_path):
        counter += 1
        new_name = f"{base_name}_Orig_Dupli{counter}{ext}"
        new_file_path = os.path.join(original_folder, new_name)

    # Rename the duplicate file
    os.rename(file_path, new_file_path)
    print(f"Duplicate renamed: {file_path} -> {new_file_path}")

def rename_original_image(original_file_path):
    """Rename the original image by adding '_Orig' postfix."""
    base_name, ext = os.path.splitext(original_file_path)
    new_name = f"{base_name}_Orig{ext}"
    new_file_path = new_name

    if not os.path.exists(new_file_path):
        os.rename(original_file_path, new_file_path)
        print(f"Original renamed: {original_file_path} -> {new_file_path}")
        return new_file_path
    return original_file_path

def find_and_rename_duplicates_in_subfolder(subfolder):
    """Find and rename duplicate images in a specific subfolder."""
    hash_map = {}
    duplicates = set()
    error_folder = os.path.join(subfolder, "Error")
    
    for file in tqdm(os.listdir(subfolder), desc=f"Processing {subfolder}"):
        file_path = os.path.join(subfolder, file)

        # Skip directories
        if not os.path.isfile(file_path):
            continue

        # Process only image files
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            file_hash = calculate_image_hash(file_path, error_folder)

            if file_hash is None:
                # Handle files with errors (optional, like in the original script)
                continue

            if file_hash in hash_map:
                # Rename duplicate instead of moving
                original_file_path = hash_map[file_hash]
                rename_duplicate_image(file_path, original_file_path, subfolder, file)
                duplicates.add(original_file_path)
            else:
                hash_map[file_hash] = file_path

    # Rename original files only if they have duplicates
    for original_file_path in duplicates:
        rename_original_image(original_file_path)

def main():
    
    # Hardcoded input folder
    base_folder = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\Processed1"

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
            # Rename the subfolder by appending '_Done'
            new_subfolder_path = f"{subfolder_path}_Done"
            os.rename(subfolder_path, new_subfolder_path)
            print(f"Renamed subfolder: {subfolder_path} -> {new_subfolder_path}")

if __name__ == "__main__":
    main()
