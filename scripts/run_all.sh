#!/usr/bin/env bash
set -euo pipefail

# colors
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo -e "${YELLOW}[epi-clock] Çalıştırma başladı...${NC}"

# Proje köküne geç
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Python sürümü kontrolü
PY_MIN="3.10"
PY_CURR="$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
python3 - <<'PY'
import sys
min_v = (3,10)
if sys.version_info < min_v:
    print("Python 3.10+ gerekli.", file=sys.stderr)
    sys.exit(1)
PY

# venv kurulumu
if [ ! -d ".venv" ]; then
  echo -e "${YELLOW}Sanal ortam oluşturuluyor (.venv)...${NC}"
  python3 -m venv .venv
fi

# Aktivasyon
# macOS/Linux
source .venv/bin/activate 2>/dev/null || true
# Windows Git Bash için
if [ -z "${VIRTUAL_ENV:-}" ] && [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
fi

echo -e "${YELLOW}Bağımlılıklar yükleniyor...${NC}"
python -m pip install --upgrade pip setuptools wheel
# pyproject.toml üzerinden yükle
pip install -e .

# Çıktılar için klasörler
mkdir -p data/raw data/processed outputs/logs outputs/figures outputs/models

# Örnek adımlar (ileride gerçek betiklerle değiştirilecek yer tutucular)
echo -e "${YELLOW}Adım 1: Veri içe aktarma${NC}"
python - <<'PY'
print("Veri içe aktarma adımı (placeholder)")
PY

echo -e "${YELLOW}Adım 2: Temizleme/Dönüşüm${NC}"
python - <<'PY'
print("Veri temizleme adımı (placeholder)")
PY

echo -e "${YELLOW}Adım 3: Modelleme/Eğitim${NC}"
python - <<'PY'
print("Modelleme adımı (placeholder)")
PY

echo -e "${GREEN}[epi-clock] Tüm adımlar başarıyla tamamlandı.${NC}"
