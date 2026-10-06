# Source before every command: keeps caches and temp files off the full C: drive.
export PIP_CACHE_DIR=/d/pip-cache
export TMP=/d/tmp TEMP=/d/tmp TMPDIR=/d/tmp
export HF_HOME=/d/hf-cache
export TABPFN_MODEL_CACHE_DIR="/d/Hacktober 2026/bahaana/models"
case "$OSTYPE" in msys*|cygwin*) export PYTHONPATH="src;." ;; *) export PYTHONPATH="src:." ;; esac  # Windows Python splits on ";"
export PYTHONUTF8=1
