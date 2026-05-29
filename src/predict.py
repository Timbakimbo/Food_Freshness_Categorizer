import sys
import numpy as np
import tensorflow as tf
import PIL.Image as Image
from tensorflow.keras.preprocessing import image

IMG_SIZE = (224, 224)
MODEL_PATH = "models/classifier.keras"

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:   
    print(f"Error loading model: {e}")
    sys.exit(1) 
    
# Streamlit integration -> need a function
def predict_image(image_path):
    try:
        if isinstance(image_path, Image.Image):
            img = image_path.resize(IMG_SIZE)
        else:
            img = image.load_img(image_path, target_size=IMG_SIZE)
        
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        prediction = model.predict(x)[0][0]
    except Exception as e:
        print(f"Error processing image: {e}")
        return "error", 0.0, 0.0
    
    if prediction >= 0.5:
        label = "non_edible"
        confidence = float(prediction)
    else:
        label = "edible"
        confidence = float(1 - prediction)
    
    return label, confidence, float(prediction)