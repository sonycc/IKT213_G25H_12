from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import numpy as np
import cv2
import tempfile

from func.imageMenuFunc import (rotate_image_func, crop_image_func,
                                flip_horizontal_func, flip_vertical_func, resize_func)
from func.toolsMenuFunc import (grayscale_image_func, gaussian_blur_func,
                                sobel_func, binary_filter_func, textbox_func, color_picker_func, zoom_in_func, zoom_out_func)
from func.shapesMenuFunc import (rectangle_func, circle_func,
                                 ellipse_func, polygon_func, line_func)

from func.onnxFunc import predict, session

app = FastAPI(title="Fish Image Processing API")
current_image = None


def check_image():
    if current_image is None:
        raise HTTPException(status_code=400, detail="No image uploaded")


def save_temp_image(img):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    cv2.imwrite(tmp.name, img)
    return tmp.name

@app.get("/empty_image")
async def empty_image(h, w):
    image = np.zeros((h, w, 3), np.uint8)
    tmp_path = save_temp_image(image)
    return FileResponse(tmp_path, media_type="image/png", filename="empty_image.png")

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.get("/ONNX")
async def onnx():
    global current_image
    check_image()

    preds = predict(current_image, model_session=session)[:3]
    return {
        "onnx": {
            "predictions": [
                {"label": p["label"], "certainty": round(p["score"], 3)} for p in preds
            ]
        }
    }


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    global current_image
    if file.content_type not in ["image/png","image/jpeg","image/jpg"]:
        raise HTTPException(400, "Only PNG/JPG files are allowed")
    contents = await file.read()
    img = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Invalid image file")
    current_image = img
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename=file.filename)


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


@app.post("/textbox")
async def textbox_image(x1, y1, text):
    global current_image
    check_image()

    current_image = textbox_func(current_image, x1, y1, text)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="textbox.png")


@app.post("/color_picker")
async def color_picker(x1, y1):
    global current_image
    check_image()

    color = color_picker_func(current_image, x1, y1)
    return color


@app.post("/crop")
async def crop_image(x1, y1, x2, y2):
    global current_image
    check_image()

    try:
        current_image = crop_image_func(current_image, x1, y1, x2, y2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="cropped.png")


@app.post("/resize")
async def resize_image(x1, y1, x2, y2):
    global current_image
    check_image()

    try:
        current_image = resize_func(current_image, x1, y1, x2, y2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="resized.png")

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

@app.post("/zoom_in")
async def zoom_in():
    global current_image
    check_image()

    current_image = zoom_in_func(current_image)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="zoomed_in.png")


@app.post("/zoom_out")
async def zoom_out():
    global current_image
    check_image()

    current_image = zoom_out_func(current_image)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="zoomed_out.png")

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
    return FileResponse(tmp_path, media_type="image/png", filename="sobel.png")


@app.post("/binary")
async def binary_filter():
    global current_image
    check_image()

    current_image = binary_filter_func(current_image)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="binary_filter.png")


@app.post("/rectangle")
async def rectangle(x1, y1, x2, y2):
    global current_image
    check_image()

    current_image = rectangle_func(current_image, x1, y1, x2, y2)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="rectangle.png")


@app.post("/circle")
async def circle(x1, y1):
    global current_image
    check_image()

    current_image = circle_func(current_image, x1, y1)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="circle.png")


@app.post("/polygon")
async def polygon(array):
    global current_image
    check_image()

    current_image = polygon_func(current_image, array)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="polygon.png")


@app.post("/ellipse")
async def ellipse(x1, y1):
    global current_image
    check_image()

    current_image = ellipse_func(current_image, x1, y1)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="ellipse.png")


@app.post("/line")
async def line(x1, y1, x2, y2):
    global current_image
    check_image()

    current_image = line_func(current_image, x1, y1, x2, y2)
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="line.png")


@app.get("/download")
async def download_image():
    global current_image
    check_image()

    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="current_image.png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
