import os
import traceback
import keras
import numpy as np
from keras.applications.efficientnet import decode_predictions
from PIL import Image
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches

try:
    import torch
    from mobile_sam import sam_model_registry, SamAutomaticMaskGenerator
except ImportError:
    torch = None
    sam_model_registry = None
    SamAutomaticMaskGenerator = None


DEFAULT_CHECKPOINT = "models/mobile_sam.pt"
DEFAULT_MAX_IMAGE_SIDE = 640
DEFAULT_POINTS_PER_SIDE = 16
DEFAULT_MAX_CANDIDATES = 20
DEFAULT_MAX_DETECTIONS = 10


class Detector:
    """
    Segmentiert Lebensmittelbilder mit MobileSAM.

    Masken werden zu Bounding Boxes reduziert, per Food-Vorklassifizierung
    gefiltert und mit Non-Max-Suppression zusammengeführt.
    """
    
    def __init__(
        self,
        checkpoint: str = DEFAULT_CHECKPOINT,
        debug: bool = False,
        max_image_side: int = DEFAULT_MAX_IMAGE_SIDE,
        points_per_side: int = DEFAULT_POINTS_PER_SIDE,
        max_candidates: int = DEFAULT_MAX_CANDIDATES,
        max_detections: int = DEFAULT_MAX_DETECTIONS,
    ):
        self.checkpoint = checkpoint
        self.debug = debug
        self.max_image_side = max_image_side
        self.points_per_side = points_per_side
        self.max_candidates = max_candidates
        self.max_detections = max_detections
        self.device = "cuda" if torch is not None and torch.cuda.is_available() else "cpu"
        self.run_dir = None
        self.score_threshold = 0.725
        self.food_classifier = None
        self.mask_generator = None

        if self.debug:
            self.run_dir = os.path.join(
                "logs/detector/",
                datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            os.makedirs(self.run_dir, exist_ok=True)

        model = self.load_segmentation()
        if model is None or SamAutomaticMaskGenerator is None:
            return

        self.mask_generator = SamAutomaticMaskGenerator(
            model,
            points_per_side=self.points_per_side,
            pred_iou_thresh=0.86,
            stability_score_thresh=0.92,
            min_mask_region_area=500,
        )
        self.food_classifier = self.load_food_classifier()

    # -----------------------------
    # IMAGE UTIL
    # -----------------------------
    def to_numpy_rgb(self, image: Image.Image) -> np.ndarray:
        return np.array(image.convert("RGB"), dtype=np.uint8)

    def resize_for_segmentation(self, image: Image.Image) -> tuple[Image.Image, float, float]:
        w, h = image.size
        largest_side = max(w, h)
        if largest_side <= self.max_image_side:
            return image.convert("RGB"), 1.0, 1.0

        scale = self.max_image_side / largest_side
        resized_w = max(1, int(round(w * scale)))
        resized_h = max(1, int(round(h * scale)))
        resized = image.convert("RGB").resize(
            (resized_w, resized_h),
            Image.Resampling.LANCZOS,
        )
        return resized, w / resized_w, h / resized_h

    def mask_color(self, index: int) -> tuple[int, int, int]:
        colors = [
            (0, 169, 98),
            (201, 54, 43),
            (214, 146, 58),
            (68, 110, 214),
            (133, 86, 191),
            (36, 139, 154),
        ]
        return colors[index % len(colors)]

    def build_segmentation_overlay(
        self,
        image: Image.Image,
        masks: list[dict],
        alpha: float = 0.38,
    ) -> Image.Image:
        base_image = image.convert("RGB")
        canvas = np.array(base_image, dtype=np.float32)

        for index, mask in enumerate(masks):
            segmentation = mask.get("segmentation")
            if segmentation is None:
                continue

            mask_image = Image.fromarray(
                segmentation.astype(np.uint8) * 255,
                mode="L",
            )
            if mask_image.size != base_image.size:
                mask_image = mask_image.resize(base_image.size, Image.Resampling.NEAREST)

            mask_pixels = np.asarray(mask_image) > 0
            color = np.array(self.mask_color(index), dtype=np.float32)
            canvas[mask_pixels] = canvas[mask_pixels] * (1 - alpha) + color * alpha

        return Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))

    def show_segments(self, image: Image.Image, masks: list[dict]):
        """
        Visualisiert alle von SAM gefundenen Segmente.
        """

        image_np = np.array(image)

        plt.figure(figsize=(12, 12))
        plt.imshow(image_np)

        for mask in masks:

            segmentation = mask["segmentation"]

            color = np.concatenate([
                np.random.random(3),
                [0.4]  # Transparenz
            ])

            overlay = np.zeros(
                (*segmentation.shape, 4),
                dtype=np.float32,
            )

            overlay[segmentation] = color

            plt.imshow(overlay)

        plt.axis("off")
        plt.tight_layout()
        # plt.show()
        self.save_figure("sam_segments")

    def show_segments_with_boxes(self, image: Image.Image, masks: list[dict]):
        fig, ax = plt.subplots(figsize=(12, 12))

        ax.imshow(np.array(image))

        for mask in masks:

            seg = mask["segmentation"]

            color = np.concatenate([
                np.random.random(3),
                [0.35]
            ])

            overlay = np.zeros(
                (*seg.shape, 4),
                dtype=np.float32,
            )

            overlay[seg] = color

            ax.imshow(overlay)

            x, y, w, h = mask["bbox"]

            rect = patches.Rectangle(
                (x, y),
                w,
                h,
                linew=1.5,
                edgecolor="red",
                facecolor="none",
            )

            ax.add_patch(rect)

        ax.axis("off")
        # plt.show()
        self.save_figure("sam_segments_with_boxes")

    def show_detections(self, image, detections):
        fig, ax = plt.subplots(figsize=(12, 12))

        ax.imshow(np.array(image))

        for det in detections:

            x1, y1, x2, y2 = det["box"]

            rect = plt.Rectangle(
                (x1, y1),
                x2 - x1,
                y2 - y1,
                fill=False,
                linew=2,
            )

            ax.add_patch(rect)

            ax.text(
                x1,
                y1,
                f"{det['score']:.2f}",
            )

        ax.axis("off")
        # plt.show()
        self.save_figure("sam_detections")

    def save_figure(self, name: str):
        if not self.debug or self.run_dir is None:
            plt.close()
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filepath = os.path.join(
            self.run_dir,
            f"{timestamp}_{name}.png"
        )

        plt.savefig(
            filepath,
            bbox_inches="tight",
            dpi=200,
        )

        plt.close()

        print(f"[DEBUG] saved: {filepath}")

    # -----------------------------
    # SAM MODEL
    # -----------------------------
    def load_segmentation(self):
        if sam_model_registry is None:
            print("[WARN] mobile_sam is not installed; object detection is disabled.")
            return None

        if not os.path.exists(self.checkpoint):
            print(f"[WARN] MobileSAM checkpoint not found at '{self.checkpoint}'; object detection is disabled.")
            return None

        try:
            sam = sam_model_registry["vit_t"](
                checkpoint=self.checkpoint
            )
            sam.to(device=self.device)
            sam.eval()
            return sam
        except Exception as e:
            print(f"[WARN] Could not load MobileSAM checkpoint: {e}")
            return None

    def load_food_classifier(self):
        try:
            return keras.applications.EfficientNetB0(
                include_top=True,
                weights="imagenet",
            )
        except Exception as e:
            print(f"[WARN] Could not load food preclassifier: {e}")
            return None

    # -----------------------------
    # MASK PROCESSING
    # -----------------------------
    def segment_everything(self, image: Image.Image):
        image_np = self.to_numpy_rgb(image)
        return self.mask_generator.generate(image_np)

    def mask_to_box(self, mask: np.ndarray):
        ys, xs = np.where(mask)

        if len(xs) == 0 or len(ys) == 0:
            return None

        return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]

    def bbox_to_box(self, mask_dict):
        bbox = mask_dict.get("bbox")
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            return None

        x, y, w, h = bbox
        return [
            int(round(x)),
            int(round(y)),
            int(round(x + w)),
            int(round(y + h)),
        ]

    def is_valid_mask(self, mask_dict, min_area=2500):
        if mask_dict["area"] < min_area:
            return False

        if mask_dict.get("predicted_iou", 0) < 0.7:
            return False

        if mask_dict.get("stability_score", 0) < 0.85:
            return False
        return True

    # -----------------------------
    # BOX UTIL
    # -----------------------------
    def clamp_box(self, box, w, h):
        if box is None:
            return None

        x1, y1, x2, y2 = box

        x1 = int(max(0, min(x1, w - 1)))
        y1 = int(max(0, min(y1, h - 1)))
        x2 = int(max(0, min(x2, w - 1)))
        y2 = int(max(0, min(y2, h - 1)))

        if x2 <= x1 or y2 <= y1:
            return None

        return [x1, y1, x2, y2]

    def safe_crop(self, image: Image.Image, box):
        if box is None:
            return None
        return image.crop(tuple(box))

    def scale_box(self, box, scale_x: float, scale_y: float, w: int, h: int):
        x1, y1, x2, y2 = box
        scaled = [
            int(round(x1 * scale_x)),
            int(round(y1 * scale_y)),
            int(round(x2 * scale_x)),
            int(round(y2 * scale_y)),
        ]
        return self.clamp_box(scaled, w, h)

    # -----------------------------
    # SCORE FUSION
    # -----------------------------
    def compute_final_score(self, food_score, mask):
        return (
            0.7 * food_score +
            0.2 * mask.get("predicted_iou", 0.0) +
            0.1 * mask.get("stability_score", 0.0)
        )

    def mask_quality(self, mask):
        return (
            0.7 * mask.get("predicted_iou", 0.0) +
            0.3 * mask.get("stability_score", 0.0)
        )

    def food_score(self, crop: Image.Image):
        """Berechnet einen Food-Score fuer genau einen Crop."""
        scores = self.food_scores([crop])
        return scores[0] if scores else ("background", 0.0)

    def food_scores(self, crops: list[Image.Image]) -> list[tuple[str, float]]:
        """Berechnet Food-Scores fuer mehrere Crops in einem Batch."""
        if self.food_classifier is None:
            return [("background", 0.0) for _ in crops]
        if not crops:
            return []

        batch = np.stack([
            np.array(crop.resize((224, 224)).convert("RGB"), dtype=np.float32)
            for crop in crops
        ])
        batch = keras.applications.efficientnet.preprocess_input(batch)

        preds = np.asarray(self.food_classifier(batch, training=False))
        decoded = decode_predictions(preds, top=3)

        scores = []
        for classes in decoded:
            food_class = "background"
            score = 0.0
            for _, label, confidence in classes:
                if float(confidence) > score:
                    food_class = label
                    score = float(confidence)

            if score <= 0.5:
                scores.append(("background", 0.0))
            else:
                scores.append((food_class, score))

        return scores

    # -----------------------------
    # IOU + NMS
    # -----------------------------
    def iou(self, a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b

        inter_x1 = max(ax1, bx1)
        inter_y1 = max(ay1, by1)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)

        inter = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

        area_a = (ax2 - ax1) * (ay2 - ay1)
        area_b = (bx2 - bx1) * (by2 - by1)

        union = area_a + area_b - inter

        return inter / union if union > 0 else 0

    def _non_max_suppression(self, detections, iou_threshold=0.25):

        detections = sorted(detections, key=lambda x: x["score"], reverse=True)

        keep = []

        while detections:
            best = detections.pop(0)
            keep.append(best)

            detections = [
                d for d in detections
                if self.iou(best["box"], d["box"]) < iou_threshold
            ]

        return keep

    # -----------------------------
    # MAIN PIPELINE
    # -----------------------------
    def analyze_segments(self, image: Image.Image) -> dict:
        result = {
            "detections": [],
            "overlay": image.convert("RGB"),
            "mask_count": 0,
            "valid_mask_count": 0,
        }

        try:
            if self.mask_generator is None:
                return result

            original_w, original_h = image.size
            a_img, scale_x, scale_y = self.resize_for_segmentation(image)
            analysis_w, analysis_h = a_img.size

            print("Starting SAM segmentation...")
            masks = self.segment_everything(a_img)
            print(f"Generated {len(masks)} masks")
            result["mask_count"] = len(masks)
            result["overlay"] = self.build_segmentation_overlay(image, masks)
            if self.debug:
                self.show_segments(image=a_img, masks=masks)
                self.show_segments_with_boxes(image=a_img, masks=masks) 

            candidates = []
            
            for mask in masks:
                if not self.is_valid_mask(mask):
                    continue
                result["valid_mask_count"] += 1

                box = self.bbox_to_box(mask)
                box = self.clamp_box(box, analysis_w, analysis_h)
                if box is None:
                    continue

                crop = self.safe_crop(a_img, box)
                if crop is None:
                    continue

                candidates.append({
                    "box": box,
                    "crop": crop,
                    "mask": mask,
                    "quality": self.mask_quality(mask),
                })

            candidates = sorted(
                candidates,
                key=lambda item: item["quality"],
                reverse=True,
            )[:self.max_candidates]

            proposals = []
            food_results = self.food_scores([candidate["crop"] for candidate in candidates])

            for candidate, (food_label, score) in zip(candidates, food_results):
                if score <= 0.0:
                    continue

                mask = candidate["mask"]
                final_score = self.compute_final_score(score, mask)
                if final_score < self.score_threshold:
                    continue

                og_box = self.scale_box(
                    candidate["box"],
                    scale_x,
                    scale_y,
                    original_w,
                    original_h,
                )
                if og_box is None:
                    continue

                proposals.append({
                    "box": og_box,
                    "score": final_score,
                    "label": food_label,
                })
            
            proposals = self._non_max_suppression(proposals, iou_threshold=0.25)
            proposals = proposals[:self.max_detections]
            if self.debug:
                self.show_detections(image, proposals)
            result["detections"] = proposals
            return result

        except Exception as e:
            print("\n" + "=" * 10)
            print("ANALYZE_SEGMENTS FAILED")
            print("=" * 10)
            print(f"Exception Type: {type(e).__name__}")
            print(f"Exception: {e}")
            print("\nTraceback:")
            traceback.print_exc()
            print("=" * 10)

            return result

    def detect_objects(self, image: Image.Image):
        return self.analyze_segments(image)["detections"]


# Singleton
_detector = None
def get_detector() -> Detector:
    global _detector

    if _detector is None:
        debug = os.environ.get("FRESHIFY_DETECTOR_DEBUG", "").lower() in {"1", "true", "yes"}
        _detector = Detector(
            debug=debug,
            max_image_side=DEFAULT_MAX_IMAGE_SIDE,
            points_per_side=DEFAULT_POINTS_PER_SIDE,
            max_candidates=DEFAULT_MAX_CANDIDATES,
            max_detections=DEFAULT_MAX_DETECTIONS,
        )
        
    return _detector

def detect_objects(image: Image.Image) -> list[dict]:
    return get_detector().detect_objects(image)


def analyze_segments(image: Image.Image) -> dict:
    return get_detector().analyze_segments(image)


def main():
    image = Image.open("data/gemuese-box.png")
    detections = detect_objects(image)
    print(f"detect_objects: {len(detections)} objects found.")


if __name__ == "__main__":
    main()
