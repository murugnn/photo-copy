import os
import numpy as np
import face_recognition
from flask import Flask, request, jsonify, url_for, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ENCODINGS_FILE = "face_encodings.npy"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def find_best_match(user_image_path):
    if not os.path.exists(ENCODINGS_FILE):
        return None, 0, "Error: Encodings file not found. Please run create_db.py."

    try:
        known_encodings_dict = np.load(ENCODINGS_FILE, allow_pickle=True).item()
        known_face_paths = list(known_encodings_dict.keys())
        known_face_encodings = list(known_encodings_dict.values())
    except Exception as e:
        return None, 0, f"Error loading encodings file: {e}"

    if not known_face_encodings:
        return None, 0, "Error: The encodings file is empty."

    user_image = face_recognition.load_image_file(user_image_path)
    user_face_locations = face_recognition.face_locations(user_image)
    if not user_face_locations:
        return None, 0, "Error: Could not detect a face in the uploaded image."
        
    user_face_encoding = face_recognition.face_encodings(user_image, user_face_locations)[0]
    
    face_distances = face_recognition.face_distance(known_face_encodings, user_face_encoding)
    best_match_index = np.argmin(face_distances)
    best_match_path = known_face_paths[best_match_index]
    
    distance = face_distances[best_match_index]
    confidence = max(0, (1.0 - distance - 0.1) * 150)
    confidence = min(99, int(confidence))
    
    return best_match_path, confidence, None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/find-match', methods=['POST'])
def find_match_endpoint():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    if file:
        filename = secure_filename(file.filename)
        user_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(user_image_path)

        matched_image_path, confidence, error = find_best_match(user_image_path)
        
        os.remove(user_image_path)

        if error:
            return jsonify({'success': False, 'error': error}), 500

        relative_path = os.path.relpath(matched_image_path, 'static')
        url_path = '/'.join(relative_path.split(os.sep))
        matched_image_url = url_for('static', filename=url_path, _external=True)

        return jsonify({
            'success': True, 
            'matched_image_url': matched_image_url,
            'confidence': confidence
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)