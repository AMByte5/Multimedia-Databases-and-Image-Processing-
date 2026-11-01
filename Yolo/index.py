
from ultralytics import YOLO
from pathlib import Path
import cv2

# =====================================
# CONFIGURATION
# =====================================

# Put the image path you want to test here
IMAGE_PATH = r"C:\Users\LapTop 1\OneDrive\Desktop\iiiiii\image10.png"

# YOLOv8 model
model = YOLO("yolov8n.pt")

# Save results inside your Python project
PROJECT_FOLDER = Path(__file__).resolve().parent
RESULTS_FOLDER = PROJECT_FOLDER / "results"

RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

# =====================================
# RUN OBJECT DETECTION
# =====================================

print("\n==============================")
print("YOLOv8 OBJECT DETECTION")
print("==============================")

print(f"Image: {IMAGE_PATH}")

results = model.predict(
    source=IMAGE_PATH,
    conf=0.01,
    imgsz=640,
    verbose=False
)

result = results[0]

# =====================================
# PRINT DETECTED OBJECTS
# =====================================

print("\nDETECTED OBJECTS:")
print("------------------------------")

if len(result.boxes) == 0:
    print("No objects detected.")

else:
    for index, box in enumerate(result.boxes, start=1):

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        object_name = model.names[class_id]

        print(
            f"{index}. {object_name} "
            f"- Confidence: {confidence * 100:.2f}%"
        )

# =====================================
# DRAW BOUNDING BOXES
# =====================================

# YOLO draws rectangles, object names,
# and confidence scores automatically.
annotated_image = result.plot()

# =====================================
# SAVE DETECTED IMAGE
# =====================================

original_name = Path(IMAGE_PATH).stem

output_path = (
    RESULTS_FOLDER /
    f"{original_name}_detected.png"
)

saved = cv2.imwrite(
    str(output_path),
    annotated_image
)

if not saved:
    raise RuntimeError(
        f"Could not save result: {output_path}"
    )

print("\n==============================")
print("DETECTION COMPLETED")
print("==============================")

print(f"Saved image: {output_path}")
