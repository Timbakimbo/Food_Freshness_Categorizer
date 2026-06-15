import os
import PIL.Image as Image
from operator import itemgetter
from predict import predict_image

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")

class ObjectDetector:
    def __init__(self, window_size=(224, 224), stride=32):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.window_size = window_size  # sliding window size TODO: 224x224 prediction size ?!?
        self.stride = stride  # how much to move the window for each step
    
    def sliding_window(self, img_w, img_h):
        """Generate sliding windows over the input image."""
    
        for win_w, win_h in [self.window_size]:
            if win_w > img_w or win_h > img_h:
                continue  # Skip if window size is larger than the image
            for y in range(0, img_h - win_h + 1, self.stride):
                for x in range(0, img_w - win_w + 1, self.stride):
                    # Generate the actual window and yield it for predict.py
                    yield (x, y, win_w, win_h)

    #TODO: Hinzufügen von 
    # 1.) Extrahieren der Features bei jedem CROP 
    # 2.) Überlappende CROPS wegwerfen (Vorfiltern)
    # 3.) Prüfen ob ein CROP überhaupt für prediction in Frage kommt mit einem Classifier oder iwas statistisches (Konsinus-Ähnlichkeit) ?!?
    def detect_objects(self, image: Image.Image) -> list[dict]:
        """Detect objects using sliding window. Accepts PIL.Image directly."""
        img = Image.open(image).convert("RGB")
        img_w, img_h = img.size
        detections = []

        for x, y, win_w, win_h in self.sliding_window(img_w, img_h):
            crop = img.crop((x, y, x + win_w, y + win_h))

            tmp_path = "/tmp/crop.jpg"
            crop.save(tmp_path)

            label, confidence, _ = predict_image(tmp_path)
            detections.append({
                "label": label,
                "score": confidence,
                "bbox": [x, y, x + win_w, y + win_h],  # w/h → x2/y2
            })

        if detections:
            best = max(detections, key=itemgetter("score"))
            stem = f"detection_{int(best['score'] * 100)}"
            x1, y1, x2, y2 = best["bbox"]
            best_crop = img.crop((x1, y1, x2, y2))
            score_pct = int(best["score"] * 100)
            best_crop.save(os.path.join(LOG_DIR, f"{stem}_detection_{score_pct}.jpg"))
            
        return detections

if __name__ == "__main__":
    detector = ObjectDetector()
    # detections = detector.detect_objects("data/bio-gemuese-box-640x480.jpg")
    detections = detector.detect_objects("data/gemuese-box.png")
    # detections = detector.detect_objects("data/train/edible/paprika/freshPepper (143).jpg")
    # print(detections)
    print(f"detect_objects: {len(detections)} detections found.")
        