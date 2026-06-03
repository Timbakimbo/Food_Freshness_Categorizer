import cv2
import tensorflow as tf
import keras_cv
import matplotlib.pyplot as plt

from util import get_next_index

# -----------------------------------
# CONFIG
# -----------------------------------

IMAGE_PATH = "data/yolo/bananen-box.jpg"

# COCO food classes in YOLOv8 COCO model
FOOD_CLASS_IDS = {
    46,  # banana
    47,  # apple
    48,  # sandwich
    49,  # orange
    50,  # broccoli
    51,  # carrot
    52,  # hot dog
    53,  # pizza
    54,  # donut
    55,  # cake
}

# -----------------------------------
# LOAD IMAGE
# -----------------------------------

image_bgr = cv2.imread(IMAGE_PATH)

if image_bgr is None:
    raise ValueError(f"Bild nicht gefunden: {IMAGE_PATH}")

image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
image = cv2.resize(image_rgb, (640, 640))  # YOLOv8 erwartet als größe ein Vielfaches von 32, also 640x640, 416x416, 320x320 etc.

# YOLOv8 erwartet Batch-Dimension
input_image = tf.convert_to_tensor(image, dtype=tf.float32)
input_image = tf.expand_dims(input_image, axis=0)

# -----------------------------------
# LOAD BACKBONE
# -----------------------------------

backbone = keras_cv.models.YOLOV8Backbone.from_preset(
    "yolo_v8_s_backbone_coco"
)

# -----------------------------------
# BUILD DETECTOR
# -----------------------------------
model = keras_cv.models.YOLOV8Detector(
    num_classes=80,
    bounding_box_format="xyxy",
    backbone=backbone,
    fpn_depth=1,
)
# # print(keras_cv.models.YOLOV8Detector.presets.keys())

# -----------------------------------
# PREDICT
# -----------------------------------
predictions = model.predict(input_image)

# -----------------------------------
# DRAW ONLY FOOD BOXES
# -----------------------------------
boxes = predictions["boxes"][0]
classes = predictions["classes"][0]
confidence = predictions["confidence"][0]

output = image.copy()
for box, cls, score in zip(boxes, classes, confidence):

    cls = int(cls)
    
    # ignore non-food classes
    if cls not in FOOD_CLASS_IDS:
        continue

    # ignore weak detections
    if score < 0.5:
        continue

    x1, y1, x2, y2 = map(int, box)

    cv2.rectangle(
        output,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )

    label = f"{cls} {score:.2f}"

    cv2.putText(
        output,
        label,
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        2
    )

# save output image
i = get_next_index()
cv2.imwrite(f"data/yolo/output_{i}.jpg", cv2.cvtColor(output, cv2.COLOR_RGB2BGR))

# -----------------------------------
# SHOW RESULT
# -----------------------------------

plt.figure(figsize=(10,10))
plt.imshow(output)
plt.axis("off")
plt.show()