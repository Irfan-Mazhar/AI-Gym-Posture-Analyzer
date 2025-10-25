# app.py
from flask import Flask, Response, stream_with_context, jsonify, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
import cv2
import mediapipe as mp
import json
import time
import importlib
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# Load environment variables from .env file
load_dotenv()

# Your modular imports
from model_loader import load_models_and_encoder
from auth import token_required
from db import mongo

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# --- Configuration for Database and JWT ---
# Reads the MONGO_URI and SECRET_KEY from your .env file
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Initialize the database connection
mongo.init_app(app)

# --- Global Variables ---
models, label_encoder = load_models_and_encoder()
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
cap = None
active_exercise = None
corrector = None
latest_data = {"reps": 0, "form": "N/A", "accuracy": 0}

EXERCISE_MAP = {
    "squats": ("logic.squat_logic", "SquatCorrector"),
    "pushups": ("logic.pushup_logic", "PushupCorrector"),
    "curls": ("logic.curls_logic", "CurlsCorrector"),
    "shoulder_press": ("logic.shoulderPress_logic", "ShoulderPressCorrector"),
}

# --- User Authentication Routes ---
# @app.route('/userDetails',methods=['GET'])
# def getUserDetails():

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    age = data.get('age')
    height = data.get('height')
    weight = data.get('weight')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if mongo.db.users.find_one({'username': username}):
        return jsonify({'message': 'User already exists'}), 409

    heightInMeter = (int(height)/100)
    bmi = int(weight)/(heightInMeter*heightInMeter)

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    mongo.db.users.insert_one({'username': username, 'password': hashed_password, 'created_at': datetime.utcnow(), 'age':age,'height':height,'weight':weight,'bmi':bmi})
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = mongo.db.users.find_one({'username': username})

    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid username or password'}), 401

    token = jwt.encode({
        'sub': user['username'],
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    # This is an example of a protected route
    # print('user_data:',current_user)
    return jsonify({
        'message': f'Welcome {current_user["username"]}!',
        'user_data': current_user
    })

# --- Exercise Analysis Routes ---

# @app.route('/start_exercise/<exercise_name>', methods=['POST'])
# def start_exercise(exercise_name):
#     global active_exercise, corrector, latest_data
#     active_exercise = exercise_name.lower()
#     if active_exercise in EXERCISE_MAP:
#         try:
#             latest_data = {"reps": 0, "form": "N/A", "accuracy": 0}
#             module_name, class_name = EXERCISE_MAP[active_exercise]
#             ExerciseModule = importlib.import_module(module_name)
#             CorrectorClass = getattr(ExerciseModule, class_name)
#             corrector = CorrectorClass()
#             print(f"Successfully started exercise: {active_exercise}")
#             return jsonify({"status": f"{active_exercise} session started"}), 200
#         except Exception as e:
#             print(f"Error starting exercise '{active_exercise}': {e}")
#             return jsonify({"status": "Error initializing exercise"}), 500
#     return jsonify({"status": f"Exercise '{active_exercise}' not found"}), 404

ALL_LANDMARKS_INDICES = list(range(33))
classifier_column_names = []
for idx in ALL_LANDMARKS_INDICES:
    name = mp_pose.PoseLandmark(idx).name
    classifier_column_names.extend([f'{name.lower()}_x', f'{name.lower()}_y', f'{name.lower()}_z', f'{name.lower()}_visibility'])

def video_generator():
    global cap, latest_data, corrector, active_exercise, models, label_encoder
    cap = cv2.VideoCapture(0)

    last_predicted_exercise = None
    prediction_streak = 0
    STABILITY_THRESHOLD = 30 # You can adjust this

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap and cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            detected_exercise_str = None

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # --- 1. Run Exercise Classifier ---
                classifier_model = models.get('classifier')
                if classifier_model and label_encoder:
                    try:
                        row = []
                        for idx in ALL_LANDMARKS_INDICES:
                            lm = landmarks[idx]
                            row.extend([lm.x, lm.y, lm.z, lm.visibility])
                        X = pd.DataFrame([row], columns=classifier_column_names)

                        # Predict the number (e.g., 2)
                        prediction_encoded = classifier_model.predict(X)[0]

                        # --- FIX: Calculate probabilities BEFORE trying to print them ---
                        prediction_proba = classifier_model.predict_proba(X)[0]

                        # Decode the number back to a string (e.g., 2 -> 'shoulderpress')
                        detected_exercise_str = label_encoder.inverse_transform([prediction_encoded])[0]

                        # --- DEBUG PRINTS (Now working correctly) ---
                        print("-" * 20)
                        print(f"Raw Prediction: {detected_exercise_str} (Index: {prediction_encoded})")
                        all_probs = {label_encoder.inverse_transform([i])[0]: f"{prob:.2f}" for i, prob in enumerate(prediction_proba)}
                        print(f"Probabilities: {all_probs}")
                        # --- END DEBUG ---

                    except Exception as e:
                        print(f"Classifier error: {e}") # Keep this active
                        pass

                # --- Stability Logic (uses detected_exercise_str) ---
                if detected_exercise_str:
                    if detected_exercise_str == last_predicted_exercise:
                        prediction_streak += 1
                    else:
                        last_predicted_exercise = detected_exercise_str
                        prediction_streak = 1

                    if prediction_streak >= STABILITY_THRESHOLD:
                        if detected_exercise_str != active_exercise:
                            active_exercise = detected_exercise_str
                            if active_exercise in EXERCISE_MAP:
                                try:
                                    module_name, class_name = EXERCISE_MAP[active_exercise]
                                    ExerciseModule = importlib.import_module(module_name)
                                    CorrectorClass = getattr(ExerciseModule, class_name)
                                    corrector = CorrectorClass()
                                    print(f"--- Switched to Exercise: {active_exercise} ---")
                                    latest_data = {"reps": 0, "form": "N/A", "accuracy": 0}
                                except Exception as e:
                                    print(f"Error switching corrector: {e}")
                                    corrector = None
                            else:
                                print(f"Warning: Corrector logic not found for '{active_exercise}'")
                                corrector = None
                else:
                    prediction_streak = 0
                    last_predicted_exercise = None
                    # active_exercise = None # Optional reset
                    # corrector = None       # Optional reset


                # --- 2. Run Form Analysis ---
                if corrector and active_exercise:
                    try:
                        reps, form, acc = corrector.analyze_form(landmarks, models.get(active_exercise))
                        latest_data = {"reps": reps, "form": form, "accuracy": acc, "exercise": active_exercise}
                    except Exception as e:
                        print(f"Analysis error for {active_exercise}: {e}") # Keep this active too
                        pass
                else:
                    latest_data = {"reps": 0, "form": "Waiting...", "accuracy": 0, "exercise": "Detecting..."}

            # --- Draw landmarks and yield frame ---
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    if cap: cap.release()

def data_generator():
    while True:
        yield f"data:{json.dumps(latest_data)}\n\n"
        time.sleep(0.1)

@app.route('/video')
def video():
    return Response(stream_with_context(video_generator()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def data():
    return Response(data_generator(), mimetype='text/event-stream')

@app.route('/stop', methods=['POST'])
def stop():
    global cap, corrector, active_exercise
    if cap is not None: cap = None
    corrector = None
    active_exercise = None
    return jsonify({"status": "session stopped"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=True, use_reloader=False)