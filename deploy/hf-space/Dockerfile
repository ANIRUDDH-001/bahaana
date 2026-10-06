# Bahaana model server for a Hugging Face Docker Space (free CPU: 2 vCPU, 16 GB).
FROM python:3.11.9-slim

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/home/user/app/src:/home/user/app \
    PIP_NO_CACHE_DIR=1 \
    TABPFN_MODEL_CACHE_DIR=/home/user/app/models \
    OMP_NUM_THREADS=2 \
    MKL_NUM_THREADS=2 \
    FRONTEND_ORIGIN=https://bahaana.onrender.com
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --user -r requirements.txt

COPY --chown=user scripts/fetch_model.py scripts/
RUN python scripts/fetch_model.py

COPY --chown=user shared/ shared/
COPY --chown=user src/ src/
COPY --chown=user api/ api/

EXPOSE 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860", "--no-access-log"]
