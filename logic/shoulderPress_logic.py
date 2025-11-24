# logic/shoulderpress_logic.py
import mediapipe as mp
import pandas as pd
from .base_corrector import BaseCorrector
from .utils import calculate_angle

mp_pose = mp.solutions.pose

class ShoulderPressCorrector(BaseCorrector):
    """
    Analyzes shoulder press form using a robust, rule-based system
    focused on rep counting, depth, and forearm alignment.
    This implementation ignores the ML model.
    """
    def __init__(self):
        super().__init__()
        self.stage = "down" # Start with arms bent
        self.column_names = ['left_elbow_angle','right_elbow_angle','left_back_angle','right_back_angle'] # Not used, but here for compatibility

    def analyze_form(self, landmarks, model):
        # The 'model' argument is ignored.
        
        # --- 1. Get Landmark Coordinates ---
        try:
            # We only need the arm landmarks for this logic
            l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            
            l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            r_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            
            l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            r_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            r_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]

            l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            r_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

        except Exception as e:
            # A landmark was not visible, skip this frame
            return self.counter, "N/A", 0

        # --- 2. Calculate Key Angles and Positions ---
        elbow_angle = (calculate_angle(l_shoulder, l_elbow, l_wrist) + 
                       calculate_angle(r_shoulder, r_elbow, r_wrist)) / 2
        
        left_elbow_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
        right_elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
        left_back_angle = calculate_angle(l_shoulder, l_hip, l_knee)
        right_back_angle = calculate_angle(r_shoulder, r_hip, r_knee)
                       
        # Get Y (vertical) coordinates for rep counting
        wrist_y = (l_wrist[1] + r_wrist[1]) / 2
        shoulder_y = (l_shoulder[1] + r_shoulder[1]) / 2

        # Get X (horizontal) coordinates for forearm check
        l_elbow_x = l_elbow[0]
        l_wrist_x = l_wrist[0]
        r_elbow_x = r_elbow[0]
        r_wrist_x = r_wrist[0]

        # --- 3. Rep Counting & Form Feedback Logic ---
        
        # Set defaults for a good rep
        form_feedback = "Good Form"
        # accuracy = 100

        # --- CHECK 1: Rep Counting ---
        # "Down" state: Arm is bent (e.g., < 100 degrees)
        if elbow_angle < 100:
            self.stage = "down"
            
        # "Up" state: Arm is straight AND wrist is physically above shoulder
        if self.stage == 'down' and elbow_angle > 160 and wrist_y < shoulder_y:
            self.stage = "up"
            self.counter += 1
            form_feedback = "Good Rep"

        # --- CHECK 2: Form Correction (Prioritized) ---
        
        # We only check for form errors when the user is at the bottom of the rep
        if self.stage == "down" or (self.stage == "up" and elbow_angle < 100): # Catches user at the bottom
            
            # Error 1: Not going deep enough
            if elbow_angle > 100: # 90-100 degrees is a good bottom position
                form_feedback = "Go Deeper"
                # accuracy = 75
            
            # Error 2: Elbow Flare / Arms "Too Wide" / Forearms not vertical
            # We check the horizontal distance between wrist and elbow.
            # A small tolerance is allowed.
            
            # Calculate the horizontal flare distance for each arm
            left_forearm_flare = abs(l_wrist_x - l_elbow_x)
            right_forearm_flare = abs(r_wrist_x - r_elbow_x)
            
            # Set a tolerance (e.g., 0.08 = 8% of screen width)
            # You can adjust this value to be stricter or looser
            FLARE_TOLERANCE = 0.08 

            if left_forearm_flare > FLARE_TOLERANCE or right_forearm_flare > FLARE_TOLERANCE:
                form_feedback = "Keep Forearms Vertical" # This feedback covers both errors
                # accuracy = 60 # Penalize for bad alignment

        # Error 3: Incomplete rep at the top
        elif self.stage == "up" and elbow_angle < 160:
            form_feedback = "Lock Out Arms"
            # accuracy = 85
        accuracy = 0
        if model:
            try:
                # Create the feature row using the calculated angles
                row = [left_elbow_angle, right_elbow_angle, left_back_angle, right_back_angle ]
                X = pd.DataFrame([row], columns=self.column_names)
                
                prediction_proba = model.predict_proba(X)[0]
                class_names = [name.lower().replace('_', '') for name in list(model.classes_)]
                if 'goodform' in class_names:
                    good_form_index = class_names.index('goodform')
                    accuracy = int(prediction_proba[good_form_index] * 100)
                else:
                    accuracy = int(max(prediction_proba) * 100)
            except Exception as e:
                print(f"ShoulderPress model error: {e}")
                accuracy = 0

        return self.counter, form_feedback, accuracy