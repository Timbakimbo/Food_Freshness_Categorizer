import tensorflow as tf
from keras import layers
from keras.applications import MobileNetV2, ResNet50V2, MobileNetV3Large, EfficientNetV2S
from keras.utils import image_dataset_from_directory
from keras.applications.mobilenet_v2 import preprocess_input
from util import plot_history

IMG_SIZE = (224, 224)
BATCH_SIZE = 8
EPOCHS = 10

# -----------------------------
# DATASETS
# -----------------------------

train_dataset = image_dataset_from_directory(
    "data/train",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
    shuffle=True
)

val_dataset = image_dataset_from_directory(
    "data/val",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
    shuffle=False
)

class_names = train_dataset.class_names
print("Classes:", class_names)

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.prefetch(buffer_size=AUTOTUNE)
val_dataset = val_dataset.prefetch(buffer_size=AUTOTUNE)

# -----------------------------
# BASE MODEL: https://keras.io/api/applications/ 
# -----------------------------

base_model = MobileNetV2(
    name="mobilenet_v2",
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

base_model.trainable = False

# -----------------------------
# MODEL
# -----------------------------

inputs = tf.keras.Input(shape=(224, 224, 3))

x = preprocess_input(inputs)

x = base_model(x, training=False)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dropout(0.2)(x)

outputs = layers.Dense(1, activation="sigmoid")(x)

model = tf.keras.Model(inputs, outputs)

# -----------------------------
# COMPILE
# -----------------------------
# TODO: Checkpoints und Fine-tuning mit Callbacks etc.
# https://keras.io/api/callbacks/model_checkpoint/

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# -----------------------------
# TRAIN
# -----------------------------

history = model.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=EPOCHS
)

# -----------------------------
# SAVE
# -----------------------------

model.save(f"models/{base_model.name}_classifier.keras")
keys = history.history
log_text = f"""
=== Training completed. ===
Model: {base_model.name}
Dataset: {len(train_dataset) * BATCH_SIZE} train samples, {len(val_dataset) * BATCH_SIZE} val samples
Epochs: {history.params['epochs']} | Steps per epoch: {history.params['steps']}
Total training time: {len(keys['loss'])} epochs

Final training loss: {keys['loss'][-1]:.4f}
Final training accuracy: {keys['accuracy'][-1]:.4f}

Final validation loss: {keys['val_loss'][-1]:.4f}
Final validation accuracy: {keys['val_accuracy'][-1]:.4f}
"""

print(log_text)
plot_history(history, save_path=f"logs/{base_model.name}_history_plot.png")

with open(f"logs/training.log", "a") as f:
    f.write(log_text)
    print(f"Saved training log → logs/training.log")
    