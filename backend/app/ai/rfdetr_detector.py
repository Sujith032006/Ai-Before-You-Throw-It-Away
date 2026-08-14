from typing import List
from PIL import Image
import logging
from app.utils.config import RFDETR_MODEL
from app.schemas.detection import DetectionItem, BoundingBox

logger = logging.getLogger(__name__)

# Standard COCO to Upcycling Object Mappings for RF-DETR
RFDETR_CLASS_MAPPINGS = {
    # Packaging & Containers
    "bottle": ("plastic_bottle", "Plastic Bottle", "Plastic (PET)", "Household Container"),
    "cup": ("tin_can", "Tin Can / Beverage Cup", "Aluminum / Metal", "Kitchen Container"),
    "bowl": ("tin_can", "Food Bowl / Metal Can", "Metal / Ceramic", "Kitchen Container"),
    "vase": ("glass_jar", "Glass Jar", "Glass", "Glass Container"),
    "wine glass": ("glass_jar", "Glass Jar", "Glass", "Glass Container"),
    "box": ("cardboard_box", "Cardboard Box", "Cardboard / Paper", "Packaging Waste"),
    "suitcase": ("cardboard_box", "Cardboard Box / Case", "Paper / Plastic", "Packaging Waste"),

    # Electronics & E-Waste
    "remote": ("remote_control", "Remote Control", "Plastic & Circuit Board", "Electronic Waste"),
    "cell phone": ("cell_phone", "Cell Phone / Smart Device", "Glass, Metal & Electronics", "Electronic Waste"),
    "laptop": ("e_waste", "Laptop / Portable Computer", "Aluminum & Electronics", "Electronic Waste"),
    "tv": ("e_waste", "Appliance / Screen", "Plastic & Electronics", "Electronic Waste"),
    "mouse": ("e_waste", "Computer Mouse", "Plastic & Wire", "Electronic Waste"),
    "keyboard": ("e_waste", "Computer Keyboard", "Plastic & Electronics", "Electronic Waste"),
    "clock": ("clock", "Wall Clock / Timer", "Plastic & Metal", "Household Hardware"),

    # Clothing & Textiles
    "handbag": ("old_tshirt", "Old Fabric / Tote Bag", "Textile / Fabric", "Clothing & Textile"),
    "backpack": ("old_tshirt", "Old Fabric Backpack", "Textile / Fabric", "Clothing & Textile"),
    "tie": ("old_tshirt", "Old Fabric / Tie", "Textile / Fabric", "Clothing & Textile"),

    # Furniture & Seating
    "chair": ("plastic_chair", "Plastic / Wooden Chair", "Molded Plastic / Wood", "Furniture Waste"),
    "couch": ("plastic_chair", "Sofa / Seating Chair", "Textile & Wood", "Furniture Waste"),
    "dining table": ("plastic_chair", "Table / Furniture", "Wood & Plastic", "Furniture Waste"),

    # Paper
    "book": ("book", "Old Book", "Paper & Cardboard", "Paper Waste")
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

            # Map class name to normalized object class if known
            if cls_name in RFDETR_CLASS_MAPPINGS:
                obj_key, display_name, material, category = RFDETR_CLASS_MAPPINGS[cls_name]
            else:
                obj_key = cls_name.replace(" ", "_")
                display_name = cls_name.title()
                material = "Reusable Material"
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
