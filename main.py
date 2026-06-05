import argparse
import subprocess
import sys
from pathlib import Path
from PIL import Image
from src.predict import predict_image as predict

# Evaluation function for CLI
def run_evaluation(model: Path, validation: Path, batch_size: int, ) -> None:
    command = [
        sys.executable,
        "src/evaluate.py",
        "--model",
        str(model),
        "--validation",
        str(validation),
        "--batch-size",
        str(batch_size),
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
    
    predict_parser = subparsers.add_parser("predict", help="Run inference on a single image.")
    predict_parser.add_argument("image", type=Path, help="Path to the image to classify.")
    
    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate the classifiers.")
    evaluate_parser.add_argument(
        "--model",
        type=Path,
        required=True,
        help="Path to the models root folder and choose a model.",
    )
    evaluate_parser.add_argument(
        "--validation",
        type=Path,
        default=Path("data/val"),
        help="Path to the validation data.",
    )
    evaluate_parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size for evaluation.",
    )

    args = parser.parse_args()

    # Execute the subcommands
    if args.command == "predict":
        run_prediction(args.image)
    elif args.command == "evaluate":
        run_evaluation(args.model, args.validation, args.batch_size)
    elif args.command == "train":
        #TODO: Training logic is handled in src/train.py and not implemented yet because it need more specifics about the training process and model architecture.
        print("Training functionality is not implemented in this CLI yet. Please run src/train.py directly.")  

# Entry point
if __name__ == "__main__":
    main()
