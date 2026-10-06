"""Download the TabPFN v2 classifier checkpoint and its license (ungated HF repo, no login)."""
from pathlib import Path

from huggingface_hub import hf_hub_download

REPO = "Prior-Labs/TabPFN-v2-clf"
CKPT = "tabpfn-v2-classifier.ckpt"
MODELS = Path(__file__).resolve().parent.parent / "models"


def main() -> None:
    MODELS.mkdir(exist_ok=True)
    for name in (CKPT, "LICENSE.txt"):
        path = hf_hub_download(REPO, name, local_dir=MODELS)
        print("ok", path)


if __name__ == "__main__":
    main()
