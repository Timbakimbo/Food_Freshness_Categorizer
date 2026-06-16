import argparse

import numpy as np
import tensorflow as tf
import PIL.Image as Image
from keras.utils import load_img, img_to_array

IMG_SIZE = (224, 224)
DEFAULT_MODEL_PATH = "models/freshify_baseline_with_new_raw.keras"
DEFAULT_THRESHOLD = 0.50


def load_model(model_path: str = DEFAULT_MODEL_PATH):
    return tf.keras.models.load_model(model_path)


_model = None


def get_model(model_path: str = DEFAULT_MODEL_PATH):
    global _model
    if _model is None:
        _model = load_model(model_path)
    return _model


def predict_image(image_path, model=None, threshold: float = DEFAULT_THRESHOLD):
    try:
        model = model or get_model()
        if isinstance(image_path, Image.Image):
            img = image_path.resize(IMG_SIZE)
        else:
            img = load_img(image_path, target_size=IMG_SIZE)

        x = img_to_array(img)
        x = np.expand_dims(x, axis=0)
        prediction = model.predict(x)[0][0]
    except Exception as e:
        print(f"Error processing image: {e}")
        return "error", 0.0, 0.0

    if prediction >= threshold:
        label = "non_edible"
        confidence = float(prediction)
    else:
        label = "edible"
        confidence = float(1 - prediction)

    return label, confidence, float(prediction)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify one food image as edible or non_edible.")
    parser.add_argument("image", help="Path to the image file.")
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH, help="Path to the Keras model.")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help="Decision threshold for non_edible.")
    args = parser.parse_args()

    model = load_model(args.model)
    label, confidence, probability_non_edible = predict_image(
        args.image,
        model=model,
        threshold=args.threshold,
    )

    print(f"label: {label}")
    print(f"confidence: {confidence:.4f}")
    print(f"probability_non_edible: {probability_non_edible:.4f}")
    print(f"threshold: {args.threshold:.2f}")


if __name__ == "__main__":
    main()
