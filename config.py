from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
KAGGLE_DATA_DIR = RAW_DATA_DIR / "kaggle"
OWN_IMAGES_DIR = RAW_DATA_DIR / "own_images"

PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
TRAIN_DIR = PROCESSED_DATA_DIR / "train"
VAL_DIR = PROCESSED_DATA_DIR / "val"
TEST_DIR = PROCESSED_DATA_DIR / "test"

MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "freshness_model.keras"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42

CLASS_NAMES = ["fresh", "spoiled"]

