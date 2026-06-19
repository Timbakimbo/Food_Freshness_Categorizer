import os
import traceback
import keras
from keras.applications.efficientnet import decode_predictions
import numpy as np
from PIL import Image
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mobile_sam import sam_model_registry, SamAutomaticMaskGenerator


class Detector:
    """
    Der Detector implementiert eine Segmentierung für Lebensmittelbilder.
    
    Es wird das gesamte Bild segmentiert und die erzeugten Objekte (Masken und Bounding Boxes) 
    werden anschließend als Ergebnisse durch Non-Max-Suppression (NMS) gefiltert und zur Klassifizierung übergeben.
    """
    
    def __init__(self):
        self.run_dir = os.path.join(
            "logs/detector/",
            datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        os.makedirs(self.run_dir, exist_ok=True)
        model = self.load_segmentation()
        self.score_threshold = 0.725
        self.food_classifier = keras.applications.EfficientNetB0(
            include_top=True,
            weights="imagenet"
        )
        self.mask_generator = SamAutomaticMaskGenerator(
            model,
            points_per_side=32,
            pred_iou_thresh=0.86,
            stability_score_thresh=0.92,
            min_mask_region_area=500,
        )

    # -----------------------------
    # IMAGE UTIL
    # -----------------------------
    def to_numpy_rgb(self, image: Image.Image) -> np.ndarray:
        return np.array(image.convert("RGB"), dtype=np.uint8)

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
                linewidth=1.5,
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
                linewidth=2,
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
        sam = sam_model_registry["vit_t"](
            checkpoint="models/mobile_sam.pt"
        )
        sam.eval()
        return sam

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
    def clamp_box(self, box, width, height):
        if box is None:
            return None

        x1, y1, x2, y2 = box

        x1 = int(max(0, min(x1, width - 1)))
        y1 = int(max(0, min(y1, height - 1)))
        x2 = int(max(0, min(x2, width - 1)))
        y2 = int(max(0, min(y2, height - 1)))

        if x2 <= x1 or y2 <= y1:
            return None

        return [x1, y1, x2, y2]

    def safe_crop(self, image: Image.Image, box):
        if box is None:
            return None
        return image.crop(tuple(box))

    # -----------------------------
    # SCORE FUSION
    # -----------------------------
    def compute_final_score(self, score, mask):
        return (
            0.7 * score +
            0.2 * mask.get("predicted_iou", 0.0) +
            0.1 * mask.get("stability_score", 0.0)
        )

    def _food_score(self, crop):
        """Berechnet Food-Score für genau einen CROP. """
        arr = np.array(crop.resize((224, 224)).convert("RGB"), dtype=np.float32)
        
        arr = keras.applications.efficientnet.preprocess_input(arr)
        arr = np.expand_dims(arr, axis=0)

        preds = self.food_classifier(arr)        
        classes = decode_predictions(preds, top=3)[0]
        
        food_class = "background"
        food_score = 0.0        
        for _, lable, score in classes:
            if float(score) > 0.5:
                food_class = lable
                food_score = float(score)
        
        return food_class, food_score

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
    def detect_objects(self, image: Image.Image):
        try:
            H, W = image.size[1], image.size[0]

            print("Starting SAM segmentation...")
            masks = self.segment_everything(image)
            print(f"Generated {len(masks)} masks")
            # DEBUG
            self.show_segments(image=image, masks=masks)
            self.show_segments_with_boxes(image=image, masks=masks) 

            proposals = []
            
            for mask in masks:
                if not self.is_valid_mask(mask):
                    continue

                box = self.mask_to_box(mask["segmentation"])
                box = self.clamp_box(box, W, H)
                if box is None:
                    continue

                crop = self.safe_crop(image, box)
                if crop is None:
                    continue

                lable, score = self._food_score(crop)
                final_score = self.compute_final_score(
                    score,
                    mask,
                )
                if final_score < self.score_threshold:
                    continue

                proposals.append({
                    "box": box,
                    "score": final_score,
                    "label": lable,
                })
            
            proposals = self._non_max_suppression(proposals, iou_threshold=0.25)
            #DEBUG:
            self.show_detections(image, proposals)
            return proposals 

        except Exception as e:
            print("\n" + "=" * 10)
            print("DETECT_OBJECTS FAILED")
            print("=" * 10)
            print(f"Exception Type: {type(e).__name__}")
            print(f"Exception: {e}")
            print("\nTraceback:")
            traceback.print_exc()
            print("=" * 10)

            return []


# Singleton
_detector = None
def get_detector() -> Detector:
    global _detector

    if _detector is None:
        _detector = Detector()
        
    return _detector

def detect_objects(image: Image.Image) -> list[dict]:
    return get_detector().detect_objects(image)


def main():
    image = Image.open("data/gemuese-box.png")
    detections = detect_objects(image)
    print(f"detect_objects: {len(detections)} objects found.")


if __name__ == "__main__":
    main()