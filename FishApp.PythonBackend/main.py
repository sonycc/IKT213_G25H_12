from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import numpy as np
import cv2
import tempfile

app = FastAPI(title="Fish Image Processing API")

# Global variable to store the current working image
current_image = None


def save_temp_image(img):
    """Save the image to a temporary file and return its path."""
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    cv2.imwrite(tmp_file.name, img)
    return tmp_file.name


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    global current_image

    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only PNG/JPG files are allowed")

    contents = await file.read()
    np_array = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    current_image = img
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename=file.filename)


@app.post("/rotate")
async def rotate_image(angle: int):
    global current_image
    if current_image is None:
        raise HTTPException(status_code=400, detail="No image uploaded")

    if angle not in [90, 180, 270]:
        raise HTTPException(status_code=400, detail="Angle must be 90, 180, or 270")

    if angle == 90:
        rotated = cv2.rotate(current_image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        rotated = cv2.rotate(current_image, cv2.ROTATE_180)
    else:  # 270
        rotated = cv2.rotate(current_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    current_image[:] = rotated
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="rotated.png")


@app.post("/grayscale")
async def grayscale_image():
    global current_image
    if current_image is None:
        raise HTTPException(status_code=400, detail="No image uploaded")

    gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
    current_image[:] = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="grayscale.png")


@app.post("/crop")
async def crop_image(x1: int, y1: int, x2: int, y2: int):
    global current_image
    if current_image is None:
        raise HTTPException(status_code=400, detail="No image uploaded")

    h, w = current_image.shape[:2]
    if not (0 <= x1 < x2 <= w) or not (0 <= y1 < y2 <= h):
        raise HTTPException(status_code=400, detail="Crop coordinates out of bounds")

    cropped = current_image[y1:y2, x1:x2]
    current_image[:] = cropped
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="cropped.png")


@app.post("/flip_horizontal")
async def flip_horizontal():
    global current_image
    if current_image is None:
        raise HTTPException(status_code=400, detail="No image uploaded")

    flipped_image = cv2.flip(current_image, 1)
    current_image[:] = flipped_image
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="flipped_horizontal.png")


@app.post("/flip_vertical")
async def flip_vertical():
    global current_image
    if current_image is None:
        raise HTTPException(status_code=400, detail="No image uploaded")

    flipped_image = cv2.flip(current_image, 0)
    current_image[:] = flipped_image
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="flipped_vertical.png")

@app.post("/gaussian_blur")
async def gaussian_blur(k_size: int):
    global current_image
    if current_image is None:
        raise HTTPException(status_code=400, detail="No image uploaded")

    gaussian = cv2.GaussianBlur(current_image, (k_size, k_size), cv2.BORDER_DEFAULT)
    current_image[:] = gaussian
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="gaussian_blur.png")


@app.get("/download")
async def download_image():
    global current_image
    if current_image is None:
        raise HTTPException(status_code=400, detail="No image uploaded")

    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="current_image.png")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
