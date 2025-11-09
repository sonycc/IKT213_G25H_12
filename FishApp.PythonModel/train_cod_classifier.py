import os
import json
import time
import random
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models

SEED          = 42
IMG_SIZE      = 224
EPOCHS        = 10
BATCH_TRAIN   = 16
BATCH_VAL     = 32
LR            = 1e-3
NUM_WORKERS   = 0
VAL_SPLIT     = 0.15
USE_TEST_AS_VAL_IF_NO_VAL = True

random.seed(SEED)
torch.manual_seed(SEED)

ROOT = Path(__file__).resolve().parent
OUT  = (ROOT / "exports").resolve()
OUT.mkdir(parents=True, exist_ok=True)

def resolve_data_root() -> Path:

    candidates = [
        Path(os.getenv("FISH_DATASET", "").strip()),
        ROOT / "FishImgDataset",
        ROOT.parent / "FishImgDataset",
    ]
    for p in candidates:
        if p and p.exists():
            return p.resolve()
    raise FileNotFoundError(
        "Could not find FishImgDataset.\n"
        "Tried:\n  - FISH_DATASET env var\n  - ./FishImgDataset\n  - ../FishImgDataset"
    )

DATA_ROOT = (ROOT / "FishImgDataset").resolve()
print("Using DATA_ROOT =", DATA_ROOT)


train_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.RandomResizedCrop(IMG_SIZE, scale=(0.6, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(0.1, 0.1, 0.1, 0.05),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

val_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])


def load_datasets():
    train_dir = DATA_ROOT / "train"
    val_dir   = DATA_ROOT / "val"
    test_dir  = DATA_ROOT / "test"

    if train_dir.exists() and (val_dir.exists() or (USE_TEST_AS_VAL_IF_NO_VAL and test_dir.exists())):
        val_like = val_dir if val_dir.exists() else test_dir
        train_ds = datasets.ImageFolder(str(train_dir), transform=train_tf)
        val_ds   = datasets.ImageFolder(str(val_like),  transform=val_tf)
        class_names = train_ds.classes
    else:
        base_dir  = train_dir if train_dir.exists() else DATA_ROOT
        full_ds   = datasets.ImageFolder(str(base_dir), transform=train_tf)
        class_names = full_ds.classes
        n_total = len(full_ds)
        n_val   = max(1, int(n_total * VAL_SPLIT))
        n_train = n_total - n_val
        train_ds, val_ds = random_split(full_ds, [n_train, n_val])
        val_ds.dataset.transform = val_tf

    print(f"Found {len(class_names)} classes:", class_names[:10], ("..." if len(class_names) > 10 else ""))
    print(f"Train images: {len(train_ds)} | Val images: {len(val_ds)}")
    return train_ds, val_ds, class_names

def make_loaders(train_ds, val_ds):
    train_loader = DataLoader(train_ds, batch_size=BATCH_TRAIN, shuffle=True,
                              num_workers=NUM_WORKERS, pin_memory=True)
    val_loader   = DataLoader(val_ds, batch_size=BATCH_VAL, shuffle=False,
                              num_workers=NUM_WORKERS, pin_memory=True)
    return train_loader, val_loader


def build_model(num_classes: int):
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model

@torch.no_grad()
def eval_acc(model, loader, device):
    model.eval()

    ok = tot = 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        pred = model(x).argmax(1)
        ok  += (pred == y).sum().item()
        tot += y.numel()
    return ok / tot if tot else 0.0

def main():
    train_ds, val_ds, class_names = load_datasets()
    train_loader, val_loader = make_loaders(train_ds, val_ds)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    PIN = device.type == "cuda"

    train_loader = DataLoader(train_ds, batch_size=BATCH_TRAIN, shuffle=True,
                              num_workers=NUM_WORKERS, pin_memory=PIN)
    val_loader = DataLoader(val_ds, batch_size=BATCH_VAL, shuffle=False,
                            num_workers=NUM_WORKERS, pin_memory=PIN)

    model = build_model(len(class_names)).to(device)
    criterion = nn.CrossEntropyLoss()
    opt = optim.Adam(model.parameters(), lr=LR)

    (OUT / "labels.txt").write_text("\n".join(class_names), encoding="utf-8")
    (OUT / "labels.json").write_text(json.dumps(class_names, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "classes.txt").write_text("\n".join(class_names), encoding="utf-8")

    best_acc  = 0.0
    best_path = OUT / "best_model.pt"

    for ep in range(1, EPOCHS + 1):
        t0 = time.time()
        model.train()
        running = 0.0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            loss = criterion(logits, y)
            running += loss.item() * x.size(0)
            opt.zero_grad()
            loss.backward()
            opt.step()

        val_acc = eval_acc(model, val_loader, device)
        train_loss = running / len(train_loader.dataset)
        dt = time.time() - t0
        print(f"epoch {ep:02d}: loss {train_loss:.4f}  val acc {val_acc:.3f}  ({dt:.1f}s)")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({"model": model.state_dict(), "classes": class_names}, best_path)

    print(f"best val acc: {best_acc:.3f}")

    ckpt = torch.load(best_path, map_location="cpu")
    model.load_state_dict(ckpt["model"])
    model.eval().cpu()

    dummy = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)
    onnx_path = OUT / "fish_classifier.onnx"
    with torch.inference_mode():
        torch.onnx.export(
            model, dummy, str(onnx_path),
            input_names=["input"], output_names=["logits"],
            opset_version=18, do_constant_folding=True,
            dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
            training=torch.onnx.TrainingMode.EVAL
        )

    print("Exported ONNX to:", onnx_path)
    print("Saved labels to:", OUT / "labels.txt")

if __name__ == "__main__":
    main()
