# Epi-Clock Prototype (Proof-of-Concept)

Bu depo, makaledeki yöntemin prototip/kanıt-özelliği (proof-of-concept) uygulamasını içerir. Prospektif/doğrulama çalışması kapsam dışıdır. Kod, metodolojik değerlendirme ve yeniden üretilebilirlik amacıyla paylaşılmıştır; klinik/operasyonel kullanım için değildir.

## Özellikler
- Minimal pipeline: veri yükleme → öznitelik çıkarımı → modelleme → değerlendirme → şekil/tablo üretimi
- Tek komutla yeniden üretim
- Sabit rasgele tohum ile tekrarlanabilir sonuçlar

## Hızlı Başlangıç
Önkoşullar: Python 3.10+, Git

```powershell
# Windows/PowerShell
git clone https://github.com/<kullanici>/<repo>.git
cd <repo>
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pip install -e .
```

```bash
# Linux/macOS
git clone https://github.com/<kullanici>/<repo>.git
cd <repo>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pip install -e .
```

## Çalıştırma
Tüm akışı tek komutla çalıştırmak için:
- Windows: scripts/run_all.ps1
- Linux/macOS: scripts/run_all.sh

Örnek:
```powershell
# PowerShell
./scripts/run_all.ps1
```

```bash
# Bash
bash scripts/run_all.sh
```

Çekirdek komutlar (manuel):
```powershell
python -m epi_clock ingest --config configs/default.yaml
python -m epi_clock features --config configs/default.yaml
python -m epi_clock train --config configs/default.yaml --seed 42
python -m epi_clock evaluate --config configs/default.yaml
python -m epi_clock make_figures --config configs/default.yaml
```

## Üretilen Çıktılar
- results/metrics.csv
- results/figures/*.png
- results/model.pkl (veya eşdeğeri)
- logs/run_YYYYMMDD_HHMMSS/

## Yapı
- src/epi_clock/: ana paket
- configs/: örnek konfigürasyonlar
- scripts/: yeniden üretim komut dosyaları
- tests/: smoke ve birim testleri
- data/ (izole, .gitignore altında)

## Kalite ve Test
```powershell
pre-commit run --all-files
pytest -q
```

## Lisans ve Sorumluluk Reddi
- Lisans: MIT (öneri, değiştirilebilir)
- Bu yazılım araştırma amaçlı bir prototiptir; klinik/operasyonel kullanım için uygunluğu doğrulanmamıştır.

## Sürüm
- v0.1.0 — Prototype (PoC)


