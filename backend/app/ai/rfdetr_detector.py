from typing import List
from PIL import Image
import logging
from app.utils.config import RFDETR_MODEL
from app.schemas.detection import DetectionItem, BoundingBox

logger = logging.getLogger(__name__)

# Open-World COCO Class Mappings (returns base physical object name & raw detection)
RFDETR_CLASS_MAPPINGS = {
    # Containers & Glassware
    "bottle": ("bottle", "Bottle", "unknown", "Containers"),
    "cup": ("cup", "Cup / Mug", "unknown", "Containers"),
    "bowl": ("bowl", "Bowl / Container", "unknown", "Containers"),
    "vase": ("glass_jar", "Vase / Glass Jar", "glass", "Glassware"),
    "wine glass": ("glass_jar", "Glassware", "glass", "Glassware"),
    "box": ("cardboard_box", "Cardboard Box", "cardboard", "Packaging Waste"),
    "suitcase": ("bag", "Suitcase / Luggage", "fabric", "Bags & Luggage"),

    # Electronics & Appliances
    "remote": ("remote_control", "Remote Control", "plastic & electronics", "Electronic Waste"),
    "cell phone": ("smartphone", "Mobile Phone", "glass & electronics", "Electronics"),
    "laptop": ("laptop", "Laptop Computer", "metal & electronics", "Electronics"),
    "tv": ("monitor", "Screen / Monitor", "plastic & electronics", "Electronics"),
    "mouse": ("mouse", "Computer Mouse", "plastic & wire", "Electronics"),
    "keyboard": ("keyboard", "Computer Keyboard", "plastic & electronics", "Electronics"),
    "clock": ("clock", "Clock", "plastic & metal", "Household Hardware"),

    # Clothing & Accessories
    "handbag": ("bag", "Handbag", "fabric", "Bags & Accessories"),
    "backpack": ("bag", "Backpack", "fabric", "Bags & Accessories"),
    "tie": ("clothing", "Fabric Tie", "fabric", "Clothing"),

    # Furniture & Seating
    "chair": ("chair", "Chair", "unknown", "Furniture"),
    "couch": ("couch", "Sofa / Couch", "fabric & wood", "Furniture"),
    "dining table": ("table", "Dining Table", "wood & plastic", "Furniture"),
    "bed": ("bed", "Bed Frame", "wood & fabric", "Furniture"),

    # Media & Paper
    "book": ("book", "Book", "paper", "Paper & Books")
}

class RFDETRDetector:
    """
    Primary RF-DETR (Real-Time Detection Transformer) Object Detector.
    Initialized once on Python service startup.
    """
    def __init__(self, model_name: str = RFDETR_MODEL):
        self.model_name = model_name
        self.model = None

    def load_model(self):
        if self.model is None:
            logger.info(f"[RF-DETR Detector] Loading model '{self.model_name}' into memory...")
            from ultralytics import RTDETR
            self.model = RTDETR(self.model_name)
            logger.info(f"[RF-DETR Detector] Model '{self.model_name}' loaded successfully.")

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

        img_w, img_h = image.size

        for box in boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            cls_name = result.names.get(cls_id, f"object_{cls_id}").lower().strip()

            xyxy = box.xyxy[0].tolist()
            x1 = max(0.0, round(xyxy[0], 2))
            y1 = max(0.0, round(xyxy[1], 2))
            x2 = min(float(img_w), round(xyxy[2], 2))
            y2 = min(float(img_h), round(xyxy[3], 2))

            bbox = BoundingBox(
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2
            )

            # Map class name to base object if known
            if cls_name in RFDETR_CLASS_MAPPINGS:
                obj_key, display_name, material, category = RFDETR_CLASS_MAPPINGS[cls_name]
            else:
                obj_key = cls_name.replace(" ", "_")
                display_name = cls_name.title()
                material = "unknown"
                category = "Household Object"

            detections.append(
                DetectionItem(
                    object=obj_key,
                    display_name=display_name,
                    confidence=round(conf, 4),
                    material=material,
                    category=category,
                    bounding_box=bbox
                )
            )

        # Sort detections by confidence descending
        detections.sort(key=lambda d: d.confidence, reverse=True)
        return detections

# Singleton instance pre-initialized
rfdetr_detector = RFDETRDetector()
