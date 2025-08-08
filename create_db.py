import face_recognition
import os
import numpy as np
import time

DB_FOLDER_PATH = os.path.join('static', 'generic_face_database')
ENCODINGS_FILE = "face_encodings.npy"

def precompute_encodings():
    """
    Scans the database folder, computes face encodings for each image,
    and saves them to a file for fast lookup later.
    """
    if not os.path.exists(DB_FOLDER_PATH):
        print(f"Error: Database folder '{DB_FOLDER_PATH}' not found.")
        print("Please make sure your actor images are inside that folder.")
        return

    print("Starting database scan and encoding...")
    start_time = time.time()
    
    known_encodings = {}
    image_files = [f for f in os.listdir(DB_FOLDER_PATH) if f.endswith(('.jpg', '.png', '.jpeg'))]
    total_images = len(image_files)
    
    if total_images == 0:
        print("Database folder is empty. No encodings to create.")
        return

    for i, filename in enumerate(image_files):
        image_path = os.path.join(DB_FOLDER_PATH, filename)
        
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        
        if encodings:
            known_encodings[image_path] = encodings[0]
        
        print(f"\rProcessing image {i+1}/{total_images}...", end="")

    if not known_encodings:
        print("\nCould not find any faces in the database images.")
        return

    print(f"\nSaving {len(known_encodings)} encodings to '{ENCODINGS_FILE}'...")
    np.save(ENCODINGS_FILE, known_encodings)
    
    end_time = time.time()
    print(f"Done. Pre-processing took {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    precompute_encodings()