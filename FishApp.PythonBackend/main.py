from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import numpy as np
import cv2
import tempfile

from func.imageMenuFunc import (rotate_image_func, crop_image_func,
                                flip_horizontal_func, flip_vertical_func)
from func.toolsMenuFunc import (grayscale_image_func, gaussian_blur_func,
                                sobel_func, binary_filter_func)
from func.onnxFunc import predict

app = FastAPI(title="Fish Image Processing API")

# Global variable to store the current working image
current_image = None


def check_image():
    if current_image is None:
        raise HTTPException(status_code=400, detail="No image uploaded")


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


@app.post("/predict")
async def predict_image():
    global current_image
    check_image()

    output = predict(current_image)
    return JSONResponse({"predictions": output})


@app.post("/rotate")
async def rotate_image(angle: int):
    global current_image
    check_image()

    try:
        current_image = rotate_image_func(current_image, angle)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="rotated.png")


@app.post("/grayscale")
async def grayscale_image():
    global current_image
    check_image()

    current_image = grayscale_image_func(current_image)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="grayscale.png")


@app.post("/crop")
async def crop_image(x1: int, y1: int, x2: int, y2: int):
    global current_image
    check_image()

    try:
        current_image = crop_image_func(current_image, x1, y1, x2, y2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="cropped.png")


@app.post("/flip_horizontal")
async def flip_horizontal():
    global current_image
    check_image()

    current_image = flip_horizontal_func(current_image)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="flipped_horizontal.png")


@app.post("/flip_vertical")
async def flip_vertical():
    global current_image
    check_image()

    current_image = flip_vertical_func(current_image)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="flipped_vertical.png")


@app.post("/gaussian_blur")
async def gaussian_blur(k_size: int):
    global current_image
    check_image()

    current_image = gaussian_blur_func(current_image, k_size)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="gaussian_blur.png")


@app.post("/sobel")
async def sobel(k_size: int):
    global current_image
    check_image()

    current_image = sobel_func(current_image, k_size)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="gaussian_blur.png")

@app.post("/binary")
async def binary_filter():
    global current_image
    check_image()

    current_image = binary_filter_func(current_image)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="binary_filter.png")


@app.get("/download")
async def download_image():
    global current_image
    check_image()

    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="current_image.png")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
