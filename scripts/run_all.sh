#!/usr/bin/env bash
set -euo pipefail

YELLOW="\033[1;33m"
GREEN="\033[0;32m"
NC="\033[0m"

echo -e "${YELLOW}[epi-clock] Çalıştırma başladı...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Sanal ortam opsiyonel
if [ ! -d ".venv" ]; then
  python3 -m venv .venv || true
fi
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -e .
fi

mkdir -p data/raw data/processed outputs/{figures,logs,models} results

echo -e "${YELLOW}Adım 1: Veri oluşturma/okuma${NC}"
python - <<'PY'
import os
import numpy as np
import pandas as pd
from epi_clock.io import write_table

raw = "data/raw/example.csv"
if not os.path.exists(raw):
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        "age": rng.integers(22, 70, size=300),
        **{f"feat_{i}": rng.normal(size=300) for i in range(200)}
    })
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv(raw, index=False)
else:
    df = pd.read_csv(raw)

write_table(df, "data/processed/step1.parquet")
print("step1: data/processed/step1.parquet yazıldı")
PY

echo -e "${YELLOW}Adım 2: Temizleme/Dönüşüm${NC}"
python - <<'PY'
from epi_clock.io import read_table, write_table
from epi_clock.prep import drop_missing, zscore

df = read_table("data/processed/step1.parquet")
df = drop_missing(df, thresh=0.2)
df = zscore(df)
write_table(df, "data/processed/step2.parquet")
print("step2: data/processed/step2.parquet yazıldı")
PY

echo -e "${YELLOW}Adım 3: Epigenetik saat benzetimi ve EAA${NC}"
python - <<'PY'
import numpy as np
import pandas as pd
from epi_clock.io import read_table, write_table

df = read_table("data/processed/step2.parquet")
rng = np.random.default_rng(123)

# Basit 'clock': bazı özelliklerin ağırlıklı toplamı
feat_cols = [c for c in df.columns if c.startswith("feat_")]
idx = rng.choice(len(feat_cols), size=min(120, len(feat_cols)), replace=False)
sel = [feat_cols[i] for i in idx]
weights = rng.normal(0, 1, size=len(sel))

clock_score = (df[sel].to_numpy() @ weights) / max(1, len(sel))
# Normalizasyon ve yaşla kalibrasyon
clock_norm = (clock_score - clock_score.mean()) / (clock_score.std() + 1e-8)
clock_age = 45 + 12 * clock_norm  # sahte saat yaşı
eaa = clock_age - df["age"].to_numpy()

out = df.copy()
out["clock_age_like"] = clock_age
out["EAA_like"] = eaa

write_table(out, "data/processed/step3_eaa.parquet")
print("step3: EAA hesaplandı -> data/processed/step3_eaa.parquet")
PY

echo -e "${YELLOW}Adım 4: Modelleme ve metrikler${NC}"
python - <<'PY'
import json
from epi_clock.io import read_table
from epi_clock.models import train_elastic_clock, report_metrics

df = read_table("data/processed/step3_eaa.parquet")
# Yaşı tahmin etme (demo amaçlı)
tr = train_elastic_clock(df, target="age")
metrics = report_metrics(tr)
print("Metrics:", metrics)
with open("results/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
print("results/metrics.json kaydedildi")
PY

echo -e "${YELLOW}Adım 5: Figürler${NC}"
python - <<'PY'
import os
import matplotlib.pyplot as plt
import seaborn as sns
from epi_clock.io import read_table

os.makedirs("outputs/figures", exist_ok=True)
df = read_table("data/processed/step3_eaa.parquet")

# EAA dağılımı
plt.figure(figsize=(5,4))
sns.histplot(df["EAA_like"], bins=30, kde=True)
plt.title("EAA_like dağılımı")
plt.tight_layout()
plt.savefig("outputs/figures/eaa_hist.png", dpi=150)
plt.close()

# clock_age vs age
plt.figure(figsize=(5,4))
sns.regplot(x=df["age"], y=df["clock_age_like"], scatter_kws={"alpha":0.4})
plt.xlabel("Chronological age")
plt.ylabel("Clock-like age")
plt.title("Clock-like age vs Chronological age")
plt.tight_layout()
plt.savefig("outputs/figures/clock_vs_age.png", dpi=150)
plt.close()

print("Figürler kaydedildi -> outputs/figures/")
PY

echo -e "${YELLOW}Adım 6: Otomatik özet raporu (summary.md)${NC}"
python - <<'PY'
import json
from datetime import datetime

with open("results/metrics.json") as f:
    m = json.load(f)

lines = []
lines.append("# Prototip Koşum Özeti")
lines.append(f"- Tarih: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
lines.append("- Ortam: Python 3.10+, pip install -e .")
lines.append("- Adımlar: step1→step2→EAA→model→figür")
lines.append("## Metrikler")
lines.append(f"- R2: {m.get('r2')}")
lines.append(f"- MAE: {m.get('mae')}")
lines.append("## Dosyalar")
lines.append("- data/processed/step1.parquet")
lines.append("- data/processed/step2.parquet")
lines.append("- data/processed/step3_eaa.parquet")
lines.append("- outputs/figures/eaa_hist.png")
lines.append("- outputs/figures/clock_vs_age.png")
lines.append("## Not")
lines.append("- Bu bir prototip; gerçek metilasyon verisi ve literatür
