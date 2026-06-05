import glob
import re
import os

def get_next_index(folder="data/yolo", prefix="output", extension="jpg"):
    ext = extension.lstrip(".")
    files = glob.glob(os.path.join(folder, f"{prefix}_*.{ext}"))
    indices = []
    for f in files:
        match = re.search(rf"{prefix}_(\d+)\.{ext}$", os.path.basename(f))
        if match:
            indices.append(int(match.group(1)))
    return max(indices, default=-1) + 1


import matplotlib.pyplot as plt

def plot_history(history, save_path):
    h = history.history
    epochs = range(1, len(h["loss"]) + 1)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Accuracy
    axes[0].plot(epochs, h["accuracy"], label="train")
    axes[0].plot(epochs, h["val_accuracy"], label="val")
    axes[0].set_title("Accuracy")
    axes[0].set_xlabel("Epoch")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Loss
    axes[1].plot(epochs, h["loss"], label="train")
    axes[1].plot(epochs, h["val_loss"], label="val")
    axes[1].set_title("Loss")
    axes[1].set_xlabel("Epoch")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

    print(f"Saved training plot -> {save_path}")