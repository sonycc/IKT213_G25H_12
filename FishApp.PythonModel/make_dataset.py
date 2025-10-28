import shutil, random
from pathlib import Path

random.seed(42)

RAW_COD = Path(r"C:\Users\arnda\ikt213g25h\IKT213_G25H_12\cod-dataset")
RAW_NOT = Path(r"C:\Users\arnda\ikt213g25h\IKT213_G25H_12\dataset-notfish")

ROOT = Path(__file__).resolve().parent
OUT  = ROOT / "data"

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".JPG", ".JPEG", ".PNG", ".BMP", ".WEBP"}

def collect(p):
    return [x for x in p.rglob("*") if x.is_file() and x.suffix in EXTS]

def copy_subset(files, dest):
    dest.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(files):
        shutil.copy2(f, dest / f"{i:06d}{f.suffix.lower()}")

def main(split=0.8):
    cod  = collect(RAW_COD)
    notf = collect(RAW_NOT)
    print(f"Found {len(cod)} cod, {len(notf)} not_cod")

    if OUT.exists():
        shutil.rmtree(OUT)

    random.shuffle(cod)
    random.shuffle(notf)
    c_train = int(len(cod)*split)
    n_train = int(len(notf)*split)

    # Create dir
    (OUT/"train"/"cod").mkdir(parents=True, exist_ok=True)
    (OUT/"train"/"not_cod").mkdir(parents=True, exist_ok=True)
    (OUT/"val"/"cod").mkdir(parents=True, exist_ok=True)
    (OUT/"val"/"not_cod").mkdir(parents=True, exist_ok=True)

    # Copy files
    copy_subset(cod[:c_train],        OUT/"train"/"cod")
    copy_subset(cod[c_train:],        OUT/"val"/"cod")
    copy_subset(notf[:n_train],       OUT/"train"/"not_cod")
    copy_subset(notf[n_train:],       OUT/"val"/"not_cod")

    print("Dataset built at:", OUT)

if __name__ == "__main__":
    main()
