from __future__ import annotations

import argparse
import json
from pathlib import Path

import tensorflow as tf

from config import DEFAULT_TRAIN_CONFIG, LABELS, TrainConfig
from data import count_images_by_label, load_datasets, set_global_seed
from evaluate import evaluate_model, save_evaluation
from model import attach_augmentation, build_model


def save_history(history: tf.keras.callbacks.History, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(history.history, indent=2), encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the food freshness classifier.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_TRAIN_CONFIG.data_dir)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_TRAIN_CONFIG.model_path)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_TRAIN_CONFIG.batch_size)
    parser.add_argument("--epochs", type=int, default=DEFAULT_TRAIN_CONFIG.epochs)
    parser.add_argument("--seed", type=int, default=DEFAULT_TRAIN_CONFIG.random_seed)
    parser.add_argument(
        "--augmentation",
        choices=("none", "standard", "background"),
        default=DEFAULT_TRAIN_CONFIG.augmentation_mode,
    )
    parser.add_argument("--experiment-name", default=DEFAULT_TRAIN_CONFIG.experiment_name)
    parser.add_argument("--early-stopping-patience", type=int, default=DEFAULT_TRAIN_CONFIG.early_stopping_patience)
    parser.add_argument("--reduce-lr-patience", type=int, default=DEFAULT_TRAIN_CONFIG.reduce_lr_patience)
    parser.add_argument("--min-learning-rate", type=float, default=DEFAULT_TRAIN_CONFIG.min_learning_rate)
    parser.add_argument("--disable-class-weights", action="store_true")
    return parser.parse_args()


def compute_class_weights(config: TrainConfig) -> dict[int, float] | None:
    if not config.use_class_weights:
        return None
    counts = count_images_by_label(config.data_dir, LABELS)
    total = sum(counts.values())
    if total == 0 or min(counts.values()) == 0:
        return None
    return {
        0: total / (2.0 * counts["edible"]),
        1: total / (2.0 * counts["non_edible"]),
    }


def build_callbacks(config: TrainConfig) -> list[tf.keras.callbacks.Callback]:
    return [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_recall",
            mode="max",
            patience=config.early_stopping_patience,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_recall",
            mode="max",
            factor=0.5,
            patience=config.reduce_lr_patience,
            min_lr=config.min_learning_rate,
            verbose=1,
        ),
    ]


def main() -> None:
    args = parse_args()
    config = TrainConfig(
        data_dir=args.data_dir,
        model_path=args.model_path,
        batch_size=args.batch_size,
        epochs=args.epochs,
        random_seed=args.seed,
        experiment_name=args.experiment_name,
        augmentation_mode=args.augmentation,
        early_stopping_patience=args.early_stopping_patience,
        reduce_lr_patience=args.reduce_lr_patience,
        min_learning_rate=args.min_learning_rate,
        use_class_weights=not args.disable_class_weights,
    )

    set_global_seed(config.random_seed)
    train_dataset, val_dataset, class_names = load_datasets(
        config.data_dir,
        config.image_size,
        config.batch_size,
        config.random_seed,
    )
    train_dataset = attach_augmentation(train_dataset, config.augmentation_mode)
    model = build_model(config)
    model.summary()
    class_weights = compute_class_weights(config)
    callbacks = build_callbacks(config)

    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=config.epochs,
        callbacks=callbacks,
        class_weight=class_weights,
    )

    config.model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(config.model_path)

    report_dir = config.report_dir / config.experiment_name
    history_path = save_history(history, report_dir / "history.json")
    evaluation = evaluate_model(model, val_dataset)
    evaluation_path = save_evaluation(evaluation, report_dir / "evaluation.json")

    print(
        json.dumps(
            {
                "class_names": class_names,
                "model_path": config.model_path.as_posix(),
                "history_path": history_path.as_posix(),
                "evaluation_path": evaluation_path.as_posix(),
                "augmentation_mode": config.augmentation_mode,
                "class_weights": class_weights,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
