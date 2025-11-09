import cv2
from PIL import Image
import numpy as np
import onnxruntime as ort

session = ort.InferenceSession("../FishApp.PythonModel/exports/fish_classifier.onnx")
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

def predict(image, model_session=None):
    # Convert to RGB, PIL uses RBG
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)

    # Improve image to match the model
    img = pil_img.resize((224, 224))
    x = np.array(img).astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    x = (x - mean) / std
    x = np.transpose(x, (2, 0, 1))
    x = np.expand_dims(x, 0).astype(np.float32)

    # run model
    result = model_session.run([output_name], {input_name: x})[0][0]

    # convert to probability
    exp = np.exp(result - np.max(result))
    probs = exp / np.sum(exp)
    top = np.argsort(-probs)[:3]

    with open("../FishApp.PythonModel/exports/labels.txt", "r") as f:
        labels = [line.strip() for line in f.readlines()]

    output = [
        {"label": labels[i], "score": round(float(probs[i]) * 100, 2)}
        for i in top
    ]

    print("Raw model output:", result)
    print("Softmax probs (top 10):", sorted(probs, reverse=True)[:10])

    print("Output shape:", result.shape)
    return output

