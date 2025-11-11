# 🧬 EpiClock: Postmortem Interval Estimation

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

**EpiClock** - Biomoleküler degradasyon kinetiği kullanarak postmortem interval (PMI) tahmini için hesaplamalı framework.

---

## 🎯 Özellikler

- ✅ **Degradasyon Kinetik Modelleme**: Üstel, çift-üstel ve özel bozunma modelleri
- ✅ **Çoklu Belirteç Analizi**: DNA, RNA, protein gibi birden fazla biyobelirteç
- ✅ **Sıcaklık Kompanzasyonu**: Arrhenius tabanlı sıcaklık düzeltmesi
- ✅ **İstatistiksel Çıkarım**: Bayesian ve frekansçı güven aralıkları
- ✅ **Veri Görselleştirme**: Yayın kalitesinde grafikler
- ✅ **Toplu İşleme**: Birden fazla örneği aynı anda analiz

---

## 📦 Kurulum

\\\ash
# Repoyu klonla
git clone https://github.com/yourusername/epi-clock-prototype.git
cd epi-clock-prototype

# Virtual environment oluştur
python -m venv .venv
.venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt
pip install -e .
\\\

---

## 🚀 Hızlı Başlangıç

\\\python
import numpy as np
from epi_clock.models.degradation import DegradationModel

# Degradasyon modeli oluştur
model = DegradationModel(
    initial_concentration=100.0,
    rate_constant=0.05,
    temperature=20.0
)

# PMI tahmini
observed = 36.79
pmi = model.estimate_pmi(observed)
print(f"Tahmini PMI: {pmi:.2f} saat")
\\\

---

## 🧪 Test

\\\ash
pytest tests/ -v
pytest tests/ --cov=epi_clock --cov-report=html
\\\

---

## 🔬 Bilimsel Arka Plan

### Degradasyon Kinetiği
**C(t) = C₀ × e^(-kt)**

### Sıcaklık Bağımlılığı
**k(T) = A × e^(-Ea/RT)**

---

## 📚 Referanslar

1. **Sampaio-Silva et al. (2013)** - RNA degradation profiling
2. **Bauer et al. (2003)** - mRNA quantification as PMI indicator
3. **Young et al. (2013)** - Estimating PMI using RNA degradation

---

## 👨‍💻 Geliştirici

**Nurcan** - Adli Tıp Doktoru & Biyoinformatik Araştırmacısı

---

## 📄 Lisans

MIT License
