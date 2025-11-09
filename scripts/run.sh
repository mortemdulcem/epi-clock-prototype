#!/usr/bin/env bash
set -euo pipefail

# Enhanced run script with real data collection
CONFIG=""
SEED="42"
COLLECT_DATA="true"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG="$2"; shift 2;;
    --seed)
      SEED="$2"; shift 2;;
    --no-collect)
      COLLECT_DATA="false"; shift;;
    *)
      echo "Unknown argument: $1"; exit 1;;
  esac
done

if [[ -z "${CONFIG}" ]]; then
  echo "ERROR: --config required (e.g., --config configs/default.yaml)"
  exit 1
fi

export PYTHONUNBUFFERED=1
echo "[run.sh] Using config: ${CONFIG}, seed: ${SEED}"

# Data collection phase (can be skipped with --no-collect)
if [[ "${COLLECT_DATA}" == "true" ]]; then
  echo "[run.sh] === DATA COLLECTION PHASE ==="
  python -m epi_clock collect_pubmed --config "${CONFIG}"
  python -m epi_clock collect_geo --config "${CONFIG}"  
  python -m epi_clock meta_analyze --config "${CONFIG}"
fi

echo "[run.sh] === ANALYSIS PHASE ==="
python -m epi_clock ingest --config "${CONFIG}"
python -m epi_clock features --config "${CONFIG}"
python -m epi_clock train --config "${CONFIG}"
python -m epi_clock evaluate --config "${CONFIG}"
python -m epi_clock make_figures --config "${CONFIG}"

echo "[run.sh] === REPORTING PHASE ==="
python -m epi_clock generate_report --config "${CONFIG}"

echo "[run.sh] Done. Check results/ directory for outputs."
