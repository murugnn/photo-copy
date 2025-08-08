import os
import numpy as np
import face_recognition
from flask import Flask, request, jsonify, url_for, render_template
from werkzeug.utils import secure_filename
from groq import Groq
from dotenv import load_dotenv  # <-- 1. IMPORT THE FUNCTION

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()  # <-- 2. CALL THE FUNCTION TO LOAD .env

app = Flask(__name__)

# --- CONFIGURATION ---
UPLOAD_FOLDER = 'uploads'
ENCODINGS_FILE = "face_encodings.npy"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- GROQ AI CLIENT INITIALIZATION ---
# This part now works because load_dotenv() has loaded the key
try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    if not os.environ.get("GROQ_API_KEY"):
        print("GROQ_API_KEY environment variable not found. Roasting feature will be disabled.")
        groq_client = None
    else:
        print("Groq client initialized successfully.")
except Exception as e:
    groq_client = None
    print(f"Could not initialize Groq client: {e}. Roasting feature will be disabled.")


def get_ai_roast(actor_info):
    """
    Generates a witty roast using the Groq API and Llama3.
    """
    if not groq_client:
        return "The AI is on a coffee break. But let's be real, it probably thinks your face broke its algorithm."

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a witty, sarcastic AI assistant named PhotoCOPY. Your job is to generate a short, funny, one or two-sentence roast for a user based on their celebrity lookalike. The user has just uploaded their selfie to find their doppelgänger. Keep it light-hearted and clever."
                },
                {
                    "role": "user",
                    "content": f"My doppelgänger is {actor_info}. Roast me."
                }
            ],
            model="llama3-8b-8192",
            temperature=0.8,
            max_tokens=100,
        )
        roast = chat_completion.choices[0].message.content
        return roast.strip()
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "The AI tried to think of a roast, but seeing your face caused a short circuit. Congrats?"


def find_best_match(user_image_path):
    """
    Finds the best matching face from the known encodings.
    """
    if not os.path.exists(ENCODINGS_FILE):
        return None, "Error: Encodings file not found. Please run create_db.py."

    try:
        known_encodings_dict = np.load(ENCODINGS_FILE, allow_pickle=True).item()
        known_face_paths = list(known_encodings_dict.keys())
        known_face_encodings = list(known_encodings_dict.values())
    except Exception as e:
        return None, f"Error loading encodings file: {e}"

    if not known_face_encodings:
        return None, "Error: The encodings file is empty."

    user_image = face_recognition.load_image_file(user_image_path)
    user_face_locations = face_recognition.face_locations(user_image)
    if not user_face_locations:
        return None, "Error: Could not detect a face in the uploaded image."
        
    user_face_encoding = face_recognition.face_encodings(user_image, user_face_locations)[0]
    
    face_distances = face_recognition.face_distance(known_face_encodings, user_face_encoding)
    best_match_index = np.argmin(face_distances)
    best_match_path = known_face_paths[best_match_index]
    
    return best_match_path, None

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

        matched_image_path, error = find_best_match(user_image_path)
        
        os.remove(user_image_path)

        if error:
            return jsonify({'success': False, 'error': error}), 500

        relative_path = os.path.relpath(matched_image_path, 'static')
        url_path = '/'.join(relative_path.split(os.sep))
        matched_image_url = url_for('static', filename=url_path, _external=True)
        
        matched_filename = os.path.basename(matched_image_path)
        actor_name = f"Doppelgänger #{matched_filename.split('.')[0].split('_')[-1]}"

        roast_message = get_ai_roast(actor_name)

        return jsonify({
            'success': True,
            'matched_image_url': matched_image_url,
            'roast_message': roast_message
        })

if __name__ == '__main__':
    # The port was 5007 in your code, keeping it that way.
    app.run(debug=True, host='0.0.0.0', port=5000)