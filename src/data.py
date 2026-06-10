from __future__ import annotations

import argparse
import csv
import hashlib
import random
import shutil
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps

from config import CATEGORY_ALIASES, DEFAULT_DATA_CONFIG, DataConfig


@dataclass(frozen=True)
class ImageRecord:
    source_path: Path
    label: str
    category: str
    source_type: str
    sha256: str
    average_hash: int


@dataclass(frozen=True)
class SplitAssignment:
    record: ImageRecord
    split: str
    output_path: Path


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    tf.keras.utils.set_random_seed(seed)


def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_average_hash(path: Path, hash_size: int = 8) -> int:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("L").resize((hash_size, hash_size))
        pixels = np.asarray(image, dtype=np.float32)
    avg = pixels.mean()
    bits = pixels > avg
    value = 0
    for bit in bits.flatten():
        value = (value << 1) | int(bit)
    return value


def hamming_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def iter_image_files(directory: Path, extensions: set[str]) -> Iterable[Path]:
    if not directory.exists():
        return
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in extensions:
            yield path


def infer_category_from_name(name: str) -> str | None:
    lowered = name.lower()
    for category, aliases in CATEGORY_ALIASES.items():
        if any(alias in lowered for alias in aliases):
            return category
    return None


def build_record(path: Path, label: str, category: str, source_type: str) -> ImageRecord:
    return ImageRecord(
        source_path=path,
        label=label,
        category=category,
        source_type=source_type,
        sha256=compute_sha256(path),
        average_hash=compute_average_hash(path),
    )


def collect_structured_records(config: DataConfig) -> list[ImageRecord]:
    records: list[ImageRecord] = []
    for source_root in config.structured_sources:
        if not source_root.exists():
            continue
        for label_dir in sorted([path for path in source_root.iterdir() if path.is_dir() and path.name in config.labels]):
            for image_path in iter_image_files(label_dir, config.image_extensions):
                category = infer_category_from_name(image_path.name)
                if category is None:
                    continue
                records.append(build_record(image_path, label_dir.name, category, "structured"))
    return records


def collect_raw_records(config: DataConfig) -> list[ImageRecord]:
    records: list[ImageRecord] = []
    for label, source_root in config.raw_sources.items():
        if not source_root.exists():
            continue
        for category_dir in sorted([path for path in source_root.iterdir() if path.is_dir()]):
            if category_dir.name not in config.allowed_categories:
                continue
            for image_path in iter_image_files(category_dir, config.image_extensions):
                records.append(build_record(image_path, label, category_dir.name, "raw"))
    return records


def collect_background_aug_records(config: DataConfig) -> list[ImageRecord]:
    records: list[ImageRecord] = []
    if not config.background_aug_dir.exists():
        return records
    for label_dir in sorted([path for path in config.background_aug_dir.iterdir() if path.is_dir() and path.name in config.labels]):
        for category_dir in sorted([path for path in label_dir.iterdir() if path.is_dir()]):
            if category_dir.name not in config.allowed_categories:
                continue
            for image_path in iter_image_files(category_dir, config.image_extensions):
                records.append(build_record(image_path, label_dir.name, category_dir.name, "background_aug"))
    return records


def dedupe_records(records: list[ImageRecord]) -> list[ImageRecord]:
    best_by_hash: dict[str, ImageRecord] = {}
    priority = {"structured": 0, "raw": 1, "background_aug": 2}
    for record in records:
        current = best_by_hash.get(record.sha256)
        if current is None or priority[record.source_type] < priority[current.source_type]:
            best_by_hash[record.sha256] = record
    return list(best_by_hash.values())


def cluster_near_duplicates(records: list[ImageRecord], threshold: int) -> list[list[ImageRecord]]:
    clusters: list[list[ImageRecord]] = []
    sorted_records = sorted(records, key=lambda item: item.average_hash)
    for record in sorted_records:
        for cluster in clusters:
            representative = cluster[0]
            if hamming_distance(record.average_hash, representative.average_hash) <= threshold:
                cluster.append(record)
                break
        else:
            clusters.append([record])
    return clusters


def assign_splits(records: list[ImageRecord], config: DataConfig) -> list[tuple[str, ImageRecord]]:
    rng = random.Random(config.random_seed)
    assignments: list[tuple[str, ImageRecord]] = []
    by_bucket: dict[tuple[str, str], list[ImageRecord]] = defaultdict(list)
    for record in records:
        by_bucket[(record.label, record.category)].append(record)

    for bucket, bucket_records in sorted(by_bucket.items()):
        clusters = cluster_near_duplicates(bucket_records, config.near_duplicate_threshold)
        rng.shuffle(clusters)
        if len(clusters) == 1:
            split_names = ["train"]
        else:
            val_target = max(1, round(len(bucket_records) * config.val_fraction))
            val_count = 0
            split_names = []
            for cluster in clusters:
                if val_count < val_target:
                    split_names.append("val")
                    val_count += len(cluster)
                else:
                    split_names.append("train")
            if "train" not in split_names:
                split_names[-1] = "train"
            if "val" not in split_names:
                split_names[0] = "val"

        for split_name, cluster in zip(split_names, clusters):
            for record in cluster:
                if record.source_type == "background_aug":
                    assignments.append(("train", record))
                else:
                    assignments.append((split_name, record))
    return assignments


def safe_filename(record: ImageRecord, seen_names: set[str]) -> str:
    suffix = record.source_path.suffix.lower()
    base = f"{record.category}_{record.label}_{record.sha256[:12]}"
    candidate = f"{base}{suffix}"
    counter = 1
    while candidate in seen_names:
        candidate = f"{base}_{counter}{suffix}"
        counter += 1
    seen_names.add(candidate)
    return candidate


def write_dataset(assignments: list[tuple[str, ImageRecord]], config: DataConfig) -> list[SplitAssignment]:
    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="rebuilt_data_", dir=output_dir.parent))
    manifest: list[SplitAssignment] = []
    seen_names: set[str] = set()
    try:
        for split_name in ("train", "val"):
            for label in config.labels:
                (temp_dir / split_name / label).mkdir(parents=True, exist_ok=True)

        for split_name, record in assignments:
            file_name = safe_filename(record, seen_names)
            destination = temp_dir / split_name / record.label / file_name
            final_destination = output_dir / split_name / record.label / file_name
            shutil.copy2(record.source_path, destination)
            manifest.append(SplitAssignment(record=record, split=split_name, output_path=final_destination))

        for split_name in ("train", "val"):
            target_dir = output_dir / split_name
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.move(str(temp_dir / split_name), str(target_dir))
        return manifest
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def remove_loose_root_files(config: DataConfig) -> list[Path]:
    removed: list[Path] = []
    if not config.remove_loose_root_files:
        return removed
    for path in sorted(config.output_dir.iterdir()):
        if path.is_file():
            path.unlink()
            removed.append(path)
    return removed


def write_manifest(manifest: list[SplitAssignment], config: DataConfig) -> Path:
    reports_dir = config.output_dir.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = reports_dir / "dataset_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "split",
                "label",
                "category",
                "source_type",
                "source_path",
                "output_path",
                "sha256",
                "average_hash",
            ],
        )
        writer.writeheader()
        for item in manifest:
            writer.writerow(
                {
                    "split": item.split,
                    "label": item.record.label,
                    "category": item.record.category,
                    "source_type": item.record.source_type,
                    "source_path": item.record.source_path.as_posix(),
                    "output_path": item.output_path.relative_to(config.output_dir.parent).as_posix(),
                    "sha256": item.record.sha256,
                    "average_hash": item.record.average_hash,
                }
            )
    return manifest_path


def summarize_manifest(manifest: list[SplitAssignment]) -> dict[tuple[str, str, str], int]:
    counts: dict[tuple[str, str, str], int] = defaultdict(int)
    for item in manifest:
        counts[(item.split, item.record.label, item.record.category)] += 1
    return dict(sorted(counts.items()))


def prepare_dataset(config: DataConfig) -> dict[str, object]:
    set_global_seed(config.random_seed)
    removed_files = remove_loose_root_files(config)
    records = collect_structured_records(config) + collect_raw_records(config) + collect_background_aug_records(config)
    unique_records = dedupe_records(records)
    assignments = assign_splits(unique_records, config)
    manifest = write_dataset(assignments, config)
    manifest_path = write_manifest(manifest, config)
    return {
        "records_seen": len(records),
        "unique_records": len(unique_records),
        "removed_root_files": [path.as_posix() for path in removed_files],
        "manifest_path": manifest_path.as_posix(),
        "summary": {
            f"{split}/{label}/{category}": count
            for (split, label, category), count in summarize_manifest(manifest).items()
        },
    }


def load_datasets(data_dir: Path, image_size: tuple[int, int], batch_size: int, seed: int) -> tuple[tf.data.Dataset, tf.data.Dataset, list[str]]:
    train_dataset = tf.keras.utils.image_dataset_from_directory(
        data_dir / "train",
        image_size=image_size,
        batch_size=batch_size,
        label_mode="binary",
        shuffle=True,
        seed=seed,
    )
    val_dataset = tf.keras.utils.image_dataset_from_directory(
        data_dir / "val",
        image_size=image_size,
        batch_size=batch_size,
        label_mode="binary",
        shuffle=False,
    )
    class_names = train_dataset.class_names
    autotune = tf.data.AUTOTUNE
    train_dataset = train_dataset.prefetch(buffer_size=autotune)
    val_dataset = val_dataset.prefetch(buffer_size=autotune)
    return train_dataset, val_dataset, class_names


def count_images_by_label(data_dir: Path, labels: tuple[str, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for label in labels:
        label_dir = data_dir / "train" / label
        counts[label] = sum(1 for path in label_dir.iterdir() if path.is_file()) if label_dir.exists() else 0
    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize and rebuild the dataset structure.")
    parser.add_argument("--remove-loose-root-files", action="store_true")
    parser.add_argument("--val-fraction", type=float, default=DEFAULT_DATA_CONFIG.val_fraction)
    parser.add_argument("--seed", type=int, default=DEFAULT_DATA_CONFIG.random_seed)
    parser.add_argument("--near-duplicate-threshold", type=int, default=DEFAULT_DATA_CONFIG.near_duplicate_threshold)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = DataConfig(
        val_fraction=args.val_fraction,
        random_seed=args.seed,
        near_duplicate_threshold=args.near_duplicate_threshold,
        remove_loose_root_files=args.remove_loose_root_files,
    )
    summary = prepare_dataset(config)
    print(summary)


if __name__ == "__main__":
    main()
