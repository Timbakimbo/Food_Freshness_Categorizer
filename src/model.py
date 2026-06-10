from __future__ import annotations

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from config import TrainConfig


def build_model(config: TrainConfig) -> tf.keras.Model:
    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(*config.image_size, 3),
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(*config.image_size, 3))
    x = preprocess_input(inputs)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(config.dropout_rate)(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=config.learning_rate),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )
    return model


def build_augmentation(mode: str) -> tf.keras.Sequential | None:
    if mode == "none":
        return None
    if mode == "standard":
        return tf.keras.Sequential(
            [
                layers.RandomFlip("horizontal"),
                layers.RandomRotation(0.05),
                layers.RandomZoom(0.1),
                layers.RandomContrast(0.1),
            ],
            name="standard_augmentation",
        )
    if mode == "background":
        return tf.keras.Sequential(
            [
                layers.RandomFlip("horizontal"),
                layers.RandomRotation(0.05),
                layers.RandomZoom(0.1),
                layers.RandomContrast(0.15),
                layers.RandomBrightness(0.15),
            ],
            name="background_ready_augmentation",
        )
    raise ValueError(f"Unsupported augmentation mode: {mode}")


def attach_augmentation(dataset: tf.data.Dataset, mode: str) -> tf.data.Dataset:
    augmenter = build_augmentation(mode)
    if augmenter is None:
        return dataset

    def augment(images: tf.Tensor, labels: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
        return augmenter(images, training=True), labels

    return dataset.map(augment, num_parallel_calls=tf.data.AUTOTUNE).prefetch(tf.data.AUTOTUNE)
