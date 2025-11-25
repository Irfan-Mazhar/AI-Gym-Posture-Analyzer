import mediapipe as mp
import pandas as pd
from .base_corrector import BaseCorrector
from .utils import calculate_angle

mp_pose = mp.solutions.pose

class ShoulderPressCorrector(BaseCorrector):
    def __init__(self):
        super().__init__()
        self.stage = "down"
        self.column_names = [
            'left_elbow_angle', 'right_elbow_angle',
            'left_back_angle', 'right_back_angle'
        ]
        # --- NEW: State for smart motion detection ---
        self.prev_elbow_angle = 0 

    def analyze_form(self, landmarks, model):
        form_feedback = "N/A"
        accuracy = 0
        penalty = 0

        # --- 1. Calculate all angles and coordinates ---
        try:
            l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            r_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            r_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            r_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            r_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # Calculate Angles
            left_elbow_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
            right_elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
            left_shoulder_angle = calculate_angle(l_hip, l_shoulder, l_elbow)
            right_shoulder_angle = calculate_angle(r_hip, r_shoulder, r_elbow)
            left_back_angle = calculate_angle(l_shoulder, l_hip, l_knee) 
            right_back_angle = calculate_angle(r_shoulder, r_hip, r_knee)
            
            # Average angles for stability
            # avg_back_angle = (left_hip_angle + right_hip_angle) / 2
            elbow_angle_avg = (left_elbow_angle + right_elbow_angle) / 2
            shoulder_angle_avg = (left_shoulder_angle + right_shoulder_angle) / 2
            
            # Coordinates for Flare Check
            l_elbow_x = l_elbow[0]
            l_wrist_x = l_wrist[0]
            r_elbow_x = r_elbow[0]
            r_wrist_x = r_wrist[0]

            # Coordinates for Rep Counting
            wrist_y_avg = (l_wrist[1] + r_wrist[1]) / 2
            shoulder_y_avg = (l_shoulder[1] + r_shoulder[1]) / 2
            
        except Exception as e:
            return self.counter, "N/A", 0

        # --- 2. Motion Detection Logic ---
        # Positive diff = Opening arms (Pushing Up)
        # Negative diff = Closing arms (Coming Down)
        # We use a small threshold (0.5) to filter out jitter
        is_pushing_up = (elbow_angle_avg - self.prev_elbow_angle) > 0.5
        is_coming_down = (self.prev_elbow_angle - elbow_angle_avg) > 0.5

        form_feedback = "Good Form"

        # --- 3. Rep Counting ---
        if elbow_angle_avg < 100: 
            self.stage = "down"
            
        # Arm straight AND overhead
        if self.stage == 'down' and elbow_angle_avg > 160 and wrist_y_avg < shoulder_y_avg:
            self.stage = "up"
            self.counter += 1
        
        # --- 4. Smart Rule-Based Feedback ---
    

        # Rule 2: Elbow Flare (Check continuously)
        left_flare = abs(l_elbow_x - l_wrist_x)
        right_flare = abs(r_elbow_x - r_wrist_x)
        if left_flare > 0.15 or right_flare > 0.15:
            form_feedback = "Keep Forearms Vertical"
            penalty += 20

        # Rule 3: Range of Motion (With Motion Detection)
        if form_feedback == "Good Form": # Only check ROM if form is otherwise good
            
            # Case A: User should be going UP (Locking out)
            # If we are in 'down' stage (rep started) but haven't reached top
            if self.stage == "down" and elbow_angle_avg < 160:
                if elbow_angle_avg > 100: # Past the start point
                    if not is_pushing_up:
                        # User has stalled in the middle of pressing
                        form_feedback = "Lock Out Arms"
                        penalty += 15
            
            # Case B: User should be going DOWN (Resetting)
            # If we are in 'up' stage (rep finished) but haven't reached bottom
            elif self.stage == "up" and shoulder_angle_avg > 90:
                 if not is_coming_down:
                     # User is holding the weight up or stalled coming down
                     form_feedback = "Go Deeper"
                     penalty += 15

        # Update previous angle for next frame
        self.prev_elbow_angle = elbow_angle_avg

        # --- 5. ML Model Prediction (ACCURACY ONLY) ---
        accuracy = max(0, 100 - penalty)
        # if model:
        #     try:
        #         row = [
        #             left_elbow_angle, right_elbow_angle,
        #             left_back_angle, right_back_angle
        #         ]
        #         X = pd.DataFrame([row], columns=self.column_names)
        #         prediction_proba = model.predict_proba(X)[0]
                
        #         class_names = [name.lower().replace('_', '') for name in list(model.classes_)]
        #         if 'goodform' in class_names:
        #             good_form_index = class_names.index('goodform')
        #             # accuracy = int(prediction_proba[good_form_index] * 100)
        #         # else:
        #             # accuracy = int(max(prediction_proba) * 100)
                
        #         # Apply Penalty from rules
        #         # accuracy = max(0, accuracy - penalty)
                
        #         # Smooth the result (Assuming BaseCorrector has this method)
        #         # accuracy = self.smooth_accuracy(accuracy)
                
        #     except Exception as e:
        #         print(f"ShoulderPress model error: {e}")
        #         accuracy = 0
        
        return self.counter, form_feedback, accuracy