import os
import hashlib
from PIL import Image
import re

def get_image_hash(image_path):
    """Generate a hash for an image file."""
    with Image.open(image_path) as img:
        img = img.resize((8, 8), Image.Resampling.LANCZOS).convert("L")
        pixels = list(img.getdata())
        avg_pixel = sum(pixels) / len(pixels)
        bits = [1 if pixel > avg_pixel else 0 for pixel in pixels]
        hash_string = ''.join(str(bit) for bit in bits)
        return hashlib.md5(hash_string.encode('utf-8')).hexdigest()

def get_image_resolution(image_path):
    """Get the resolution of an image."""
    with Image.open(image_path) as img:
        return img.size

def find_duplicates(root_folder):
    """Find and rename duplicate images in a folder structure."""
    hash_map = {}
    exclude_folder_name = "Error"
    exclude_extension = ".xxjpg"

    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Exclude directories named "Error"
        dirnames[:] = [d for d in dirnames if d != exclude_folder_name]

        for filename in filenames:
            if filename.lower().endswith(exclude_extension):
                continue

            file_path = os.path.join(dirpath, filename)
            try:
                file_hash = get_image_hash(file_path)
                resolution = get_image_resolution(file_path)

                if file_hash in hash_map:
                    hash_map[file_hash].append((file_path, resolution))
                else:
                    hash_map[file_hash] = [(file_path, resolution)]
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    for file_hash, files in hash_map.items():
        if len(files) > 1:
            sorted_files = sorted(files, key=lambda x: x[1], reverse=True)  # Sort by resolution descending
            highest_res_file = sorted_files[0]

            for idx, (file_path, resolution) in enumerate(sorted_files):
                if (highest_res_file[0] == file_path):
                    new_filename = f"{os.path.splitext(os.path.split(file_path)[1])[0]}_Size1{os.path.splitext(file_path)[1]}"
                    new_filepath = os.path.join(os.path.dirname(file_path), new_filename)
                    try:
                        os.rename(file_path, new_filepath)
                        print(f"Renamed {file_path} -> {new_filepath}")
                    except Exception as e:
                        print(f"Error renaming {file_path} to {new_filepath}: {e}")
                else:
                    # Regular expression to extract resolution
                    resolution_pattern = r"\b\d+\s*x\s*\d+\b"

                    # Search for the pattern in the string
                    match = re.search(resolution_pattern, file_path)

                    if match:
                        resolution = match.group().replace(" ", "")
                    else:
                        resolution = f"{resolution[0]}x{resolution[1]}"
                        
                    size_suffix = f"_Size{idx + 1}"
                    new_filename = f"{os.path.splitext(os.path.split(highest_res_file[0])[1])[0]}{size_suffix}_{resolution}{os.path.splitext(highest_res_file[0])[1]}"
                    new_filepath = os.path.join(os.path.dirname(highest_res_file[0]), new_filename)

                    try:
                        os.rename(file_path, new_filepath)
                        print(f"Renamed {file_path} -> {new_filepath}")
                    except Exception as e:
                        print(f"Error renaming {file_path} to {new_filepath}: {e}")

if __name__ == "__main__":
    root_folder = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\check1"
    find_duplicates(root_folder)
