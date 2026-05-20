from pathlib import Path
import shutil
import random
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_ZIP_EXTRACTED_DIR = BASE_DIR / "data" / "raw" / "banana_dataset"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

LABEL_MAP = {
    "Fresh": "fresh",
    "Rotten": "spoiled",
}

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

SEED = 42


def collect_images():
    image_records = []

    for freshness_label, target_label in LABEL_MAP.items():
        label_dir = RAW_ZIP_EXTRACTED_DIR / "Banana" / freshness_label

        if not label_dir.exists():
            raise FileNotFoundError(f"Missing folder: {label_dir}")

        for image_path in label_dir.rglob("*"):
            if image_path.suffix.lower() in IMAGE_EXTENSIONS:
                image_records.append((image_path, target_label))

    return image_records


def is_valid_image(image_path):
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def clear_processed_dir():
    if PROCESSED_DIR.exists():
        shutil.rmtree(PROCESSED_DIR)

    for split in ["train", "val", "test"]:
        for label in ["fresh", "spoiled"]:
            (PROCESSED_DIR / split / label).mkdir(parents=True, exist_ok=True)


def split_images(image_records):
    random.seed(SEED)

    by_label = {}
    for image_path, label in image_records:
        by_label.setdefault(label, []).append(image_path)

    split_result = {
        "train": [],
        "val": [],
        "test": [],
    }

    for label, paths in by_label.items():
        random.shuffle(paths)

        n = len(paths)
        n_train = int(n * TRAIN_RATIO)
        n_val = int(n * VAL_RATIO)

        train_paths = paths[:n_train]
        val_paths = paths[n_train:n_train + n_val]
        test_paths = paths[n_train + n_val:]

        split_result["train"].extend((p, label) for p in train_paths)
        split_result["val"].extend((p, label) for p in val_paths)
        split_result["test"].extend((p, label) for p in test_paths)

    return split_result


def copy_images(split_result):
    for split, records in split_result.items():
        for idx, (src_path, label) in enumerate(records):
            target_dir = PROCESSED_DIR / split / label
            target_name = f"{label}_{idx:04d}{src_path.suffix.lower()}"
            target_path = target_dir / target_name
            shutil.copy2(src_path, target_path)


def print_summary():
    print("\nDataset summary:")
    for split in ["train", "val", "test"]:
        for label in ["fresh", "spoiled"]:
            folder = PROCESSED_DIR / split / label
            count = len(list(folder.glob("*")))
            print(f"{split:5s} | {label:7s}: {count}")


def main():
    image_records = collect_images()

    valid_records = []
    invalid_images = []

    for image_path, label in image_records:
        if is_valid_image(image_path):
            valid_records.append((image_path, label))
        else:
            invalid_images.append(image_path)

    print(f"Found images: {len(image_records)}")
    print(f"Valid images: {len(valid_records)}")
    print(f"Invalid images: {len(invalid_images)}")

    clear_processed_dir()
    split_result = split_images(valid_records)
    copy_images(split_result)
    print_summary()


if __name__ == "__main__":
    main()