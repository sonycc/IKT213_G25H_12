import json
import time
import random
from pathlib import Path
from typing import List, Dict

import torch
import torch.nn as nn
import torch.optim as optim
import torch.backends.cudnn as cudnn
from torch.utils.data import DataLoader, random_split, ConcatDataset
from torchvision import datasets, transforms, models

SEED          = 42
IMG_SIZE      = 224
EPOCHS        = 10
BATCH_TRAIN   = 16
BATCH_VAL     = 32
LR            = 1e-3
NUM_WORKERS   = 16
VAL_SPLIT     = 0.15
USE_TEST_AS_VAL_IF_NO_VAL = False
USE_GRAY_DUPLICATE_AUG = True
USE_ROTATE_DUPLICATE_AUG = True

random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    cudnn.benchmark = True
    try:
        torch.set_float32_matmul_precision("high")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
OUT  = (ROOT / "exports").resolve()
OUT.mkdir(parents=True, exist_ok=True)

DATA_ROOT = (ROOT / "FishImgDataset").resolve()
if not DATA_ROOT.exists():
    raise FileNotFoundError(f"Expected dataset folder at {DATA_ROOT} (with train/ val/ test/).")

train_dir = DATA_ROOT / "train"
val_dir   = DATA_ROOT / "val"
test_dir  = DATA_ROOT / "test"
for d in (train_dir, val_dir):
    if not d.exists():
        raise FileNotFoundError(f"Missing required folder: {d}")

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

eval_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])
def build_train_dataset_augmented(
    train_dir: Path,
    base_tf: transforms.Compose,
    img_size: int,
    use_gray_dupes: bool,
    use_rotate_dupes: bool,
):

    base_train = datasets.ImageFolder(str(train_dir), transform=base_tf)
    class_names = base_train.classes

    parts = [base_train]
    msg_parts = [f"{len(base_train)} original"]

    if use_gray_dupes:
        gray_tf = transforms.Compose([
            transforms.Resize(256),
            transforms.RandomResizedCrop(img_size, scale=(0.6, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.Grayscale(num_output_channels=3),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225]),
        ])
        gray_train = datasets.ImageFolder(str(train_dir), transform=gray_tf)
        parts.append(gray_train)
        msg_parts.append(f"{len(gray_train)} grayscale")

    if use_rotate_dupes:
        rot_tf = transforms.Compose([
            transforms.Resize(256),
            transforms.RandomResizedCrop(img_size, scale=(0.6, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(degrees=(-25, 25)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225]),
        ])
        rot_train = datasets.ImageFolder(str(train_dir), transform=rot_tf)
        parts.append(rot_train)
        msg_parts.append(f"{len(rot_train)} rotated")

    if len(parts) == 1:
        return base_train, class_names

    train_ds = ConcatDataset(parts)
    print(f"[AUG] Using dataset augmentation: {' + '.join(msg_parts)} = {len(train_ds)} total")
    return train_ds, class_names

def load_datasets():
    test_ds = datasets.ImageFolder(str(test_dir), transform=eval_tf) if test_dir.exists() else None

    val_like = val_dir if val_dir.exists() else (test_ds if USE_TEST_AS_VAL_IF_NO_VAL else None)
    if val_like is None:
        raise FileNotFoundError("Need a val/ folder or set USE_TEST_AS_VAL_IF_NO_VAL=True with a test/ folder.")

    train_ds, class_names = build_train_dataset_augmented(
        train_dir=train_dir,
        base_tf=train_tf,
        img_size=IMG_SIZE,
        use_gray_dupes=USE_GRAY_DUPLICATE_AUG,
        use_rotate_dupes=USE_ROTATE_DUPLICATE_AUG,
    )

    val_ds = datasets.ImageFolder(str(val_like), transform=eval_tf)

    if test_ds is not None and set(test_ds.classes) != set(class_names):
        print("[WARN] Test set classes differ from training classes (by name).")

    print(f"Found {len(class_names)} classes:", class_names[:10], ("..." if len(class_names) > 10 else ""))
    print(f"Train images: {len(train_ds)} | Val images: {len(val_ds)} | Test images: {len(test_ds) if test_ds else 0}")
    return train_ds, val_ds, test_ds, class_names

def make_loader(ds, batch, shuffle, pin):
    if ds is None:
        return None
    return DataLoader(ds, batch_size=batch, shuffle=shuffle,
                      num_workers=NUM_WORKERS, pin_memory=pin)

def build_model(num_classes: int):
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


@torch.no_grad()
def eval_acc(model, loader, device, amp_enabled: bool):
    if loader is None:
        return 0.0
    model.eval()
    ok = tot = 0
    ctx = torch.cuda.amp.autocast() if (amp_enabled and device.type == "cuda") else torch.no_grad()
    with ctx:
        for x, y in loader:
            x = x.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)
            pred = model(x).argmax(1)
            ok  += (pred == y).sum().item()
            tot += y.numel()
    return ok / tot if tot else 0.0

def eval_test_and_dump(model: nn.Module, loader: DataLoader, device: torch.device,
                       class_names: List[str], out_dir: Path) -> Dict:
    model.eval()
    ds = loader.dataset
    single_loader = DataLoader(ds, batch_size=1, shuffle=False,
                               num_workers=NUM_WORKERS, pin_memory=(device.type=="cuda"))
    softmax = nn.Softmax(dim=1)
    correct = total = 0
    per_cls_ok  = {c: 0 for c in class_names}
    per_cls_tot = {c: 0 for c in class_names}

    out_csv = out_dir / "test_predictions.csv"
    with out_csv.open("w", encoding="utf-8") as f:
        f.write("image_path,true_label,top1,top1_prob,top2,top2_prob,top3,top3_prob\n")
        with (torch.cuda.amp.autocast() if device.type=="cuda" else torch.no_grad()):
            for i, (x, y) in enumerate(single_loader):
                x = x.to(device, non_blocking=True)
                logits = model(x)
                probs  = softmax(logits).squeeze(0)
                topk = torch.topk(probs, k=min(3, probs.numel()))
                top_idx = topk.indices.tolist()
                top_prob = topk.values.tolist()

                img_path, true_idx = ds.samples[i]
                true_name = ds.classes[true_idx]

                pred_idx = top_idx[0]
                pred_ok = (pred_idx == true_idx)
                correct += int(pred_ok)
                total   += 1
                per_cls_tot[true_name] += 1
                if pred_ok:
                    per_cls_ok[true_name] += 1

                idx2name = ds.classes
                row = [
                    img_path.replace(",", " "),
                    true_name,
                    idx2name[top_idx[0]], f"{top_prob[0]:.6f}",
                ]
                row += ([idx2name[top_idx[1]], f"{top_prob[1]:.6f}"] if len(top_idx) > 1 else ["",""])
                row += ([idx2name[top_idx[2]], f"{top_prob[2]:.6f}"] if len(top_idx) > 2 else ["",""])
                f.write(",".join(row) + "\n")

    test_acc = correct / total if total else 0.0
    per_class_acc = {c: (per_cls_ok[c] / per_cls_tot[c] if per_cls_tot[c] else 0.0) for c in class_names}
    return {"test_acc": test_acc, "per_class_acc": per_class_acc, "num_test": total}

def main():
    train_ds, val_ds, test_ds, class_names = load_datasets()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_amp = (device.type == "cuda")
    pin = (device.type == "cuda")
    if device.type == "cuda":
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA not available - running on CPU.")

    train_loader = make_loader(train_ds, BATCH_TRAIN, True, pin)
    val_loader   = make_loader(val_ds,   BATCH_VAL,  False, pin)
    test_loader  = make_loader(test_ds,  BATCH_VAL,  False, pin) if test_ds is not None else None

    model = build_model(len(class_names)).to(device, non_blocking=True)
    criterion = nn.CrossEntropyLoss()
    opt = optim.Adam(model.parameters(), lr=LR)
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    # Save labels
    (OUT / "labels.txt").write_text("\n".join(class_names), encoding="utf-8")
    (OUT / "labels.json").write_text(json.dumps(class_names, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "classes.txt").write_text("\n".join(class_names), encoding="utf-8")

    best_acc  = 0.0
    best_path = OUT / "best_model.pt"
    train_log_path = OUT / "training_log.csv"
    with train_log_path.open("w", encoding="utf-8") as f:
        f.write("epoch,train_loss,val_acc,epoch_seconds\n")

    history = []
    for ep in range(1, EPOCHS + 1):
        t0 = time.time()
        model.train()
        running = 0.0
        for x, y in train_loader:
            x = x.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)

            opt.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=use_amp):
                logits = model(x)
                loss = criterion(logits, y)

            running += loss.item() * x.size(0)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()

        val_acc = eval_acc(model, val_loader, device, amp_enabled=use_amp) if val_loader is not None else 0.0
        train_loss = running / len(train_loader.dataset)
        dt = time.time() - t0
        print(f"epoch {ep:02d}: loss {train_loss:.4f}  val acc {val_acc:.3f}  ({dt:.1f}s)")

        with train_log_path.open("a", encoding="utf-8") as f:
            f.write(f"{ep},{train_loss:.6f},{val_acc:.6f},{dt:.3f}\n")
        history.append({"epoch": ep, "train_loss": train_loss, "val_acc": val_acc, "seconds": dt})

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({"model": model.state_dict(), "classes": class_names}, best_path)

    print(f"best val acc: {best_acc:.3f}")

    ckpt = torch.load(best_path, map_location=device)
    model.load_state_dict(ckpt["model"])
    model.eval()

    # Test on testimmages
    test_summary: Dict = {}
    if test_loader is not None:
        print("Evaluating on test set...")
        test_summary = eval_test_and_dump(model, test_loader, device, class_names, OUT)
        print(f"test acc: {test_summary['test_acc']:.3f} (n={test_summary['num_test']})")
    else:
        print("No test set found - skipping test evaluation.")

    dummy = torch.randn(1, 3, IMG_SIZE, IMG_SIZE, device=device)
    onnx_path = OUT / "fish_classifier.onnx"
    with torch.inference_mode(), torch.cuda.amp.autocast(enabled=use_amp):
        torch.onnx.export(
            model, dummy, str(onnx_path),
            input_names=["input"], output_names=["logits"],
            opset_version=18, do_constant_folding=True,
            dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
            training=torch.onnx.TrainingMode.EVAL
        )

    print("Exported ONNX to:", onnx_path)
    print("Saved labels to:", OUT / "labels.txt")

    metrics = {
        "epochs": EPOCHS,
        "best_val_acc": best_acc,
        "device": str(device),
        "cuda_device_name": torch.cuda.get_device_name(0) if device.type=="cuda" else None,
        "num_train": len(train_ds),
        "num_val": len(val_ds),
        "num_test": len(test_ds) if test_ds is not None else 0,
        "history": history,
        "test": test_summary,
        "labels": class_names,
        "artifacts": {
            "onnx": str(onnx_path),
            "labels_txt": str(OUT / "labels.txt"),
            "labels_json": str(OUT / "labels.json"),
            "best_model_pt": str(best_path),
            "training_log_csv": str(train_log_path),
            "test_predictions_csv": str(OUT / "test_predictions.csv") if test_loader is not None else None,
        }
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote summary metrics to:", OUT / "metrics.json")

if __name__ == "__main__":
    main()
