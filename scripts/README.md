# epi-clock (prototype)

Epigenetik saat deneyleri için prototip Python projesi. Bu repo, veri işleme, modelleme ve raporlama adımlarını düzenli bir yapıda toplamayı amaçlar.

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
2. Çalıştırma betiğini başlatın:
   ```bash
   bash scripts/run_all.sh
   ```
   Betik, .venv sanal ortamını oluşturur, pyproject.toml bağımlılıklarını yükler ve temel adımları çalıştırır.

## Proje Yapısı
```
epi-clock-prototype/
├─ scripts/
│  └─ run_all.sh         # Tüm adımları çalıştıran betik
├─ data/
│  ├─ raw/               # Ham veriler
│  └─ processed/         # İşlenmiş veriler
├─ outputs/
│  ├─ figures/           # Grafikler
│  ├─ logs/              # Günlük dosyaları
│  └─ models/            # Eğitimli modeller
├─ pyproject.toml        # Proje meta ve bağımlılıklar
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
