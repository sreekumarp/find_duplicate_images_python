import os
import shutil
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Define the categories
categories = ['Document', 'Screenshot', 'Meme', 'Photograph']

def build_model():
    """Build a simple CNN model for image classification."""
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(len(categories), activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model(data_dir, model_save_path):
    """Train the CNN model on the provided dataset."""
    # Data augmentation and preprocessing
    train_datagen = ImageDataGenerator(
        rescale=1.0/255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=0.2  # Split data into training and validation
    )

    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='training'
    )

    validation_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )

    # Build the model
    model = build_model()

    # Train the model
    model.fit(
        train_generator,
        epochs=10,
        validation_data=validation_generator
    )

    # Save the model
    model.save(model_save_path)
    print(f"Model saved to {model_save_path}")

def classify_image(model, image_path):
    """Classify an image into one of the categories."""
    try:
        # Load and preprocess the image
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))  # Resize to the input size of your model
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, axis=0) / 255.0  # Normalize

        # Predict the category
        predictions = model.predict(img_array)
        category_index = predictions.argmax()
        return categories[category_index]
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def organize_images(base_folder, model):
    """Classify and move images into subfolders based on their categories."""
    for root, _, files in os.walk(base_folder):
        # Skip the "Error" folder
        if "Error" in root.split(os.sep):
            continue

        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                file_path = os.path.join(root, file)

                # Classify the image
                category = classify_image(model, file_path)
                if category and category != 'Meme':
                    # Create the category folder if it doesn't exist
                    category_folder = os.path.join(base_folder, category)
                    if not os.path.exists(category_folder):
                        os.makedirs(category_folder)

                    # Move the file to the category folder
                    shutil.move(file_path, os.path.join(category_folder, file))
                    print(f"Moved {file} to {category}/")

if __name__ == "__main__":
    # Base folder containing images or dataset
    mode = 'classify'
    base_folder = 'F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\Processed1\\300 x 1100_Done'
    model_path = 'D:\\Projects\\face_sorter\\class.keras'
    
    if os.path.exists(model_path) and os.path.exists(base_folder):
        model = tf.keras.models.load_model(model_path)
        organize_images(base_folder, model)
        print("Image classification and organization complete.")
    else:
        print("Invalid model or folder path.")
    # input("Enter 'train' to train a model or 'classify' to classify images: ").strip()

    # if mode == 'train':
    #     data_dir = input("Enter the path to the dataset folder: ").strip()
    #     model_save_path = input("Enter the path to save the trained model: ").strip()
    #     if os.path.exists(data_dir):
    #         train_model(data_dir, model_save_path)
    #     else:
    #         print("Invalid dataset folder path.")

    # elif mode == 'classify':
    #     model_path = input("Enter the path to the trained model: ").strip()
    #     base_folder = input("Enter the path to the folder containing images: ").strip()
    #     if os.path.exists(model_path) and os.path.exists(base_folder):
    #         model = tf.keras.models.load_model(model_path)
    #         organize_images(base_folder, model)
    #         print("Image classification and organization complete.")
    #     else:
    #         print("Invalid model or folder path.")

    # else:
    #     print("Invalid mode. Choose 'train' or 'classify'.")
