from fastapi import APIRouter, File, UploadFile, status
from app.schemas.detection import ScanResponse
from app.services.image_service import validate_and_load_image
from app.services.detection_service import process_detection

from app.services.persistence_service import save_scan_and_detection

router = APIRouter(prefix="/api", tags=["Scan"])

@router.post("/scan", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_item(file: UploadFile = File(...)):
    file_bytes = await file.read()
    content_type = file.content_type or "image/jpeg"
    
    # 1. Validate & load PIL Image
    pil_image = validate_and_load_image(file_bytes, content_type)
    
    # 2. Process image with YOLO detector
    response = process_detection(pil_image)
    
    # 3. Persist scan and detection record
    if response.primary_detection:
        save_scan_and_detection(
            object_name=response.primary_detection.object,
            confidence=response.primary_detection.confidence,
            bounding_box=response.primary_detection.bounding_box.dict() if response.primary_detection.bounding_box else None
        )
        
    return response

