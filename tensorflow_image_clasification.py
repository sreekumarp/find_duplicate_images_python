import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import os

# Define class labels
CLASS_LABELS = ["Document", "Meme"]

# Load a pre-trained MobileNetV2 model for feature extraction
def load_model():
    base_model = tf.keras.applications.MobileNetV2(
        weights="imagenet", include_top=False, input_shape=(224, 224, 3)
    )
    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(len(CLASS_LABELS), activation="softmax")
    ])
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

# Predict image class
def predict_image_class(model, image_path):
    preprocessed_image = preprocess_image(image_path)
    predictions = model.predict(preprocessed_image, verbose=0)
    predicted_class = CLASS_LABELS[np.argmax(predictions)]
    confidence = np.max(predictions)
    return predicted_class, confidence

# Process images in a folder and its subfolders
def process_images_in_folder(model, folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')) and not file.lower().endswith('xxjpg'):
                file_path = os.path.join(root, file)
                predicted_class, confidence = predict_image_class(model, file_path)
                print(f"File: {file_path}")
                print(f"Predicted Class: {predicted_class}")
                print(f"Confidence: {confidence:.2f}")
                print("-" * 40)

if __name__ == "__main__":
    # Load or fine-tune model
    model = load_or_fine_tune_model()

    # Path to folder containing images
    folder_path = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\Processed1\\300 x 100_Done"  # Update with actual folder path

    # Process images
    process_images_in_folder(model, folder_path)
