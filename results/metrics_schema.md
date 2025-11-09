id: metrics-schema
name: Metrics Schema
type: markdown
content: |-
  # metrics.csv Sözlüğü

  Zorunlu Kolonlar
  - run_id: Tarih-saat damgası veya UUID
  - fold: outer fold no (veya "overall")
  - metric: metrik adı (auc, pr_auc, brier, logloss, sens_at_90sp, cal_slope, cal_intercept)
  - value: sayısal değer (float)

  İsteğe Bağlı Kolonlar
  - subgroup: alt grup adı (sex=F, age_bin=35-50, addiction_type=opioid vb.)
  - n: örnek sayısı
  - ci_low, ci_high: bootstrap %95 GA
  - notes: serbest metin

  Örnek
  run_id,fold,metric,value,subgroup,n,ci_low,ci_high
  20251109T1350,overall,auc,0.742,,120,0.68,0.80
  20251109T1350,overall,brier,0.186,,120,,
  20251109T1350,fold=1,auc,0.731,,96,,
