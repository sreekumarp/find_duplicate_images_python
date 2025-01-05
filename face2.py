import os
import cv2
import shutil
import face_recognition
from pathlib import Path

# Function to load image and detect faces
def detect_faces(image_path):
    # Load the image
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    return face_locations

# Function to check if the face is already recognized
def get_face_encoding(image_path):
    # Load the image
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings

# Main logic to sort images
def sort_images_by_faces(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    recognized_faces = {}  # Dictionary to store face encodings and corresponding names
    face_counter = 1  # Counter for naming folders
    progress = 0

    # Get all image files from the source folder
    image_files = [f for f in Path(source_folder).rglob('*') if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
    total_images = len(image_files)
    
    for image_file in image_files:
        print(f"Processing {image_file.name}...")
        
        face_locations = detect_faces(image_file)
        
        # If faces are found in the image
        if face_locations:
            face_encodings = get_face_encoding(image_file)

            for encoding in face_encodings:
                # Check if this face is already recognized
                known_face = None
                for known_encoding, name in recognized_faces.items():
                    matches = face_recognition.compare_faces([known_encoding], encoding)
                    if True in matches:
                        known_face = name
                        break
                
                # If it's a new face, prompt for name
                if known_face is None:
                    name = input(f"New face detected in {image_file.name}. Enter a name for this face: ")
                    folder_name = f"Face_{face_counter}_{name}"
                    recognized_faces[tuple(encoding)] = folder_name
                    face_counter += 1
                else:
                    folder_name = known_face

                # Create folder for the face if not already created
                face_folder = os.path.join(destination_folder, folder_name)
                if not os.path.exists(face_folder):
                    os.makedirs(face_folder)

                # Move the image to the corresponding face folder
                destination_path = os.path.join(face_folder, image_file.name)
                shutil.copy2(str(image_file), destination_path)
                print(f"Moved {image_file.name} to {folder_name}/")

        # Update progress
        progress += 1
        print(f"Progress: {progress}/{total_images} images processed")

if __name__ == "__main__":
    source_folder = "D:\sample"  # Replace with your source folder path
    destination_folder = "D:\sample_out"  # Replace with your destination folder path

    sort_images_by_faces(source_folder, destination_folder)
    print("Image sorting complete.")
