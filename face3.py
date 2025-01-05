import os
import cv2
import face_recognition

# Function to detect and recognize faces in an image
def process_image(image_path, known_face_encodings, known_face_names):
    """
    Detects and recognizes faces in an image.

    Args:
        image_path: Path to the image file.
        known_face_encodings: List of known face encodings.
        known_face_names: List of corresponding names for known faces.

    Returns:
        List of recognized face names.
    """
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # If a match was found, get the name of the person
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        face_names.append(name)

    return face_names

# Main function to sort photos
def sort_photos(input_dir, output_dir):
    """
    Sorts photos into folders based on recognized faces.

    Args:
        input_dir: Path to the input directory containing photos.
        output_dir: Path to the output directory.
    """
    known_face_encodings = []
    known_face_names = []

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through images in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(input_dir, filename)

            try:
                face_names = process_image(image_path, known_face_encodings, known_face_names)
            except Exception as e:
                print(f"Error processing image '{filename}': {e}")
                continue

            for face_name in face_names:
                face_dir = os.path.join(output_dir, face_name)
                os.makedirs(face_dir, exist_ok=True)
                new_filename = f"{face_name}_{os.path.splitext(filename)[0]}.jpg"
                new_path = os.path.join(face_dir, new_filename)
                cv2.imwrite(new_path, cv2.imread(image_path))

            # If any faces are recognized, add them to the known faces list
            for name in face_names:
                if name not in known_face_names:
                    known_face_names.append(name)
                    # Get the first encoding for each new face
                    face_encodings = face_recognition.face_encodings(
                        face_recognition.load_image_file(image_path))
                    if len(face_encodings) > 0:
                        known_face_encodings.append(face_encodings[0])

if __name__ == "__main__":
    input_dir = "D:\sample"  # Replace with your input directory
    output_dir = "D:\sample_out"  # Replace with your desired output directory
    sort_photos(input_dir, output_dir)