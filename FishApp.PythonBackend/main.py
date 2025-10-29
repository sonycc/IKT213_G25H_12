from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import numpy as np, cv2, tempfile, os
import onnxruntime as ort

app = FastAPI(title="Fish Image Processing API")
current_image = None

def save_temp_image(img):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    cv2.imwrite(tmp.name, img)
    return tmp.name

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.get("/ONNX")
async def onnx():
    # Placeholder response shaped similar to your example
    return {
        "not implementet": {
            "detected": ["name"],     # replace with actual detected label
            "certainty": "75%"        # replace with actual certainty (as percent string)
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
    return FileResponse(save_temp_image(current_image), media_type="image/png", filename=file.filename)

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

    current_image = rotated
    tmp_path = save_temp_image(current_image)
    return FileResponse(tmp_path, media_type="image/png", filename="rotated.png")


@app.post("/grayscale")
async def grayscale_image():
    global current_image
    if current_image is None: raise HTTPException(400, "No image uploaded")
    gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
    current_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return FileResponse(save_temp_image(current_image), media_type="image/png", filename="grayscale.png")

@app.post("/crop")
async def crop_image(x1:int, y1:int, x2:int, y2:int):
    global current_image
    if current_image is None: raise HTTPException(400, "No image uploaded")
    h,w = current_image.shape[:2]
    if not (0<=x1<x2<=w and 0<=y1<y2<=h): raise HTTPException(400, "Crop coordinates out of bounds")
    current_image = current_image[y1:y2, x1:x2]
    return FileResponse(save_temp_image(current_image), media_type="image/png", filename="cropped.png")

@app.get("/download")
async def download_image():
    global current_image
    if current_image is None: raise HTTPException(400, "No image uploaded")
    return FileResponse(save_temp_image(current_image), media_type="image/png", filename="current_image.png")

# ===== ONNX classifier =====
MODEL_PATH = os.getenv("COD_MODEL_PATH", os.path.join(os.path.dirname(__file__), "cod_classifier.onnx"))
CLASSES_PATH = os.getenv("COD_CLASSES_PATH", os.path.join(os.path.dirname(__file__), "classes.txt"))

try:
    ort_session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
    with open(CLASSES_PATH, "r") as f:
        class_names = [ln.strip() for ln in f if ln.strip()]
except Exception as e:
    ort_session = None
    class_names = None
    print("[WARN] Model not ready:", e)

IM_MEAN = np.array([0.485,0.456,0.406], dtype=np.float32)
IM_STD  = np.array([0.229,0.224,0.225], dtype=np.float32)

def preprocess_bgr_to_nchw(img_bgr):
    img = cv2.resize(img_bgr, (256,256), interpolation=cv2.INTER_AREA)
    s = (256-224)//2
    img = img[s:s+224, s:s+224]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)/255.0
    img = (img - IM_MEAN) / IM_STD
    chw = np.transpose(img, (2,0,1))
    return np.expand_dims(chw, 0).astype(np.float32)

def softmax(logits):
    l = logits - logits.max(axis=1, keepdims=True)
    e = np.exp(l)
    return e / e.sum(axis=1, keepdims=True)

@app.post("/predict")
async def predict(file: UploadFile | None = File(default=None)):
    global current_image
    if ort_session is None or not class_names:
        raise HTTPException(503, "Model not loaded on server")

    if file is not None:
        contents = await file.read()
        img = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
        if img is None: raise HTTPException(400, "Invalid image file")
    else:
        if current_image is None: raise HTTPException(400, "No image provided and no current image uploaded")
        img = current_image.copy()

    x = preprocess_bgr_to_nchw(img)
    input_name = ort_session.get_inputs()[0].name
    logits = ort_session.run(None, {input_name: x})[0]
    prob = softmax(logits)[0]
    best_idx = int(np.argmax(prob))
    best_label = class_names[best_idx]

    # cod probability
    cod_names = [n for n in class_names if n.lower() in ("cod","torsk")]
    if cod_names and cod_names[0] in class_names:
        cod_idx = class_names.index(cod_names[0])
        cod_prob = float(prob[cod_idx])
    else:
        cod_prob = float(prob[best_idx]) if "cod" in best_label.lower() else float(1.0 - prob[best_idx])

    return JSONResponse({
        "label": best_label,
        "probability_cod": round(cod_prob, 4),
        "probabilities": {class_names[i]: float(prob[i]) for i in range(len(class_names))}
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
