import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import os
import shutil
import pytesseract
from PIL import Image

# Define class labels
CLASS_LABELS = ["Document", "Meme", "Normal", "Screenshots"]

# Load a pre-trained MobileNetV2 model for feature extraction
def load_model():

    base_model = tf.keras.applications.MobileNetV2(
        weights="imagenet", include_top=False, input_shape=(224, 224, 3)
    )
    model = tf.keras.models.load_model("document_meme_classifier.h5")

    # model = tf.keras.Sequential([
    #     base_model,
    #     tf.keras.layers.GlobalAveragePooling2D(),
    #     tf.keras.layers.Dense(len(CLASS_LABELS), activation="softmax")
    # ])
    return model

# Load or fine-tune the model
def load_or_fine_tune_model(model_path="model.h5"):
    if os.path.exists(model_path):
        print("Loading pre-trained model...")
        model = tf.keras.models.load_model(model_path)
    else:
        print("Fine-tuning the model...")
        model = load_model()
        # Fine-tune on custom dataset (not included here)
        # Compile the model
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        # Train on your dataset (use model.fit())
        # Save the model after training
        model.save(model_path)
    return model

# Preprocess input image
def preprocess_image(image_path):
    img = load_img(image_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    return np.expand_dims(img_array, axis=0)

# Check if the image contains at least 30% text
def contains_text(image_path):
    image = Image.open(image_path)
    image_area = image.size[0] * image.size[1]
    boxes = pytesseract.image_to_boxes(image)
    text_area = 0
    for box in boxes.splitlines():
        b = box.split(' ')
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        text_area += (w - x) * (h - y)
    text_percentage = (text_area / image_area) * 100
    return text_percentage >= 30

# Predict image class
def predict_image_class(model, image_path):
    preprocessed_image = preprocess_image(image_path)
    predictions = model.predict(preprocessed_image, verbose=0)
    predicted_class = CLASS_LABELS[np.argmax(predictions)]
    confidence = np.max(predictions)
    
    # Check if the image contains text
    if predicted_class == "Document" and not contains_text(image_path):
        predicted_class = "Normal"
    
    return predicted_class, confidence

# Process images in a folder and its subfolders
def process_images_in_folder(model, folder_path):
    for root, _, files in os.walk(folder_path):
        if "Error" in root:
            continue
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')) and not file.lower().endswith('xxjpg'):
                file_path = os.path.join(root, file)
                predicted_class, confidence = predict_image_class(model, file_path)
                print(f"File: {file_path}")
                print(f"Predicted Class: {predicted_class}")
                print(f"Confidence: {confidence:.2f}")
                print("-" * 40)

                # Skip moving the file if it is classified as "Normal"
                if predicted_class == "Normal":
                    continue

                # Determine the confidence range
                confidence_percentage = int(confidence * 100)
                confidence_range = f"{(confidence_percentage // 10) * 10}-{((confidence_percentage // 10) + 1) * 10}"

                # Create the target directory if it doesn't exist
                target_dir = os.path.join(folder_path, predicted_class, confidence_range)
                os.makedirs(target_dir, exist_ok=True)

                # Move the file to the target directory
                target_path = os.path.join(target_dir, file)
                shutil.move(file_path, target_path)

if __name__ == "__main__":
    # Load or fine-tune model
    model = load_or_fine_tune_model()
    # Path to folder containing images
    folder_path = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\Processed1\\300 x 200_Done"  # Update with actual folder path

    # Process images
    process_images_in_folder(model, folder_path)
