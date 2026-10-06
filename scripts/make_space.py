"""Assemble the Hugging Face Docker Space for the API: `python scripts/make_space.py <space clone dir>`.

Everything in the target except its .git folder is replaced, so the Space always matches this repo.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ["requirements.txt", "scripts/fetch_model.py", "shared/holidays_2026.json"]
TREES = ["api", "src"]
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc")


def make_space(out: Path) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.iterdir():
        if old.name != ".git":
            shutil.rmtree(old) if old.is_dir() else old.unlink()
    for name in ("Dockerfile", "README.md"):
        shutil.copy2(ROOT / "deploy" / "hf-space" / name, out / name)
    for rel in FILES:
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, out / rel)
    for rel in TREES:
        shutil.copytree(ROOT / rel, out / rel, ignore=SKIP)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/make_space.py <space clone dir>")
    print("Space files written to", make_space(Path(sys.argv[1])))
