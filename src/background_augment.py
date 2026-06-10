from __future__ import annotations

import argparse
import hashlib
import random
import shutil
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageFilter, ImageOps

from config import BACKGROUND_AUG_DIR, BACKGROUND_LIBRARY_DIR, DEFAULT_DATA_CONFIG, RAW_SOURCES


@dataclass(frozen=True)
class BackgroundAugmentConfig:
    raw_sources: dict[str, Path]
    output_dir: Path = BACKGROUND_AUG_DIR
    background_library_dir: Path = BACKGROUND_LIBRARY_DIR
    white_threshold: int = 235
    chroma_threshold: int = 25
    border_ratio_threshold: float = 0.7
    variants_per_image: int = 2
    random_seed: int = 42
    blur_radius: float = 1.5
    object_scale_min: float = 0.65
    object_scale_max: float = 0.82


def set_seed(seed: int) -> random.Random:
    np.random.seed(seed)
    return random.Random(seed)


def load_rgb(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).convert("RGB")


def white_border_ratio(image: Image.Image, white_threshold: int, chroma_threshold: int) -> float:
    array = np.asarray(image.resize((128, 128)), dtype=np.uint8)
    border = np.concatenate([array[0, :, :], array[-1, :, :], array[:, 0, :], array[:, -1, :]], axis=0)
    brightness = border.mean(axis=1)
    spread = border.max(axis=1) - border.min(axis=1)
    return float(((brightness >= white_threshold) & (spread <= chroma_threshold)).mean())


def is_white_background_candidate(path: Path, config: BackgroundAugmentConfig) -> bool:
    image = load_rgb(path)
    ratio = white_border_ratio(image, config.white_threshold, config.chroma_threshold)
    return ratio >= config.border_ratio_threshold


def build_foreground_mask(image: Image.Image, white_threshold: int, blur_radius: float) -> Image.Image:
    arr = np.asarray(image, dtype=np.uint8)
    brightness = arr.mean(axis=2)
    spread = arr.max(axis=2) - arr.min(axis=2)
    foreground = ~((brightness >= white_threshold) & (spread <= 30))
    mask = Image.fromarray((foreground.astype(np.uint8) * 255), mode="L")
    mask = mask.filter(ImageFilter.MedianFilter(size=5))
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return mask


def crop_to_foreground(image: Image.Image, mask: Image.Image) -> tuple[Image.Image, Image.Image]:
    bbox = mask.getbbox()
    if bbox is None:
        return image, mask
    return image.crop(bbox), mask.crop(bbox)


def procedural_background(size: tuple[int, int], rng: random.Random) -> Image.Image:
    width, height = size
    top = np.array([rng.randint(130, 210), rng.randint(120, 200), rng.randint(110, 190)], dtype=np.float32)
    bottom = np.array([rng.randint(90, 180), rng.randint(90, 170), rng.randint(80, 160)], dtype=np.float32)
    y = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None, None]
    gradient = top * (1.0 - y) + bottom * y
    gradient = np.repeat(gradient, width, axis=1)
    noise = np.random.normal(loc=0.0, scale=8.0, size=(height, width, 3))
    image = np.clip(gradient + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(image, mode="RGB").filter(ImageFilter.GaussianBlur(radius=1.2))


def load_background_library(path: Path) -> list[Image.Image]:
    if not path.exists():
        return []
    backgrounds: list[Image.Image] = []
    for item in sorted(path.rglob("*")):
        if item.is_file() and item.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            backgrounds.append(load_rgb(item))
    return backgrounds


def choose_background(size: tuple[int, int], library: list[Image.Image], rng: random.Random) -> Image.Image:
    if not library:
        return procedural_background(size, rng)
    background = rng.choice(library).copy().resize(size)
    return background.filter(ImageFilter.GaussianBlur(radius=0.8))


def composite_on_background(image: Image.Image, mask: Image.Image, background: Image.Image, rng: random.Random, config: BackgroundAugmentConfig) -> Image.Image:
    canvas = background.copy()
    image, mask = crop_to_foreground(image, mask)
    target_size = int(min(canvas.size) * rng.uniform(config.object_scale_min, config.object_scale_max))
    scale = target_size / max(image.size)
    resized_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    image = image.resize(resized_size, Image.LANCZOS)
    mask = mask.resize(resized_size, Image.LANCZOS)

    max_x = max(canvas.width - image.width, 1)
    max_y = max(canvas.height - image.height, 1)
    offset = (rng.randint(0, max_x), rng.randint(0, max_y))

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_mask = mask.filter(ImageFilter.GaussianBlur(radius=10))
    shadow_layer = Image.new("RGBA", image.size, (0, 0, 0, 60))
    shadow.paste(shadow_layer, (offset[0] + 6, offset[1] + 8), shadow_mask)

    rgba_canvas = canvas.convert("RGBA")
    rgba_canvas = Image.alpha_composite(rgba_canvas, shadow)
    foreground = image.convert("RGBA")
    rgba_canvas.paste(foreground, offset, mask)
    return rgba_canvas.convert("RGB")


def output_name(source_path: Path, variant_idx: int) -> str:
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest()[:10]
    return f"{source_path.stem}_bgaug_{variant_idx}_{digest}.jpg"


def clear_output_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def generate_variants(config: BackgroundAugmentConfig) -> dict[str, int]:
    rng = set_seed(config.random_seed)
    library = load_background_library(config.background_library_dir)
    clear_output_dir(config.output_dir)

    summary = {"candidates": 0, "generated": 0}
    for label, source_root in config.raw_sources.items():
        for category_dir in sorted([path for path in source_root.iterdir() if path.is_dir()]):
            output_category = config.output_dir / label / category_dir.name
            output_category.mkdir(parents=True, exist_ok=True)
            for image_path in sorted(category_dir.iterdir()):
                if not image_path.is_file() or image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                    continue
                if not is_white_background_candidate(image_path, config):
                    continue
                summary["candidates"] += 1
                image = load_rgb(image_path)
                mask = build_foreground_mask(image, config.white_threshold, config.blur_radius)
                for variant_idx in range(config.variants_per_image):
                    background = choose_background(image.size, library, rng)
                    composite = composite_on_background(image, mask, background, rng, config)
                    composite.save(output_category / output_name(image_path, variant_idx), quality=92)
                    summary["generated"] += 1
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate selective white-background food augmentations.")
    parser.add_argument("--variants-per-image", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--white-threshold", type=int, default=235)
    parser.add_argument("--border-ratio-threshold", type=float, default=0.7)
    parser.add_argument("--background-library-dir", type=Path, default=BACKGROUND_LIBRARY_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = BackgroundAugmentConfig(
        raw_sources=RAW_SOURCES.copy(),
        variants_per_image=args.variants_per_image,
        random_seed=args.seed,
        white_threshold=args.white_threshold,
        border_ratio_threshold=args.border_ratio_threshold,
        background_library_dir=args.background_library_dir,
    )
    summary = generate_variants(config)
    print(summary)


if __name__ == "__main__":
    main()
