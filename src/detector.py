import os
from keras import ops
from matplotlib import pyplot as plt
import numpy as np
import keras
import keras_hub
import PIL.Image as Image
import tensorflow as tf

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
IMG_SIZE = (224, 224)
STRIDE = 128 # zu klein: 16, 32, 64
SCORE_THRESHOLD = 0.22 # zu hoch: 0.5, 0.3, 0.25
IMAGE_SIZE = (1024,1024)


def load_model() -> keras.Model:
    """Feature-Extraktor."""
    # backbone = keras.applications.MobileNetV3Small(
    #     input_shape=(*IMG_SIZE, 3),
    #     include_top=False,
    #     pooling="avg",
    #     weights="imagenet",
    # ) 
    # = 0 Objekte
    backbone = keras.applications.EfficientNetB0(
        name="efficientnetb0",
        weights="imagenet",
        pooling="avg",
        include_top=True,
        # input_shape=(*IMG_SIZE, 3),
    )
    # = 12 Objekte (MobielNetV2)
    backbone.trainable = False
    return backbone
    # return tf.keras.models.load_model("models/freshify_baseline_with_new_raw.keras") # = 0 Objekte

def get_score(obj):
    return obj["score"]

#######################
# Segmentation Helpers
#######################
def load_segmentation() -> keras.Model:
    # kagglehub/.../sam_huge_sa1b/5/task.weights.h5 = 2.39GB
    return keras_hub.models.ImageSegmenter.from_preset("sam_huge_sa1b")

def resize_and_pad(x):
    return ops.image.resize(x, IMAGE_SIZE, pad_to_aspect_ratio=True)

def show_image(image, ax):
    ax.imshow(ops.convert_to_numpy(image).astype("uint8"))

def show_mask(mask, ax):
    color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
    h, w, _ = mask.shape
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)

def show_points(points, ax):
    x, y = points[:, 0], points[:, 1]
    ax.scatter(x, y, c="green", marker="*", s=375, ec="white", lw=1.25)

def show_box(box, ax):
    box = box.reshape(-1)
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, ec="red", fc="none", lw=2))
    
class Detector:
    def __init__(self, window_size: tuple[int, int] = IMG_SIZE):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.window_size = window_size
        self.stride = STRIDE
        self.score_threshold = SCORE_THRESHOLD
        self.nms_threshold = 0.2 # zu hoch: 0.5, 0.3
        self.model = load_segmentation()
     
    def segment_anything(self, image: Image.Image):
        # Turns the PIL object into a NumPy matrix
        image_array = keras.utils.img_to_array(image)
        # SAM expect 1024x1024
        image = resize_and_pad(image_array)

        # SAM Poit prompt
        # input_point = np.array([[300,400]]) # Zitrone
        # input_point = np.array([[530,650]]) # Tomaten
        input_point = np.array([[300,270]]) # Banane
        
        # 1 means foreground, and 0 means background.
        input_label = np.array([1])
        
        outputs = self.model.predict(
            {
                "images": ops.expand_dims(image, axis=0),
                "points": ops.expand_dims(input_point, axis=0),
                "labels": ops.expand_dims(input_label, axis=0),
            }
        )
        print(f"OUTPUT_Shape={outputs['masks'].shape}")
        
        def get_mask(sam_outputs, index=0):
            mask = sam_outputs["masks"][0][index]
            mask = np.expand_dims(mask, axis=-1)
            mask = resize_and_pad(mask)
            return ops.convert_to_numpy(mask) > 0.0

        mask = get_mask(outputs, index=0)
        
        plt.figure(figsize=(10,10))
        show_image(image, plt.gca())
        show_mask(mask, plt.gca())
        show_points(input_point, plt.gca())
        plt.show()
        
        # fig, axes = plt.subplots(1, 3, figsize=(20, 60))
        # masks = outputs["masks"][0][1:]
        # for i, mask in enumerate(masks):
        #     show_image(image, axes[i])
        #     show_points(input_point, axes[i])
        #     mask = get_mask(outputs, index=i + 1)
        #     show_mask(mask, axes[i])
        #     axes[i].set_title(f"Mask {i + 1}", fontsize=16)
        #     axes[i].axis("off")
        # plt.show()
     
    # @staticmethod   
    # def _iou(box_a: list[int], box_b: list[int]) -> float:
    #     """Berechnet die Überlappung zweier Boxen."""
    #     # https://learnopencv.com/intersection-over-union-iou-in-object-detection-and-segmentation/
    #     ax1, ay1, ax2, ay2 = box_a
    #     bx1, by1, bx2, by2 = box_b

    #     i_x1 = max(ax1, bx1)
    #     i_y1 = max(ay1, by1)
    #     i_x2 = min(ax2, bx2)
    #     i_y2 = min(ay2, by2)

    #     i_w = max(0, i_x2 - i_x1)
    #     i_h = max(0, i_y2 - i_y1)

    #     intersection = i_w * i_h

    #     area_a = (ax2 - ax1) * (ay2 - ay1)
    #     area_b = (bx2 - bx1) * (by2 - by1)

    #     union = area_a + area_b - intersection
    #     if union > 0:
    #         return intersection / union
    #     else: 
    #         return 0.0

    # def _non_max_suppression(self, objects: list[dict], iou_threshold: float = 0.5,) -> list[dict]:
    #     """NMS-Algorithmus."""
    #     if not objects:
    #         return []

    #     objects = sorted(
    #         objects,
    #         key=get_score,
    #         reverse=True,
    #     )

    #     keep = []

    #     while objects:
    #         best = objects.pop(0)
    #         keep.append(best)

    #         objects = [
    #             obj
    #             for obj in objects
    #             if self._iou(best["box"], obj["box"]) < iou_threshold
    #         ]

    #     return keep

    # def _sliding_window(self, img_w: int, img_h: int):
    #     win_w, win_h = self.window_size
        
    #     for y in range(0, img_h - win_h + 1, self.stride):
    #         for x in range(0, img_w - win_w + 1, self.stride):
    #             yield x, y, win_w, win_h

    # def _score_crop(self, crop: Image.Image) -> float:
    #     """Berechnet Score für genau einen CROP. """
    #     arr = np.array(crop.resize(IMG_SIZE).convert("RGB"), dtype=np.float32)
    #     arr = keras.applications.efficientnet.preprocess_input(arr)
    #     arr = np.expand_dims(arr, axis=0)
        
    #     feature = self.model.predict(arr, verbose=0)[0]  # (576,)
    #     norm = float(np.linalg.norm(feature))
        
    #     # Normalisiert (Richtwert für MobileNetV2)
    #     return min(1.0, norm / 120.0)

    # def detect_objects(self, image: Image.Image) -> list[dict]:
    #     """
    #     Gibt eine Liste von Dicts zurück:
    #     normalize_detection()=[{"box": [x1, y1, x2, y2], "label": str, "score": float}]
    #     """
    #     img_w, img_h = image.size
    #     results: list[dict] = []

    #     for x, y, win_w, win_h in self._sliding_window(img_w, img_h):
    #         crop = image.crop((x, y, x + win_w, y + win_h))
    #         score = self._score_crop(crop)
            
    #         # Schlechte CROPs verwerfen
    #         if score < self.score_threshold:
    #             continue
            
    #         results.append({
    #             "box": [x, y, x + win_w, y + win_h],
    #             "label": "Produkt", #TODO: remove -> predict: ediable/non_ediable
    #             "score": score,
    #         })
        
    #     # results = self._non_max_suppression(results, iou_threshold=self.nms_threshold)
    #     # results.sort(key=get_score, reverse=True)

    #     #DEBUG:
    #     for id, obj in enumerate(results):
    #         x1, y1, x2, y2 = obj["box"]
    #         crop = image.crop((x1, y1, x2, y2))
    #         score = obj["score"]
            
    #         name = f"detection_{id:02d}_{score:.3f}"
    #         crop.save(os.path.join(LOG_DIR, f"{name}.png"))
        
    #     return results


# Modulschnittstelle
def detect_objects(image: Image.Image) -> list[dict]:
    detector = Detector()
    return detector.detect_objects(image)

# DEBUG:
if __name__ == "__main__":
    # img = Image.open("data/gemuese-box.png")
    # img = Image.open("data/train/edible/banane/banana-e-k (3).png")
    d = Detector()
    # objects = d.detect_objects(img)
    # print(f"detect_objects: {len(objects)} objects found.")
    # ---------------------------------------------------------
    # Loads the image as a Python Imaging Library (PIL) object
    pil_image = keras.utils.load_img("data/gemuese-box.png")
    segment = d.segment_anything(pil_image)
