id: run-all-fixed
name: scripts/run_all.sh (temiz sürüm)
type: markdown
content: |-
  #!/usr/bin/env bash
  set -euo pipefail

  YELLOW="\033[1;33m"
  GREEN="\033[0;32m"
  NC="\033[0m"

  echo -e "${YELLOW}[epi-clock] Çalıştırma başladı...${NC}"

  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
  cd "$PROJECT_ROOT"

  # Config yolu: parametre verilmezse defaults
  CONFIG=${1:-configs/default.yaml}
  echo "[Epi-Clock] Using config: $CONFIG"

  # Sanal ortam (opsiyonel)
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv || true
  fi
  if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi

  python -m pip install --upgrade pip
  python -m pip install -e .

  mkdir -p data/raw data/interim data/processed results logs

  echo "[1/5] Ingest"
  python -m epi_clock ingest --config "$CONFIG"

  echo "[2/5] Feature engineering"
  python -m epi_clock features --config "$CONFIG"

  echo "[3/5] Train"
  python -m epi_clock train --config "$CONFIG" --seed 42

  echo "[4/5] Evaluate"
  python -m epi_clock evaluate --config "$CONFIG"

  echo "[5/5] Make figures"
  python -m epi_clock make_figures --config "$CONFIG"

  echo -e "${GREEN}[DONE]${NC} Results at: results/, logs/"
