# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score
# import pickle
# from xgboost import XGBClassifier

# # ==============================================================================
# # Step 1: Load Your Dataset
# # ==============================================================================
# # Make sure your CSV file is in the same directory as this script,
# # or provide the full path to it.
# CSV_PATH = '../data/pushups_form_angles.csv' 
# df = pd.read_csv(CSV_PATH)

# print("Dataset loaded successfully.")
# print("First 5 rows of the dataset:")
# print(df.head())
# print(f"\nDataset contains {len(df)} rows.")

# # ==============================================================================
# # Step 2: Prepare the Data
# # ==============================================================================
# # 'X' contains our features (all the landmark coordinates)
# # 'y' contains our labels (the 'class' column)
# X = df.drop('class', axis=1) 
# y = df['class']

# print("\nFeatures (X) and labels (y) have been separated.")

# # ==============================================================================
# # Step 3: Split Data into Training and Testing Sets
# # ==============================================================================
# # We'll use 80% of the data to train the model and 20% to test its performance.
# # random_state ensures that the split is the same every time you run the script.
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# print(f"Data split into training ({len(X_train)} rows) and testing ({len(X_test)} rows) sets.")

# # ==============================================================================
# # Step 4: Choose and Train the Model
# # ==============================================================================
# # We'll use a RandomForestClassifier, which is a powerful and reliable model for this kind of task.

# label_encoder = LabelEncoder()

# # Fit the encoder on the training labels AND transform them to numbers
# y_train_encoded = label_encoder.fit_transform(y_train)

# # ONLY transform the test labels using the SAME encoder
# y_test_encoded = label_encoder.transform(y_test)

# print(f"\nLabels encoded. Mapping: {dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))}")

# model = XGBClassifier(n_estimators=100, random_state=42,use_label_encoder=False, eval_metric='mlogloss')

# print("\nTraining the model...")
# # The .fit() function is where the model learns from your training data.
# model.fit(X_train, y_train_encoded)
# print("Model training complete! ✅")

# # ==============================================================================
# # Step 5: Evaluate the Model
# # ==============================================================================
# # Now we use the trained model to make predictions on the test data it has never seen before.
# y_pred_encoded = model.predict(X_test)

# # We compare the model's predictions (y_pred) to the actual correct labels (y_test).
# accuracy = accuracy_score(y_test_encoded, y_pred_encoded)
# print(f"\nModel Accuracy on Test Data: {accuracy * 100:.2f}%")

# # ==============================================================================
# # Step 6: Save the Trained Model
# # ==============================================================================
# # We save the trained model to a file using 'pickle'.
# # This allows us to load and use it in our Flask app without retraining.
# model_filename = 'pushups_new_model.pkl'
# with open(model_filename, 'wb') as f:
#     pickle.dump(model, f)

# encoder_filename = 'exercise_classifier_label_encoder.pkl'
# with open(encoder_filename, 'wb') as f:
#     pickle.dump(label_encoder, f)
# print(f"Label encoder saved successfully as '{encoder_filename}'! ✨")

# print(f"\nModel saved successfully as '{model_filename}'! ✨")
# print(f"Model classes found: {list(model.classes_)}")


import pandas as pd
from sklearn.model_selection import train_test_split
# No LabelEncoder needed
from sklearn.ensemble import RandomForestClassifier # Changed import
from sklearn.metrics import accuracy_score
import pickle
# from xgboost import XGBClassifier # No XGBoost needed

# ==============================================================================
# Step 1: Load Your Dataset
# ==============================================================================
# Make sure this points to your new ANGLE-BASED CSV
CSV_PATH = '../data/shoulder_press_form_angles.csv' # Example for pushups
df = pd.read_csv(CSV_PATH)

print("Dataset loaded successfully.")
print(f"\nDataset contains {len(df)} rows.")
print(f"Label distribution:\n{df['class'].value_counts()}")

# ==============================================================================
# Step 2: Prepare the Data
# ==============================================================================
X = df.drop('class', axis=1)
y = df['class'] # y is now the original string labels (e.g., 'good_form')

print("\nFeatures (X) and labels (y) have been separated.")

# ==============================================================================
# Step 3: Split Data into Training and Testing Sets
# ==============================================================================
# We train and test on the original string labels
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Data split into training ({len(X_train)} rows) and testing ({len(X_test)} rows) sets.")

# ==============================================================================
# Step 4: Choose and Train the Model
# ==============================================================================
# Switched to RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)

print("\nTraining the RandomForest model...")
# Train on the original string labels (y_train)
model.fit(X_train, y_train)
print("Model training complete! ✅")

# You can check the classes it learned (will be strings)
print(f"Model classes learned: {list(model.classes_)}")

# ==============================================================================
# Step 5: Evaluate the Model
# ==============================================================================
# Predict on the test set
y_pred = model.predict(X_test)

# Compare the string predictions (y_pred) with the original string test labels (y_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy on Test Data: {accuracy * 100:.2f}%") # Should still be high

# ==============================================================================
# Step 6: Save the Trained Model
# ==============================================================================
# Make sure to save with the correct filename that model_loader.py expects
model_filename = 'shoulderPress_form_model.pkl' # Example
with open(model_filename, 'wb') as f: # Saves directly to models folder
    pickle.dump(model, f)

print(f"\nModel saved successfully as './{model_filename}'! ✨")
# No encoder file is needed!