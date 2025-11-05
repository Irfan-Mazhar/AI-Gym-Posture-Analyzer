# logic/pushup_logic.py
import mediapipe as mp
import pandas as pd
from .base_corrector import BaseCorrector
from .utils import calculate_angle

mp_pose = mp.solutions.pose

class PushupCorrector(BaseCorrector):
    def __init__(self):
        super().__init__()
        # 1. Define the angle columns your new model was trained on
        self.column_names = ['left_elbow_angle', 'right_elbow_angle', 'left_hip_angle', 'right_hip_angle']

    def analyze_form(self, landmarks, model):
        # --- 1. Calculate all angles ---
        try:
            l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            r_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            r_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            r_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            r_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # Calculate the angles
            left_elbow_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
            right_elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
            left_hip_angle = calculate_angle(l_shoulder, l_hip, l_ankle) # Back angle
            right_hip_angle = calculate_angle(r_shoulder, r_hip, r_ankle) # Back angle
        except Exception as e:
            return self.counter, "N/A", 0

        # --- 2. Rep Counting ---
        elbow_angle_avg = (left_elbow_angle + right_elbow_angle) / 2
        if elbow_angle_avg > 160: self.stage = "up"
        if self.stage == 'up' and elbow_angle_avg < 90:
            self.stage = "down"
            self.counter += 1
        
        # --- 3. ML Model (Angle-Based) for Form/Accuracy ---
        form_feedback = "N/A"
        accuracy = 0
        if model:
            try:
                # Create the feature row using the calculated angles
                row = [left_elbow_angle, right_elbow_angle, left_hip_angle, right_hip_angle]
                X = pd.DataFrame([row], columns=self.column_names)
                
                prediction_class = model.predict(X)[0]
                prediction_proba = model.predict_proba(X)[0]
                form_feedback = prediction_class.replace('_', ' ').title()
                
                class_names = [name.lower().replace('_', '') for name in list(model.classes_)]
                if 'goodform' in class_names:
                    good_form_index = class_names.index('goodform')
                    accuracy = int(prediction_proba[good_form_index] * 100)
                else:
                    accuracy = int(max(prediction_proba) * 100)
            except Exception as e:
                print(f"Pushup model error: {e}")
                form_feedback = "Error"
                accuracy = 0
        
        return self.counter, form_feedback, accuracy