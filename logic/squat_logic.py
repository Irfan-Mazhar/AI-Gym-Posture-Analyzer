# logic/squat_logic.py
import mediapipe as mp
import pandas as pd
from .base_corrector import BaseCorrector
from .utils import calculate_angle

mp_pose = mp.solutions.pose

class SquatCorrector(BaseCorrector):
    def __init__(self):
        super().__init__()
        # 1. Define the angle columns your new model was trained on
        self.column_names = ['left_knee_angle', 'right_knee_angle', 'left_hip_angle', 'right_hip_angle']

    def analyze_form(self, landmarks, model):
        # --- 1. Calculate all angles ---
        try:
            l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            r_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            r_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            r_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

            # Calculate the angles
            left_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
            right_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
            left_hip_angle = calculate_angle(l_shoulder, l_hip, l_knee)
            right_hip_angle = calculate_angle(r_shoulder, r_hip, r_knee)
        except Exception as e:
            return self.counter, "N/A", 0

        # --- 2. Rep Counting & Rule-Based Feedback ---
        knee_angle_avg = (left_knee_angle + right_knee_angle) / 2
        hip_angle_avg = (left_hip_angle + right_hip_angle) / 2

        form_feedback = "Good Form"
        if hip_angle_avg > 160 and knee_angle_avg > 160: self.stage = "up"
        if self.stage == "up" and hip_angle_avg < 150: self.stage = "down"
        if self.stage == "down":
            if knee_angle_avg < 90: form_feedback = "Good Depth"
            else: form_feedback = "Go Deeper"
            if hip_angle_avg < 50: form_feedback = "Keep Chest Up"
        if self.stage == "down" and knee_angle_avg > 160:
            self.stage = "up"
            self.counter += 1
        
        # --- 3. ML Model (now angle-based) for Accuracy ---
        accuracy = 0
        if model:
            try:
                # Create the feature row using the calculated angles
                row = [left_knee_angle, right_knee_angle, left_hip_angle, right_hip_angle]
                X = pd.DataFrame([row], columns=self.column_names)
                
                prediction_proba = model.predict_proba(X)[0]
                class_names = [name.lower().replace('_', '') for name in list(model.classes_)]
                if 'goodform' in class_names:
                    good_form_index = class_names.index('goodform')
                    accuracy = int(prediction_proba[good_form_index] * 100)
                else:
                    accuracy = int(max(prediction_proba) * 100)
            except Exception as e:
                print(f"Squat model error: {e}")
                accuracy = 0
        
        return self.counter, form_feedback, accuracy