import argparse
import subprocess
import sys
from pathlib import Path
from PIL import Image
from src.predict import predict_image as predict

# Training function for CLI
def run_training(data_dir: Path, epochs: int, batch_size: int, model_path: Path) -> int:
    command = [
        sys.executable,
        "src/train.py",
        "--data-dir",
        str(data_dir),
        "--epochs",
        str(epochs),
        "--batch-size",
        str(batch_size),
        "--model-path",
        str(model_path),
    ]
    result = subprocess.run(command)
    return result.returncode

# Prediction function for CLI
def run_prediction(image_path: Path) -> None:
    image = Image.open(image_path).convert("RGB")
    label, confidence, score = predict(image)
    print(f"Prediction: {label}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Raw score: {score:.4f}")
    

def main() -> None:
    parser = argparse.ArgumentParser(description="CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Predict subcommand
    predict_parser = subparsers.add_parser("predict", help="Run inference on a single image.")
    predict_parser.add_argument("image", type=Path, help="Path to the image to classify.")
    
    #TODO: Train subcommand
    train_parser = subparsers.add_parser("train", help="Train the freshness classifier.")
    train_parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Path to the data root containing train/ and val/ folders.",
    )
    train_parser.add_argument(
        "--epochs",
        type=int,
        default=8,
        help="Number of training epochs.",
    )
    train_parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Batch size for training.",
    )
    train_parser.add_argument(
        "--model-path",
        type=Path,
        default=Path("models/classifier.pth"),
        help="Output path for the trained checkpoint.",
    )

    args = parser.parse_args()

    # Execute the subcommands
    if args.command == "predict":
        run_prediction(args.image)
    elif args.command == "train":
        #TODO: Training logic is handled in src/train.py and not implemented yet because it need more specifics about the training process and model architecture.
        print("Training functionality is not implemented in this CLI yet. Please run src/train.py directly.")  

# Entry point
if __name__ == "__main__":
    main()
