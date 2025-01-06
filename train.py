import tensorflow as tf
from tensorflow.keras import layers, models
import os

# Define paths to dataset directories
TRAIN_DIR = "F:\\dataset\\train"  # Update with the actual path
VAL_DIR = "F:\\dataset\\validation"  # Update with the actual path
MODEL_SAVE_PATH = "document_meme_classifier.h5"

# Define parameters
IMG_SIZE = (224, 224)  # Image size for resizing
BATCH_SIZE = 32  # Batch size
EPOCHS = 10  # Number of epochs for training
FINE_TUNE_EPOCHS = 5  # Number of epochs for fine-tuning
CLASS_NAMES = ["Document", "Meme", "Normal", "Screenshots"]  # Class names (ensure they match your dataset)

# Step 1: Load and preprocess the dataset
def load_datasets():
    train_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        TRAIN_DIR,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical"
    )
    val_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        VAL_DIR,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical"
    )

    # Optimize datasets for performance
    #train_dataset = train_dataset.prefetch(buffer_size=tf.data.AUTOTUNE)
    train_dataset = train_dataset.prefetch(buffer_size=tf.data.AUTOTUNE).apply(
    tf.data.experimental.ignore_errors()
    )
    val_dataset = val_dataset.prefetch(buffer_size=tf.data.AUTOTUNE).apply(
    tf.data.experimental.ignore_errors()
    )
    return train_dataset, val_dataset

# Step 2: Build the model using transfer learning
def build_model():
    # Load pre-trained MobileNetV2
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False  # Freeze the base model

    # Add custom classification layers
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.5),
        layers.Dense(len(CLASS_NAMES), activation="softmax")
    ])

    # Compile the model
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model

# Step 3: Train the model
def train_model(model, train_dataset, val_dataset):
    print("Starting model training...")
    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=EPOCHS
    )
    print("Training complete!")
    return model, history

# Step 4: Fine-tune the base model
def fine_tune_model(model, train_dataset, val_dataset):
    print("Starting fine-tuning...")
    # Unfreeze the base model
    model.layers[0].trainable = True

    # Re-compile the model with a lower learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    # Fine-tune the model
    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=FINE_TUNE_EPOCHS
    )
    print("Fine-tuning complete!")
    return model, history

# Step 5: Main script
if __name__ == "__main__":
    # Ensure dataset paths exist
    if not os.path.exists(TRAIN_DIR) or not os.path.exists(VAL_DIR):
        print("Dataset directories not found. Please check TRAIN_DIR and VAL_DIR.")
        exit()

    # Load datasets
    train_dataset, val_dataset = load_datasets()

    # Build the model
    model = build_model()

    # Train the model
    model, _ = train_model(model, train_dataset, val_dataset)

    # Fine-tune the model
    model, _ = fine_tune_model(model, train_dataset, val_dataset)

    # Save the trained model
    model.save(MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")
