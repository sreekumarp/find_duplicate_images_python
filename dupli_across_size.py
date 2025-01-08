import os
import hashlib
import shutil
from PIL import Image
import imagehash
from tqdm import tqdm

def calculate_image_hash(image_path, error_folder, hash_size=8):
    """Calculate a perceptual hash for an image after resizing it to a fixed size."""
    try:
        with Image.open(image_path) as img:
            # Resize the image to a fixed size before hashing
            img = img.resize((hash_size * 4, hash_size * 4), Image.ANTIALIAS)
            return imagehash.average_hash(img, hash_size=hash_size), img.size
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        move_to_error_folder(image_path, error_folder)
        return None, None

def move_to_error_folder(file_path, error_folder):
    """Move the file to the Error subfolder."""
    if not os.path.exists(error_folder):
        os.makedirs(error_folder)
    shutil.move(file_path, os.path.join(error_folder, os.path.basename(file_path)))
    print(f"Moved {file_path} to {error_folder}")

def rename_image_by_size(images, subfolder):
    """Rename images based on their resolution size, with _Size1 being the highest."""
    sorted_images = sorted(images, key=lambda x: x[1][0] * x[1][1], reverse=True)

    for idx, (file_path, resolution) in enumerate(sorted_images, start=1):
        base_name, ext = os.path.splitext(os.path.basename(file_path))
        new_name = f"{base_name}_Size{idx}{ext}"
        new_file_path = os.path.join(subfolder, new_name)

        os.rename(file_path, new_file_path)
        print(f"Renamed {file_path} -> {new_file_path}")

def find_and_rename_duplicates_in_subfolder(subfolder):
        """Find and rename duplicate images in a specific subfolder and its sub-subfolders."""
        hash_map = {}
        duplicates = set()
        error_folder = os.path.join(subfolder, "Error")
        images_with_resolution = []

        for root, _, files in os.walk(subfolder):
            for file in tqdm(files, desc=f"Processing {root}"):
                file_path = os.path.join(root, file)

                # Skip directories
                if not os.path.isfile(file_path):
                    continue

                # Process only image files
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                    file_hash, resolution = calculate_image_hash(file_path, error_folder)

                    if file_hash is None:
                        # Handle files with errors (optional, like in the original script)
                        continue

                    images_with_resolution.append((file_path, resolution))

                    if file_hash in hash_map:
                        # Mark as duplicate but do not rename yet
                        duplicates.add(hash_map[file_hash])
                    else:
                        hash_map[file_hash] = file_path

        # Rename images based on resolution
        rename_image_by_size(images_with_resolution, subfolder)

def main():
    # Hardcoded input folder
    base_folder = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\check1"

    # Ensure the folder exists
    if not os.path.exists(base_folder):
        print(f"Folder {base_folder} does not exist.")
        return
    
    find_and_rename_duplicates_in_subfolder(base_folder)

    # Iterate through all subfolders
    # for subfolder in os.listdir(base_folder):
    #     subfolder_path = os.path.join(base_folder, subfolder)

    #     if os.path.isdir(subfolder_path):
    #         print(f"Processing subfolder: {subfolder_path}")
    #         find_and_rename_duplicates_in_subfolder(subfolder_path)
    #         # Rename the subfolder by appending '_Done'
    #         new_subfolder_path = f"{subfolder_path}_Done"
    #         os.rename(subfolder_path, new_subfolder_path)
    #         print(f"Renamed subfolder: {subfolder_path} -> {new_subfolder_path}")

if __name__ == "__main__":
    main()
