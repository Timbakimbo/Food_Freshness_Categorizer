import os
import numpy as np
import keras
import PIL.Image as Image
import tensorflow as tf

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
IMG_SIZE = (224, 224)
STRIDE = 64
SCORE_THRESHOLD = 0.25

def load_model() -> keras.Model:
    """Feature-Extraktor."""
    # backbone = keras.applications.MobileNetV3Small(
    #     input_shape=(*IMG_SIZE, 3),
    #     include_top=False,
    #     pooling="avg",
    #     weights="imagenet",
    # ) 
    # = 0 Objekte
    backbone = keras.applications.MobileNetV2(
        name="mobilenet_v2",
        weights="imagenet",
        pooling="avg",
        include_top=False,
        input_shape=(*IMG_SIZE, 3)
    )
    # = 12 Objekte
    backbone.trainable = False
    return backbone
    # return tf.keras.models.load_model("models/freshify_baseline_with_new_raw.keras") # = 0 Objekte


class Detector:
    def __init__(self, window_size: tuple[int, int] = IMG_SIZE):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.window_size = window_size
        self.stride = STRIDE
        self.score_threshold = SCORE_THRESHOLD
        self.model = load_model()

    def _sliding_window(self, img_w: int, img_h: int):
        win_w, win_h = self.window_size
        
        for y in range(0, img_h - win_h + 1, self.stride):
            for x in range(0, img_w - win_w + 1, self.stride):
                yield x, y, win_w, win_h

    def _score_crop(self, crop: Image.Image) -> float:
        """Berechnet Score für genau einen CROP. """
        arr = np.array(crop.resize(IMG_SIZE).convert("RGB"), dtype=np.float32)
        arr = keras.applications.mobilenet_v2.preprocess_input(arr)
        arr = np.expand_dims(arr, axis=0)
        
        feature = self.model.predict(arr, verbose=0)[0]  # (576,)
        norm = float(np.linalg.norm(feature))
        
        # Normalisiert (Richtwert für MobileNetV2)
        return min(1.0, norm / 120.0)

    def detect_objects(self, image: Image.Image) -> list[dict]:
        """
        Gibt eine Liste von Dicts zurück:
        normalize_detection()=[{"box": [x1, y1, x2, y2], "label": str, "score": float}]
        """
        img_w, img_h = image.size
        results: list[dict] = []

        for x, y, win_w, win_h in self._sliding_window(img_w, img_h):
            crop = image.crop((x, y, x + win_w, y + win_h))
            score = self._score_crop(crop)
            
            # Schlechte CROPs verwerfen
            if score < self.score_threshold:
                continue
            
            # DEBUG:
            # stem = f"detection_{(score * 100)}"
            # crop.save(os.path.join(LOG_DIR, f"{stem}.png"))
            
            # CROPS mit Feature=Gemüse/Obst
            results.append({
                "box": [x, y, x + win_w, y + win_h],
                "label": "Produkt", #TODO: Wofür?
                "score": score,
            })

        return results


# Modulschnittstelle
def detect_objects(image: Image.Image) -> list[dict]:
    detector = Detector()
    return detector.detect_objects(image)

# DEBUG:
# if __name__ == "__main__":
#     img = Image.open("data/gemuese-box.png")
#     d = Detector()
#     detections = d.detect_objects(img)
#     print(f"detect_objects: {len(detections)} detections found.")