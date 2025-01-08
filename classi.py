import os
import shutil
import cv2
import numpy as np
from sklearn.decomposition import SparseCoder
from sklearn.cluster import KMeans
from skimage.feature import hog

def extract_features(image_path):
    """Extracts HOG (Histogram of Oriented Gradients) features from an image."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return None
    image_resized = cv2.resize(image, (128, 128))
    features, _ = hog(image_resized, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), visualize=True)
    return features

def classify_image(features, coder, dictionary):
    """Classify an image based on sparse coding."""
    sparse_code = coder.transform(features.reshape(1, -1))
    reconstruction = np.dot(sparse_code, dictionary)
    category = np.argmax(reconstruction)
    return category

def organize_files(base_dir, categories):
    """Organizes files into subfolders based on classification."""
    for category in categories:
        category_path = os.path.join(base_dir, category)
        os.makedirs(category_path, exist_ok=True)

    for root, _, files in os.walk(base_dir):
        if os.path.basename(root) == "Error":
            continue

        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith('.xxjpg') or not file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                continue

            features = extract_features(file_path)
            if features is None:
                continue

            category_idx = classify_image(features, sparse_coder, dictionary)
            category = categories[category_idx]
            target_path = os.path.join(base_dir, category, file)

            shutil.move(file_path, target_path)

if __name__ == "__main__":
    base_directory = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\Processed1\\1100 x 900_Done"  # Replace with your directory path
    categories = ["Documents", "Screenshots", "Memes", "Photographs"]

    # Load a dummy dictionary for sparse coding
    dictionary = np.random.rand(324, len(categories))  # 324 is HOG feature length

    sparse_coder = SparseCoder(dictionary=dictionary, transform_n_nonzero_coefs=10, transform_algorithm='omp')

    organize_files(base_directory, categories)
    print("Image classification and organization complete.")
