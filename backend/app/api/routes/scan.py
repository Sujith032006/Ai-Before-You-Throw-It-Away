from fastapi import APIRouter, File, UploadFile, status
from app.schemas.detection import ScanResponse
from app.services.image_service import validate_and_load_image
from app.services.detection_service import process_detection
from app.services.persistence_service import save_scan_and_detection

router = APIRouter(prefix="/api", tags=["Scan & Analyze"])

@router.post("/scan", response_model=ScanResponse, status_code=status.HTTP_200_OK)
@router.post("/analyze", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_item(file: UploadFile = File(...)):
    file_bytes = await file.read()
    content_type = file.content_type or "image/jpeg"
    file_size = len(file_bytes)
    
    # 1. Validate & load PIL Image
    pil_image = validate_and_load_image(file_bytes, content_type)
    
    # 2. Process image with Stage 1 Object Identification + Stage 2 Support Lookup
    response = process_detection(pil_image, file_size_bytes=file_size)
    
    # 3. Persist scan and detection record if valid detection exists
    target_object = None
    if response.analysis and response.analysis.object and response.analysis.object.name != "unknown":
        target_object = response.analysis.object.name
    elif response.primary_detection:
        target_object = response.primary_detection.object

    if target_object:
        saved_scan_id = save_scan_and_detection(
            object_name=target_object,
            confidence=response.analysis.confidence if response.analysis else (response.primary_detection.confidence if response.primary_detection else 0.90)
        )
        response.scan_id = saved_scan_id
        
    return response
