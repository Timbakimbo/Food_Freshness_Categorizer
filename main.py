import argparse
from pathlib import Path

from src.predict import DEFAULT_MODEL_PATH, DEFAULT_THRESHOLD, load_model, predict_image


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify one food image as edible or non_edible.",
    )
    parser.add_argument("image", type=Path, help="Path to the image file.")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_PATH,
        help="Path to the Keras freshness model.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="Decision threshold for non_edible.",
    )
    args = parser.parse_args()

    model = load_model(args.model)
    label, confidence, probability_non_edible = predict_image(
        args.image,
        model=model,
        threshold=args.threshold,
    )

    print(f"label: {label}")
    print(f"confidence: {confidence:.4f}")
    print(f"probability_non_edible: {probability_non_edible:.4f}")
    print(f"threshold: {args.threshold:.2f}")


if __name__ == "__main__":
    main()
