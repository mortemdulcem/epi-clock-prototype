#Requires -Version 7
param(
  [string]$ConfigPath = "configs/default.yaml",
  [int]$Seed = 42
)

$ErrorActionPreference = "Stop"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$env:RUN_ID = "run_$ts"

Write-Host "==> RUN_ID: $env:RUN_ID"

function Step($name, $script) {
  Write-Host "==> $name"
  & $script
  if ($LASTEXITCODE -ne 0) { throw "Step failed: $name" }
}

Step "Ingest"     { python -m epi_clock ingest --config $ConfigPath }
Step "Features"   { python -m epi_clock features --config $ConfigPath }
Step "Train"      { python -m epi_clock train --config $ConfigPath --seed $Seed }
Step "Evaluate"   { python -m epi_clock evaluate --config $ConfigPath }
Step "Figures"    { python -m epi_clock make_figures --config $ConfigPath }

Write-Host "==> Completed. Outputs under results/ and logs/"
