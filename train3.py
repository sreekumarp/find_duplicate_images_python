import os
import shutil
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms

# Define a simple convolutional neural network for image classification
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=4):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(32 * 56 * 56, 128)  # Adjust based on output size of conv layers
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 32 * 56 * 56)  # Adjust based on output size of conv layers
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Define image transformation for preprocessing
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Create and load the model
model = SimpleCNN(num_classes=4)  # 4 classes: Document, Screenshot, Meme, Photograph
model.load_state_dict(torch.load('path/to/your/trained_model.pth'))  # Load your trained model weights
model.eval()

def classify_image(image_path):
    """
    Classifies an image using the trained model.

    Args:
        image_path: Path to the image file.

    Returns:
        The predicted category (e.g., 'Document', 'Screenshot', 'Meme', 'Photograph').
    """

    try:
        img = Image.open(image_path)
        img_tensor = transform(img).unsqueeze(0)  # Add batch dimension

        with torch.no_grad():
            output = model(img_tensor)

        # Get predicted class probabilities
        probabilities = torch.softmax(output, dim=1) 
        _, predicted_class_index = torch.max(probabilities, 1) 

        # Define your class mapping
        class_mapping = {
            0: 'Document',
            1: 'Screenshot',
            2: 'Meme',
            3: 'Photograph'
        }

        predicted_category = class_mapping.get(predicted_class_index.item(), 'Unknown')

        # Check probability threshold
        probability_threshold = 0.8  # Adjust as needed
        top_probability, _ = torch.topk(probabilities, 1)
        if top_probability.item() < probability_threshold:
            predicted_category = 'Unknown' 

        return predicted_category

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return 'Unknown'

def classify_and_move_images(root_dir):
    """
    Classifies images in a given directory and moves them to respective subfolders.

    Args:
        root_dir: The root directory containing the images.
    """

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg')): 
                file_path = os.path.join(root, file)
                predicted_category = classify_image(file_path)

                # Create category subfolders if they don't exist
                category_dir = os.path.join(root, predicted_category)
                if not os.path.exists(category_dir):
                    os.makedirs(category_dir)

                # Move the file to the appropriate category subfolder
                new_file_path = os.path.join(category_dir, file)
                shutil.move(file_path, new_file_path)

if __name__ == "__main__":
    root_directory = "F:\\ULTFONE_20240829_175529\\E\\Lost Files\\File Name Lost\\jpg\\JPG\\2024\\Processed1\\300 x 200_Done"  # Replace with the actual root directory
    classify_and_move_images(root_directory)