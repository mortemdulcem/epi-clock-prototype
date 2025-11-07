echo -e "${YELLOW}Adım 1: Veri içe aktarma${NC}"
python - <<'PY'
import pandas as pd
from epi_clock.io import read_table, write_table
import os
raw = "data/raw/example.csv"
if os.path.exists(raw):
    df = read_table(raw)
else:
    import numpy as np
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        "age": rng.integers(20, 80, size=300),
        **{f"feat_{i}": rng.normal(size=300) for i in range(50)}
    })
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv(raw, index=False)
write_table(df, "data/processed/step1.parquet")
print("step1: data/processed/step1.parquet yazıldı")
PY

echo -e "${YELLOW}Adım 2: Temizleme/Dönüşüm${NC}"
python - <<'PY'
from epi_clock.prep import drop_missing, zscore
from epi_clock.io import read_table, write_table
df = read_table("data/processed/step1.parquet")
df = drop_missing(df, thresh=0.2)
df = zscore(df)
write_table(df, "data/processed/step2.parquet")
print("step2: data/processed/step2.parquet yazıldı")
PY

echo -e "${YELLOW}Adım 3: Modelleme/Eğitim${NC}"
python - <<'PY'
from epi_clock.io import read_table
from epi_clock.models import train_elastic_clock, report_metrics
df = read_table("data/processed/step2.parquet")
tr = train_elastic_clock(df, target="age")
print("Metrics:", report_metrics(tr))
PY

