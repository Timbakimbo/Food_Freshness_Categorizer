from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

from config import DEFAULT_TRAIN_CONFIG, TrainConfig


def predict_image(model: tf.keras.Model, image_path: Path, image_size: tuple[int, int], threshold: float = 0.5) -> dict[str, float | str]:
    loaded = image.load_img(image_path, target_size=image_size)
    array = image.img_to_array(loaded)
    array = np.expand_dims(array, axis=0)
    probability_non_edible = float(model.predict(array, verbose=0)[0][0])
    if probability_non_edible >= threshold:
        label = "non_edible"
        confidence = probability_non_edible
    else:
        label = "edible"
        confidence = 1.0 - probability_non_edible
    return {
        "label": label,
        "confidence": confidence,
        "probability_non_edible": probability_non_edible,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict food freshness from a single image.")
    parser.add_argument("image_path", type=Path)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_TRAIN_CONFIG.model_path)
    parser.add_argument("--threshold", type=float, default=0.35)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = TrainConfig(model_path=args.model_path)
    model = tf.keras.models.load_model(config.model_path)
    result = predict_image(model, args.image_path, config.image_size, threshold=args.threshold)
    print(f"Prediction: {result['label']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Probability non_edible: {result['probability_non_edible']:.4f}")


if __name__ == "__main__":
    main()
