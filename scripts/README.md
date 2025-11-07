# epi-clock (prototype)

Epigenetik saat deneyleri için prototip Python projesi. Bu depo, veri işleme, modelleme ve raporlama adımlarını düzenli bir yapıda toplamayı amaçlar.

## Gereksinimler
- Python >= 3.10
- Git
- (Opsiyonel) Bash ortamı

## Kurulum ve Çalıştırma

1. Depoyu klonlayın:
```bash
git clone https://github.com/mortemdulcem/epi-clock-prototype.git
cd epi-clock-prototype
```

2. (Opsiyonel) Ortamı hazırlayın:
```bash
python -m venv .venv
source .venv/bin/activate    # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e .
```

3. Çalıştırma betiğini başlatın:
```bash
bash scripts/run_all.sh
```

Not: Betik, gerekliyse sanal ortamı oluşturur, pyproject.toml’daki bağımlılıkları yükler ve temel adımları sırasıyla çalıştırır.

## Proje Yapısı
```
epi-clock-prototype/
├─ scripts/
│  └─ run_all.sh           # Tüm adımları çalıştıran betik
├─ src/
│  └─ epi_clock/
│     ├─ io.py             # Veri içe aktarma
│     ├─ prep.py           # Temizleme / özellik mühendisliği
│     ├─ models.py         # Model eğitim / validasyon
│     └─ exp.py            # Deney kayıt / çıktı yönetimi
├─ data/
│  ├─ raw/                 # Ham veriler
│  └─ processed/           # İşlenmiş veriler
├─ outputs/
│  ├─ figures/             # Grafikler
│  ├─ logs/                # Günlük dosyaları
│  └─ models/              # Eğitimli modeller
├─ pyproject.toml          # Proje meta veriler ve bağımlılıklar
└─ README.md
```

## Geliştirme
- Kod biçimlendirme: `black` (satır uzunluğu 88)
- İçe aktarma düzeni: `isort` (black profili)

Aşağıdaki komutlar, sanal ortam aktifken çalıştırılabilir:
```bash
black .
isort .
```

## Yol Haritası
- Veri içe aktarma için `src/epi_clock/io.py`
- Temizleme/özellik mühendisliği için `src/epi_clock/prep.py`
- Model eğitim/validasyon için `src/epi_clock/models.py`
- Deney kayıt/çıkış yönetimi için `src/epi_clock/exp.py`

## Lisans
TBD
