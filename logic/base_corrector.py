from abc import ABC, abstractmethod
from collections import deque

class BaseCorrector(ABC):
    def __init__(self):
        self.stage = "up"
        self.counter = 0
        self.landmarks_to_use = []
        self.column_names = []
        
        # Store last 5 frames
        self.accuracy_buffer = deque(maxlen=5)

    def smooth_accuracy(self, new_accuracy):
        """
        Calculates a smoothed average.
        """
        self.accuracy_buffer.append(new_accuracy)
        
        # Simple average
        avg = sum(self.accuracy_buffer) / len(self.accuracy_buffer)
        
        # Optional: Snap to nearest 5 for cleaner UI
        # snapped = 5 * round(avg / 5)
        
        return int(avg)

    @abstractmethod
    def analyze_form(self, landmarks, model):
        pass