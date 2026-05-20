import numpy as np
import tensorflow as tf
from PIL import Image

from src.config import IMAGE_SIZE, MODEL_PATH

_model: tf.keras.Model | None = None


def load_model() -> tf.keras.Model:
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No trained model found at {MODEL_PATH}. "
                "Train the model with 'python -m src.train_model' first."
            )
        _model = tf.keras.models.load_model(MODEL_PATH)

    return _model


def predict_freshness(image: Image.Image) -> tuple[str, float, str]:
    model = load_model()

    image = image.convert("RGB")
    image = image.resize(IMAGE_SIZE)

    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)

    probability_spoiled = float(model.predict(image_array, verbose=0)[0][0])

    if probability_spoiled >= 0.5:
        label = "spoiled"
        confidence = probability_spoiled
        recommendation = "Manuell pruefen oder aussortieren."
    else:
        label = "fresh"
        confidence = 1.0 - probability_spoiled
        recommendation = "Visuell unauffaellig; normale menschliche Kontrolle bleibt sinnvoll."

    return label, confidence, recommendation

