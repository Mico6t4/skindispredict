import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
import os

# Load the pre-trained model
try:
    model = load_model('predictions/model/skin_disease_classifier.h5')  # Update with the correct path to your model
except Exception as e:
    raise RuntimeError(f"Error loading the model: {str(e)}")

# Define categories (make sure these match the training data's classes)
categories = [
    'BA- cellulitis',
    'BA-impetigo',
    'FU-athlete-foot',
    'FU-nail-fungus',
    'FU-ringworm',
    'PA-cutaneous-larva-migrans',
    'VI-chickenpox',
    'VI-shingles'
]

# Function to preprocess an image
def prepare_image(image_path):
    """
    Preprocess the image for the MobileNetV2 model.
    - Load the image with target size 224x224.
    - Convert it to an array and preprocess it.
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError("The image file was not found.")

        # Load the image with the target size
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img)
        
        # Expand dimensions to match model input and preprocess
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        return img_array
    except Exception as e:
        raise ValueError(f"Error processing the image: {str(e)}")

# Function to make predictions
def predict_image(image_path):
    """
    Predict the class of the image.
    - Preprocess the image.
    - Predict using the model.
    - Return predicted class and confidence.
    """
    try:
        # Preprocess the image
        img_array = prepare_image(image_path)
        
        # Get predictions
        predictions = model.predict(img_array)
        
        # Determine the predicted class and confidence
        predicted_class_index = np.argmax(predictions)
        confidence = predictions[0][predicted_class_index]
        predicted_class = categories[predicted_class_index]

        # Validate the predicted class
        if predicted_class not in categories:
            raise ValueError(f"Invalid class detected: {predicted_class}. Please check the image or model.")

        return predicted_class, confidence
    except Exception as e:
        raise RuntimeError(f"Error during prediction: {str(e)}")
