"""Bahaana model server on Modal (free Starter credits). Deploy from the repo root: `modal deploy deploy/modal_app.py`.

Runs api/main.py unchanged. Render's free 512 MB / 0.1 CPU can't hold one TabPFN request (peaks ~490-540 MB on Linux).
"""
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parent.parent
APP = "/root/app"
SKIP = ["**/__pycache__", "**/*.pyc"]

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install_from_requirements(str(ROOT / "requirements.txt"), extra_index_url="https://download.pytorch.org/whl/cpu")
    .env({
        "PYTHONPATH": f"{APP}/src:{APP}",
        "TABPFN_MODEL_CACHE_DIR": f"{APP}/models",
        "OMP_NUM_THREADS": "2",
        "MKL_NUM_THREADS": "2",
        "FRONTEND_ORIGIN": "https://bahaana.onrender.com",
    })
    .add_local_file(ROOT / "scripts" / "fetch_model.py", f"{APP}/scripts/fetch_model.py", copy=True)
    .run_commands(f"python {APP}/scripts/fetch_model.py")
    .add_local_dir(ROOT / "shared", f"{APP}/shared", ignore=SKIP)
    .add_local_dir(ROOT / "src", f"{APP}/src", ignore=SKIP)
    .add_local_dir(ROOT / "api", f"{APP}/api", ignore=SKIP)
)

app = modal.App("bahaana-api")


# One small container at most, so a burst of visitors can't spend the free credits.
@app.function(image=image, cpu=2.0, memory=2048, timeout=300, scaledown_window=300, max_containers=1)
@modal.concurrent(max_inputs=8)
@modal.asgi_app()
def web():
    import sys

    sys.path[:0] = [f"{APP}/src", APP]
    from api.main import app as fastapi_app

    return fastapi_app
