import onnxruntime as ort
import numpy as np
from PIL import Image

# --- last modell ---
session = ort.InferenceSession("resnet50-v2-7.onnx")
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# --- last labels ---
with open("synset.txt") as f:
    labels = [line.strip() for line in f]


def predict(image_path, normalize=True):
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    x = np.array(img).astype("float32") / 255.0

    if normalize:
        # normalisering (ImageNet) – hold ALT som float32
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        x = (x - mean) / std

        # ... etter transpose/expand_dims:
    x = np.transpose(x, (2, 0, 1))
    x = np.expand_dims(x, 0).astype(np.float32)  # <- sørg for float32 inn til modellen

    out = session.run([output_name], {input_name: x})[0][0]
    exp = np.exp(out - np.max(out))
    probs = exp / np.sum(exp)
    top = np.argsort(-probs)[:3]
    return [(labels[i], probs[i] * 100) for i in top]


# --- test med og uten normalisering ---
print("🐶 Testing på dog.jpg ...\n")

print("👉 Uten normalisering:")
for label, score in predict("../dog1.jpg", normalize=False):
    print(f"  {label}: {score:.1f}%")

print("\n👉 Med normalisering:")
for label, score in predict("../dog1.jpg", normalize=True):
    print(f"  {label}: {score:.1f}%")
