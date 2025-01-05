import os
import cv2
import shutil
import face_recognition
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
from pathlib import Path
import threading

class FaceSorterApp:
    def __init__(self, root, source_folder, destination_folder):
        self.root = root
        self.source_folder = source_folder
        self.destination_folder = destination_folder

        self.recognized_faces = {}  # Dictionary to store face encodings and corresponding names
        self.face_counter = 1  # Counter for naming folders
        self.duplicates = []  # List to store duplicate image paths

        self.image_files = [f for f in Path(source_folder).rglob('*') if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        self.total_images = len(self.image_files)
        self.current_image_index = 0

        self.timer = None
        self.default_name_used = False  # Tracks if a default name was used

        self.create_widgets()
        self.load_next_image()
    def on_next_button(self):
        # Cancel any active timer
        if self.timer:
            self.timer.cancel()

        # If no name is entered, assign a default name
        if not self.name_entry.get():
            self.assign_default_name()
        else:
            # Use the entered name
            self.on_name_entry()

    def create_widgets(self):
        # Image display area
        self.canvas = tk.Canvas(self.root, width=600, height=400)
        self.canvas.pack()

        # Label to show image file info
        self.label = tk.Label(self.root, text="")
        self.label.pack()

        # Progress bar
        self.progress_label = tk.Label(self.root, text="Progress:")
        self.progress_label.pack()
        self.progress_bar = Progressbar(self.root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_bar.pack()

        # Name entry for the face
        self.entry_label = tk.Label(self.root, text="Enter name for the face (will auto-assign in 1 minute):")
        self.entry_label.pack()

        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        # Buttons
        self.next_button = tk.Button(self.root, text="Next", command=self.on_next_button)
        self.next_button.pack()

        self.quit_button = tk.Button(self.root, text="Quit", command=self.root.quit)
        self.quit_button.pack()

    def load_next_image(self):
        if self.current_image_index < self.total_images:
            self.image_file = self.image_files[self.current_image_index]
            self.label.config(text=f"Processing {self.image_file.name}...")
            self.update_progress()
            self.display_image()
            self.detect_faces()
        else:
            self.review_duplicates()

    def update_progress(self):
        progress = int((self.current_image_index / self.total_images) * 100)
        self.progress_bar['value'] = progress
        self.root.update_idletasks()

    def display_image(self):
        # Load image with OpenCV
        image = cv2.imread(str(self.image_file))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk

    def detect_faces(self):
        # Detect faces in the image
        image = face_recognition.load_image_file(str(self.image_file))
        self.face_locations = face_recognition.face_locations(image)
        self.face_encodings = face_recognition.face_encodings(image, self.face_locations)

        if self.face_locations:
            self.show_face(0)  # Show the first face
        else:
            self.root.title("No faces found in this image.")
            self.move_to_next_image()

    def show_face(self, face_index):
        if face_index < len(self.face_locations):
            # Extract the face from the image
            top, right, bottom, left = self.face_locations[face_index]
            image = cv2.imread(str(self.image_file))
            face_image = image[top:bottom, left:right]

            # Display face using Tkinter
            face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            face_pil = Image.fromarray(face_rgb)
            face_tk = ImageTk.PhotoImage(face_pil)

            # Display the face on the canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=face_tk)
            self.canvas.image = face_tk

            # Ask for the name of the person in the face
            self.name_entry.delete(0, tk.END)
            self.name_entry.focus_set()

            # Set a timer to assign a default name if no input is given
            self.timer = threading.Timer(1, self.assign_default_name)
            self.timer.start()

            self.name_entry.bind("<Return>", self.on_name_entry)

    def assign_default_name(self):
        self.default_name_used = True
        self.name_entry.insert(0, f"Face{self.face_counter}")
        self.on_name_entry()

    def on_name_entry(self, event=None):
        # Cancel the timer
        if self.timer:
            self.timer.cancel()

        # Get the name entered by the user
        name = self.name_entry.get()
        if not name:
            return  # Wait for the name to be entered or timer to expire

        # Save the face encoding and move the image
        folder_name = self.create_folder_for_face(name)
        self.check_duplicates(folder_name)
        self.move_image_to_folder(folder_name)

        # Move to the next image
        self.move_to_next_image()

    def create_folder_for_face(self, name):
        folder_name = f"Face_{self.face_counter}_{name}"
        folder_path = os.path.join(self.destination_folder, folder_name)

        # Create folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Store the face encoding with the folder name
        #self.recognized_faces[self.face_encodings[0]] = folder_name
        self.recognized_faces[tuple(self.face_encodings[0])] = folder_name
        self.face_counter += 1
        return folder_name

    def check_duplicates(self, folder_name):
        for known_encoding, known_folder in self.recognized_faces.items():
            if face_recognition.compare_faces([known_encoding], self.face_encodings[0])[0]:
                self.duplicates.append((str(self.image_file), folder_name))

    def move_image_to_folder(self, folder_name, operation="copy"):
        #destination_path = os.path.join(self.destination_folder, folder_name, self.image_file.name)
        #shutil.move(str(self.image_file), destination_path)
        destination_path = os.path.join(self.destination_folder, folder_name, self.image_file.name)
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        if operation == "move":
            shutil.move(str(self.image_file), destination_path)
        elif operation == "copy":
            shutil.copy2(str(self.image_file), destination_path)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def move_to_next_image(self):
        self.current_image_index += 1
        self.load_next_image()

    def review_duplicates(self):
        if not self.duplicates:
            messagebox.showinfo("Complete", "All images have been processed, and no duplicates were found.")
            self.root.quit()
            return

        # for duplicate, folder_name in self.duplicates:
        #     message = f"Duplicate found: {duplicate} in folder {folder_name}. Delete it?"
        #     if messagebox.askyesno("Duplicate Found", message):
        #         os.remove(duplicate)

        messagebox.showinfo("Complete", "All images have been processed!")
        self.root.quit()

if __name__ == "__main__":
    source_folder = "D:\sample"  # Replace with your source folder path
    destination_folder = "D:\sample_out"  # Replace with your destination folder path

    root = tk.Tk()
    app = FaceSorterApp(root, source_folder, destination_folder)
    root.mainloop()
