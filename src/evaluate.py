import numpy as np
import tensorflow as tf
from keras.utils import image_dataset_from_directory
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    roc_curve,
    auc,
)

from util import get_next_index

IMG_SIZE = (224, 224)
BATCH_SIZE = 8
MODEL_PATH = "models/efficientnetv2-s_classifier.keras"
VAL_DIR    = "data/val"

# -----------------------------
# LOAD MODEL & DATASET
# -----------------------------

print(f"Loading model from '{MODEL_PATH}' ...")
model = tf.keras.models.load_model(MODEL_PATH)
model_name = MODEL_PATH.split("/")[-1].split("_")[0]

val_dataset = image_dataset_from_directory(
    VAL_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
    shuffle=False,
)

class_names = val_dataset.class_names
print("Classes:", class_names)

val_dataset = val_dataset.prefetch(buffer_size=tf.data.AUTOTUNE)

# -----------------------------
# COLLECT PREDICTIONS
# -----------------------------

print("\nRunning inference on validation set ...")

y_true = []
y_prob = []

for images, labels in val_dataset:
    probs = model.predict(images, verbose=0).flatten()
    y_prob.extend(probs.tolist())
    y_true.extend(labels.numpy().flatten().astype(int).tolist())

y_true = np.array(y_true)
y_prob = np.array(y_prob)
y_pred = (y_prob >= 0.5).astype(int)

# -----------------------------
# SCALAR METRICS
# -----------------------------

acc       = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, zero_division=0)
recall    = recall_score(y_true, y_pred, zero_division=0)
f1        = f1_score(y_true, y_pred, zero_division=0)

print(f"\n{'='*40}")
print(f"  Accuracy : {acc:.4f}")
print(f"  Precision: {precision:.4f}")
print(f"  Recall   : {recall:.4f}")
print(f"  F1-Score : {f1:.4f}")
print(f"{'='*40}")
print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))

# -----------------------------
# PLOTS
# -----------------------------

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle(f"Model Evaluation: {model_name}", fontsize=16, fontweight="bold")

# -- 1. Confusion Matrix --
ax = axes[0]
cm = confusion_matrix(y_true, y_pred)
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=class_names,
    yticklabels=class_names,
    ax=ax,
    linewidths=0.5,
)
ax.set_title("Confusion Matrix")
ax.set_xlabel("Predicted")
ax.set_ylabel("True")

# -- 2. Precision / Recall / F1 / Accuracy bar chart --
ax = axes[1]
metric_names  = ["Accuracy", "Precision", "Recall", "F1-Score"]
metric_values = [acc, precision, recall, f1]
colors = sns.color_palette("muted", len(metric_names))
bars = ax.bar(metric_names, metric_values, color=colors, edgecolor="white", linewidth=0.8)
ax.set_ylim(0, 1.15)
ax.set_title("Classification Metrics")
ax.set_ylabel("Score")
for bar, val in zip(bars, metric_values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.02,
        f"{val:.3f}",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )
ax.grid(axis="y", alpha=0.3)

# -- 3. ROC Curve --
ax = axes[2]
fpr, tpr, _ = roc_curve(y_true, y_prob)
roc_auc = auc(fpr, tpr)
ax.plot(fpr, tpr, color="#4C72B0", lw=2, label=f"ROC (AUC = {roc_auc:.4f})")
ax.plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1, label="Random classifier")
ax.fill_between(fpr, tpr, alpha=0.08, color="#4C72B0")
ax.set_title("ROC Curve")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.legend(loc="lower right")
ax.grid(alpha=0.3)

plt.tight_layout()

i = get_next_index(folder="logs", prefix="evaluation", extension="png")
output_path = f"logs/evaluation_{model_name}_{i}.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"\nEvaluation plot saved → {output_path}")
plt.show()