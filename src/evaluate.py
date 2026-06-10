from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

from config import DEFAULT_TRAIN_CONFIG, IMAGE_EXTENSIONS, LABELS, TrainConfig
from data import load_datasets, set_global_seed


def evaluate_model(model: tf.keras.Model, dataset: tf.data.Dataset, threshold: float = 0.5) -> dict[str, float | dict[str, int]]:
    probabilities = model.predict(dataset, verbose=0).reshape(-1)
    labels = np.concatenate([batch_labels.numpy().reshape(-1) for _, batch_labels in dataset], axis=0)
    return compute_binary_report(labels, probabilities, threshold)


def save_evaluation(report: dict[str, float | dict[str, int]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output_path


def iter_image_paths(image_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in image_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def load_image_batch(image_paths: list[Path], image_size: tuple[int, int]) -> np.ndarray:
    arrays = []
    for image_path in image_paths:
        loaded = image.load_img(image_path, target_size=image_size)
        arrays.append(image.img_to_array(loaded))
    return np.asarray(arrays, dtype=np.float32)


def label_to_int(label: str) -> int:
    if label not in LABELS:
        raise ValueError(f"Unsupported label: {label}. Expected one of: {', '.join(LABELS)}")
    return 1 if label == "non_edible" else 0


def int_to_label(value: int) -> str:
    return "non_edible" if value == 1 else "edible"


def compute_binary_report(labels: np.ndarray, probabilities: np.ndarray, threshold: float) -> dict[str, float | dict[str, int]]:
    predictions = (probabilities >= threshold).astype(int)

    tp = int(np.sum((predictions == 1) & (labels == 1)))
    tn = int(np.sum((predictions == 0) & (labels == 0)))
    fp = int(np.sum((predictions == 1) & (labels == 0)))
    fn = int(np.sum((predictions == 0) & (labels == 1)))

    accuracy = (tp + tn) / max(len(labels), 1)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    edible_precision = tn / max(tn + fn, 1)
    edible_recall = tn / max(tn + fp, 1)

    return {
        "accuracy": accuracy,
        "precision_non_edible": precision,
        "recall_non_edible": recall,
        "precision_edible": edible_precision,
        "recall_edible": edible_recall,
        "false_negatives_non_edible": fn,
        "false_positives_non_edible": fp,
        "confusion_matrix": {
            "true_negative_edible": tn,
            "false_positive_non_edible": fp,
            "false_negative_non_edible": fn,
            "true_positive_non_edible": tp,
        },
    }


def evaluate_image_directory(
    model: tf.keras.Model,
    image_dir: Path,
    true_label: str,
    image_size: tuple[int, int],
    threshold: float = 0.5,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    image_paths = iter_image_paths(image_dir)
    if not image_paths:
        raise ValueError(f"No supported image files found in {image_dir}")

    images = load_image_batch(image_paths, image_size)
    probabilities = model.predict(images, verbose=0).reshape(-1)
    labels = np.full(shape=len(image_paths), fill_value=label_to_int(true_label), dtype=int)
    report = compute_binary_report(labels, probabilities, threshold)

    rows: list[dict[str, object]] = []
    for image_path, probability in zip(image_paths, probabilities):
        predicted_int = int(probability >= threshold)
        predicted_label = int_to_label(predicted_int)
        confidence = float(probability if predicted_int == 1 else 1.0 - probability)
        rows.append(
            {
                "image_path": image_path.as_posix(),
                "true_label": true_label,
                "predicted_label": predicted_label,
                "is_correct": predicted_label == true_label,
                "probability_non_edible": float(probability),
                "confidence": confidence,
            }
        )

    correct = sum(1 for row in rows if row["is_correct"])
    directory_report: dict[str, object] = {
        **report,
        "image_dir": image_dir.as_posix(),
        "true_label": true_label,
        "threshold": threshold,
        "num_images": len(image_paths),
        "num_correct": correct,
        "num_incorrect": len(image_paths) - correct,
    }
    if true_label == "non_edible":
        directory_report["non_edible_detection_rate"] = correct / len(image_paths)
    else:
        directory_report["edible_detection_rate"] = correct / len(image_paths)
    return directory_report, rows


def save_predictions(rows: list[dict[str, object]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "image_path",
                "true_label",
                "predicted_label",
                "is_correct",
                "probability_non_edible",
                "confidence",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a trained food freshness model.")
    parser.add_argument("--model-path", type=Path, default=DEFAULT_TRAIN_CONFIG.model_path)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_TRAIN_CONFIG.data_dir)
    parser.add_argument("--image-dir", type=Path)
    parser.add_argument("--true-label", choices=LABELS)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_TRAIN_CONFIG.report_dir)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_TRAIN_CONFIG.batch_size)
    parser.add_argument("--seed", type=int, default=DEFAULT_TRAIN_CONFIG.random_seed)
    parser.add_argument("--threshold", type=float, default=0.5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = TrainConfig(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        random_seed=args.seed,
        model_path=args.model_path,
    )
    set_global_seed(config.random_seed)
    model = tf.keras.models.load_model(config.model_path)
    if args.image_dir is not None:
        if args.true_label is None:
            raise ValueError("--true-label is required when --image-dir is used")
        report, rows = evaluate_image_directory(
            model=model,
            image_dir=args.image_dir,
            true_label=args.true_label,
            image_size=config.image_size,
            threshold=args.threshold,
        )
        report_path = save_evaluation(report, args.report_dir / "evaluation.json")
        predictions_path = save_predictions(rows, args.report_dir / "predictions.csv")
        print(
            json.dumps(
                {
                    "report_path": report_path.as_posix(),
                    "predictions_path": predictions_path.as_posix(),
                    **report,
                },
                indent=2,
            )
        )
    else:
        _, val_dataset, _ = load_datasets(config.data_dir, config.image_size, config.batch_size, config.random_seed)
        report = evaluate_model(model, val_dataset, threshold=args.threshold)
        report_path = save_evaluation(report, args.report_dir / "evaluation.json")
        print(json.dumps({"report_path": report_path.as_posix(), **report}, indent=2))


if __name__ == "__main__":
    main()
