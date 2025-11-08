#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/run.sh --config configs/default.yaml --seed 123
#
# Bu betik, epi_clock paketindeki alt-komutları sırasıyla çalıştırır:
# ingest -> features -> train -> evaluate -> make_figures

CONFIG=""
SEED="42"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG="$2"; shift 2;;
    --seed)
      SEED="$2"; shift 2;;
    *)
      echo "Unknown argument: $1"; exit 1;;
  esac
done

if [[ -z "${CONFIG}" ]]; then
  echo "ERROR: --config yolu gerekli (ör: --config configs/default.yaml)"
  exit 1
fi

export PYTHONUNBUFFERED=1

echo "[run.sh] Using config: ${CONFIG}, seed: ${SEED}"
python -m epi_clock ingest --config "${CONFIG}"
python -m epi_clock features --config "${CONFIG}"
python -m epi_clock train --config "${CONFIG}"
python -m epi_clock evaluate --config "${CONFIG}"
python -m epi_clock make_figures --config "${CONFIG}"

echo "[run.sh] Done."
