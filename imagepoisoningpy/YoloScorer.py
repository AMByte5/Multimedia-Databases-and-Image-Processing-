class YoloScorer:
    def __init__(self, model, confidence, imgsz, class_id, device):
        self.model, self.confidence, self.imgsz = model, confidence, imgsz
        self.class_id, self.device = class_id, device

    def predict(self, rgb):
        # Ultralytics numpy sources expect BGR, whereas Pillow uses RGB.
        result = self.model.predict(source=rgb[:, :, ::-1].copy(), conf=self.confidence,
                                    imgsz=self.imgsz, device=self.device, verbose=False,
                                    save=False)[0]
        if result.boxes is None:
            raise ValueError("Use a YOLO object-detection model, not classification weights.")
        detections = []
        for box in result.boxes:
            cls = int(box.cls[0].item())
            detections.append({"class_id": cls, "name": result.names[cls],
                               "confidence": float(box.conf[0].item()),
                               "xyxy": box.xyxy[0].cpu().tolist()})
        selected = [d for d in detections if self.class_id is None or d["class_id"] == self.class_id]
        return max((d["confidence"] for d in selected), default=0.0), detections, result

    def __call__(self, rgb):
        return self.predict(rgb)[0]
