import io
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_dummy_image_bytes():
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), color="blue")
    image.save(file, "jpeg")
    file.seek(0)
    return file.read()

def test_scan_invalid_file_type():
    response = client.post(
        "/api/scan",
        files={"file": ("test.txt", b"hello world", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported image format" in response.json()["detail"]

def test_scan_valid_image():
    image_bytes = create_dummy_image_bytes()
    response = client.post(
        "/api/scan",
        files={"file": ("test.jpg", image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "detections" in data
