# This is a python script I used to extract the face from malayalam movie scenes from Youtube.
# Just for reference, happy coding!!

import os
import cv2
import yt_dlp
from mtcnn import MTCNN
import numpy as np

# --- 1. Upgraded Video Downloader ---
def download_hd_video(url, output_path='video.mp4', min_height=720):
    """
    Downloads a video from YouTube, attempting to get at least 720p quality.
    """
    print(f"Starting HD download for: {url}")
    # This format string prioritizes videos with a height of at least 720p
    ydl_opts = {
        'format': f'bestvideo[height>={min_height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Video download complete.")
        return True
    except Exception as e:
        print(f"An error occurred during download: {e}")
        return False

# --- 2. Upgraded Database Creator with Quality Filters ---
def create_high_quality_face_db(video_path, output_folder, frame_interval=30, 
                                min_eye_distance=30, padding_pixels=25, jpeg_quality=95):
    """
    Extracts high-quality faces from a video by filtering based on size and clarity.

    Args:
        video_path (str): Path to the video file.
        output_folder (str): Folder to save the high-quality cropped faces.
        frame_interval (int): Process every Nth frame.
        min_eye_distance (int): The minimum pixel distance between the eyes for a face to be considered high-quality.
        padding_pixels (int): Pixels to add around the detected face bounding box.
        jpeg_quality (int): The quality (0-100) to use when saving the JPEG files.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    detector = MTCNN()
    frame_count = 0
    saved_face_count = len([name for name in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, name))])
    
    total_faces_detected = 0

    print("Starting high-quality face extraction...")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = detector.detect_faces(frame_rgb)
            total_faces_detected += len(faces)
            
            for face in faces:
                # --- QUALITY FILTERING ---
                # 1. Confidence Score Filter
                if face['confidence'] < 0.98:
                    continue

                # 2. Face Size / Resolution Filter (THE MOST IMPORTANT ONE)
                keypoints = face['keypoints']
                left_eye = np.array(keypoints['left_eye'])
                right_eye = np.array(keypoints['right_eye'])
                eye_distance = np.linalg.norm(left_eye - right_eye)

                if eye_distance < min_eye_distance:
                    continue # Skip this face, it's too small and will be low-res.

                # --- IF FACE IS HIGH-QUALITY, PROCEED WITH CROPPING ---
                x, y, w, h = face['box']
                
                # 3. Add Padding to the Crop
                x1 = max(0, x - padding_pixels)
                y1 = max(0, y - padding_pixels)
                x2 = min(frame.shape[1], x + w + padding_pixels)
                y2 = min(frame.shape[0], y + h + padding_pixels)
                
                cropped_face = frame[y1:y2, x1:x2]

                # Ensure the cropped face isn't empty
                if cropped_face.size == 0:
                    continue

                # 4. Save with High JPEG Quality
                face_filename = os.path.join(output_folder, f"face_{saved_face_count}.jpg")
                cv2.imwrite(face_filename, cropped_face, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
                saved_face_count += 1
            
            print(f"\rProcessed frame: {frame_count} | Total Detected: {total_faces_detected} | Saved (High-Quality): {saved_face_count}", end="")

        frame_count += 1

    cap.release()
    print(f"\nExtraction complete. Your database now contains {saved_face_count} high-quality faces.")

# --- Main Execution Block ---
if __name__ == "__main__":
    YOUTUBE_URL = "https://youtube.com/shorts/mMx-cwXxw1M?si=OJQCtIuCe5xKe6gB"
    VIDEO_FILENAME = "temp_video.mp4"
    DB_FOLDER_NAME = "generic_face_database"
    
    # --- Script Execution ---
    if download_hd_video(YOUTUBE_URL, VIDEO_FILENAME):
        create_high_quality_face_db(
            video_path=VIDEO_FILENAME, 
            output_folder=DB_FOLDER_NAME, 
            frame_interval=15,    # Check frames more often to not miss good faces
            min_eye_distance=40,  # Increase this for even higher quality
            padding_pixels=30
        )
        
        if os.path.exists(VIDEO_FILENAME):
            os.remove(VIDEO_FILENAME)
            print(f"Cleaned up and removed {VIDEO_FILENAME}.")