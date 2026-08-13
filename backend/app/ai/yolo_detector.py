from typing import List
from PIL import Image
from ultralytics import YOLO
from app.utils.config import YOLO_MODEL
from app.schemas.detection import DetectionItem, BoundingBox

class YOLODetector:
    def __init__(self, model_name: str = YOLO_MODEL):
        self.model_name = model_name
        self.model = None

    def load_model(self):
        if self.model is None:
            # Loads lightweight pretrained YOLO model (downloads on first run if needed)
            self.model = YOLO(self.model_name)

    def detect(self, image: Image.Image) -> List[DetectionItem]:
        self.load_model()
        results = self.model(image)
        detections: List[DetectionItem] = []

        if not results:
            return detections

        result = results[0]
        boxes = result.boxes

        if boxes is None or len(boxes) == 0:
            return detections

        for box in boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            cls_name = result.names.get(cls_id, f"object_{cls_id}")

            # Formatting display name (e.g., 'sports ball' -> 'Sports Ball', 'bottle' -> 'Bottle')
            display_name = cls_name.replace("_", " ").title()

            xyxy = box.xyxy[0].tolist()
            bbox = BoundingBox(
                x1=round(xyxy[0], 2),
                y1=round(xyxy[1], 2),
                x2=round(xyxy[2], 2),
                y2=round(xyxy[3], 2)
            )

            detections.append(
                DetectionItem(
                    object=cls_name.lower().replace(" ", "_"),
                    display_name=display_name,
                    confidence=round(conf, 4),
                    bounding_box=bbox
                )
            )

        # Sort detections by confidence descending
        detections.sort(key=lambda d: d.confidence, reverse=True)
        return detections

# Singleton instance
yolo_detector = YOLODetector()
