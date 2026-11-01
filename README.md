# Multimedia Databases and Image Processing

Independent projects, each in its own top-level folder:

| Folder | Project |
|---|---|
| `ImagePoisoningJava/` | Original Java image attack project (Java 21 / Maven). |
| `imagepoisoningpy/` | Python adversarial image attacks. |
| `Yolo/` | Python YOLO detector (`index.py`). |
| `image poisoning defense.py/` | Python automatic attack tagging and image defenses. |

Open the individual project folder in your IDE. For Java, open `ImagePoisoningJava/pom.xml` or run Maven inside that folder. The repository root is a collection of projects, not a Maven project.

Python virtual environments, local model weights, caches, and generated images are excluded by each project's `.gitignore`. Install dependencies locally. The YOLO script uses Ultralytics and OpenCV and loads `yolov8n.pt`; configure its input image path before running.
