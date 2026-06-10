from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "reports"
GENERATED_DIR = PROJECT_ROOT / "generated"
BACKGROUND_AUG_DIR = GENERATED_DIR / "background_aug"
BACKGROUND_LIBRARY_DIR = GENERATED_DIR / "background_library"
RAW_SOURCES = {
    "edible": PROJECT_ROOT / "dataset_cat1",
    "non_edible": PROJECT_ROOT / "dataset_cat2",
}
STRUCTURED_SOURCES = [
    DATA_DIR / "train",
    DATA_DIR / "val",
]
ALLOWED_CATEGORIES = (
    "erdbeere",
    "banane",
    "paprika",
    "orange",
    "gurke",
    "zitrone",
)
LABELS = ("edible", "non_edible")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic"}
CATEGORY_ALIASES = {
    "erdbeere": ("erdbeere", "strawberry"),
    "banane": ("banane", "banana"),
    "paprika": ("paprika", "pepper"),
    "orange": ("orange",),
    "gurke": ("gurke", "cucumber"),
    "zitrone": ("zitrone", "lemon"),
}


@dataclass(frozen=True)
class DataConfig:
    raw_sources: dict[str, Path] = field(default_factory=lambda: RAW_SOURCES.copy())
    structured_sources: tuple[Path, ...] = field(default_factory=lambda: STRUCTURED_SOURCES)
    background_aug_dir: Path = BACKGROUND_AUG_DIR
    output_dir: Path = DATA_DIR
    labels: tuple[str, str] = LABELS
    allowed_categories: tuple[str, ...] = ALLOWED_CATEGORIES
    image_extensions: set[str] = field(default_factory=lambda: IMAGE_EXTENSIONS.copy())
    val_fraction: float = 0.2
    random_seed: int = 42
    near_duplicate_threshold: int = 4
    remove_loose_root_files: bool = False


@dataclass(frozen=True)
class TrainConfig:
    image_size: tuple[int, int] = (224, 224)
    batch_size: int = 8
    epochs: int = 10
    learning_rate: float = 1e-3
    dropout_rate: float = 0.2
    random_seed: int = 42
    model_path: Path = MODEL_DIR / "food_freshness_mobilenetv2.keras"
    report_dir: Path = REPORT_DIR
    data_dir: Path = DATA_DIR
    experiment_name: str = "baseline"
    augmentation_mode: str = "none"
    early_stopping_patience: int = 3
    reduce_lr_patience: int = 2
    min_learning_rate: float = 1e-5
    use_class_weights: bool = True


DEFAULT_DATA_CONFIG = DataConfig()
DEFAULT_TRAIN_CONFIG = TrainConfig()
