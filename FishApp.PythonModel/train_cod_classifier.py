from pathlib import Path
import torch
from torchvision import transforms, datasets, models
import torch.nn as nn
import torch.optim as optim

ROOT      = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "data"
train_dir = DATA_ROOT / "train"
val_dir   = DATA_ROOT / "val"

train_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.RandomResizedCrop(224, scale=(0.6,1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(0.1,0.1,0.1,0.05),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])
val_tf = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])

def main():
    train_ds = datasets.ImageFolder(str(train_dir), transform=train_tf)
    val_ds   = datasets.ImageFolder(str(val_dir),   transform=val_tf)
    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=16, shuffle=True,  num_workers=0)
    val_loader   = torch.utils.data.DataLoader(val_ds,   batch_size=32, shuffle=False, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(model.fc.in_features, 2)
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    opt = optim.Adam(model.parameters(), lr=1e-3)

    def eval_acc():
        model.eval()
        tot=0; ok=0
        with torch.no_grad():
            for x,y in val_loader:
                x,y = x.to(device), y.to(device)
                pred = model(x).argmax(1)
                ok += (pred==y).sum().item()
                tot += y.numel()
        return ok/tot if tot else 0.0

    best_acc = 0.0
    best_path = ROOT / "cod_classifier_resnet18.pt"
    for ep in range(8):
        model.train()
        for x,y in train_loader:
            x,y = x.to(device), y.to(device)
            logits = model(x)
            loss = criterion(logits, y)
            opt.zero_grad(); loss.backward(); opt.step()
        acc = eval_acc()
        print(f"epoch {ep+1}: val acc {acc:.3f}")
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), best_path)

    if best_path.exists():
        model.load_state_dict(torch.load(best_path, map_location=device))
    model.eval()
    model_cpu = model.to("cpu")
    dummy = torch.randn(1, 3, 224, 224, device="cpu")
    onnx_path = ROOT / "cod_classifier.onnx"

    with torch.inference_mode():
        torch.onnx.export(
            model_cpu, dummy, str(onnx_path),
            input_names=["input"], output_names=["logits"],
            opset_version=18,
            do_constant_folding=True,
            dynamic_axes={
                "input": {0: "batch"},
                "logits": {0: "batch"},
            },
            training=torch.onnx.TrainingMode.EVAL
        )

    idx_to_class = {v:k for k,v in train_ds.class_to_idx.items()}
    with open(ROOT/"classes.txt","w", encoding="utf-8") as f:
        for i in range(len(idx_to_class)):
            f.write(idx_to_class[i]+"\n")

    print("Exported ONNX to:", onnx_path)
    print("Classes:", idx_to_class)

if __name__ == "__main__":
    main()
