id: model-card
name: Model Card (Epi-Clock)
type: markdown
content: |-
  # Model Card — Epi-Clock Prototype

  Overview
  - Purpose: Epigenetik saat hızlanması ve clock drift tabanlı nüks tahmini (araştırma/prototip).
  - Scope: Sentetik ve/veya kamu verileriyle metodolojik değerlendirme. Klinik kullanım için değildir.

  Data
  - Sources: Kamu GEO/GDC, sentetik örneklem.
  - Sensitive attributes: Yaş, cinsiyet vb.; adli bağlamda dikkat.
  - Limitations: Heterojenite, batch etkileri, sınırlı temsil.

  Modeling
  - Features: AgeAccel (Horvath/Hannum/PhenoAge/GrimAge), clock-drift, lökosit kompozisyonu ve temel kovaryatlar.
  - Algorithms: Logistic (Elastic Net), nested CV, isotonic kalibrasyon.

  Evaluation
  - Primary metrics: AUC, Brier, kalibrasyon eğimi/kesişim.
  - Subgroups: Cinsiyet, yaş, bağımlılık alt tipi.

  Risks & Mitigations
  - Veri yanlılığı ve batch etkileri → ComBat/normalizasyon, alt grup raporları.
  - Fazla uyum (overfitting) → nested CV, dış doğrulama çağrısı.

  Intended Use
  - Akademik değerlendirme, yöntem karşılaştırma, reprodüksiyon.
  - Klinik/adli karar desteği için kullanılmamalıdır.

  Ethical Considerations
  - Adli/klinikte yanlış pozitif/negatifin sonuçları ciddidir; yalnızca araştırma amaçlı.
