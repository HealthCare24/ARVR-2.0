from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import io
from PIL import Image
import mediapipe as mp

app = Flask(__name__)
CORS(app)

mp_pose = mp.solutions.pose

# Important landmarks based on MediaPipe pose
# IMPORTANT_LANDMARKS = [0, 1, 2, 5, 6, 11, 12, 13, 14]  # Add indexes of important landmarks based on your model

def normalize_coordinates(coordinates):
    if not coordinates:
        return coordinates

    x_coords = [coord[0] for coord in coordinates]
    y_coords = [coord[1] for coord in coordinates]
    z_coords = [coord[2] if len(coord) > 2 else 0 for coord in coordinates]  # Handle z if present

    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    min_z, max_z = min(z_coords), max(z_coords)

    normalized_coords = [
        [
            (x - min_x) / (max_x - min_x) if max_x != min_x else 0.5,
            (y - min_y) / (max_y - min_y) if max_y != min_y else 0.5,
            (z - min_z) / (max_z - min_z) if max_z != min_z else 0.5
        ]
        for x, y, z in zip(x_coords, y_coords, z_coords)
    ]
    return normalized_coords

def filter_model_coordinates(model_coords):
    return [model_coords[i] for i in range(0,33) if i < len(model_coords)]

def extract_video_coordinates(image_data):
    img_bytes = base64.b64decode(image_data.split(',')[1])
    img = Image.open(io.BytesIO(img_bytes))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        results = pose.process(img)

    video_coordinates = []
    if results.pose_landmarks:
        video_coordinates = [[landmark.x, landmark.y, landmark.z] for landmark in results.pose_landmarks.landmark]

    return video_coordinates

@app.route('/coordinates', methods=['POST'])
def receive_coordinates():
    data = request.get_json()
    image_data = data.get('image', '')
    model_coordinates = data.get('modelCoordinates', [])

    video_coordinates = extract_video_coordinates(image_data)
    
    normalized_video_coords = normalize_coordinates(video_coordinates)
    normalized_model_coords = normalize_coordinates(model_coordinates)

    filtered_model_coords = filter_model_coordinates(normalized_model_coords)

    print("Normalized video coordinates:", normalized_video_coords)
    print("Filtered model coordinates:", filtered_model_coords)
    similarity_percentage =95

    # Commenting out similarity calculation for now
    # similarity_percentage = calculate_similarity(normalized_video_coords, filtered_model_coords)

    return jsonify({
        'filtered_model_coordinates': filtered_model_coords,
        'filtered_video_coordinates': normalized_video_coords,
        'similarity': similarity_percentage,
    })

if __name__ == '__main__':
    app.run(debug=True)
