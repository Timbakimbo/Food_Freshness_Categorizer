import argparse

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from src.config import BATCH_SIZE, IMAGE_SIZE, MODEL_DIR, MODEL_PATH, SEED, TRAIN_DIR, VAL_DIR


def load_datasets() -> tuple[tf.data.Dataset, tf.data.Dataset]:
    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="binary",
        seed=SEED,
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        VAL_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="binary",
        seed=SEED,
    )

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.shuffle(1000, seed=SEED).prefetch(autotune)
    val_ds = val_ds.prefetch(autotune)

    return train_ds, val_ds


def build_baseline_model() -> tf.keras.Model:
    model = models.Sequential(
        [
            layers.Rescaling(1.0 / 255, input_shape=(*IMAGE_SIZE, 3)),
            layers.Conv2D(32, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    return model


def build_mobilenet_model() -> tf.keras.Model:
    data_augmentation = tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
            layers.RandomContrast(0.1),
        ],
        name="data_augmentation",
    )

    base_model = MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    inputs = layers.Input(shape=(*IMAGE_SIZE, 3))
    x = data_augmentation(inputs)
    x = preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)

    model = models.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    return model


def train(model_type: str, epochs: int) -> None:
    train_ds, val_ds = load_datasets()

    if model_type == "baseline":
        model = build_baseline_model()
    elif model_type == "mobilenet":
        model = build_mobilenet_model()
    else:
        raise ValueError("model_type must be 'baseline' or 'mobilenet'.")

    model.summary()
    model.fit(train_ds, validation_data=val_ds, epochs=epochs)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a food freshness classifier.")
    parser.add_argument("--model", choices=["baseline", "mobilenet"], default="mobilenet")
    parser.add_argument("--epochs", type=int, default=10)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train(model_type=args.model, epochs=args.epochs)

