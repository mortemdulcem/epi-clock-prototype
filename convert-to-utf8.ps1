Set-Content -Path ".\convert-tree-to-utf8.ps1" -Value @'
param(
  [string]$Root = ".",
  [string[]]$Include = @("*.py","*.md","*.yml","*.yaml"),
  [string[]]$ExcludeDir = @(".git",".venv","venv","env","__pycache__","*.egg-info",".mypy_cache",".pytest_cache")
)
Get-ChildItem -LiteralPath $Root -Recurse -File -Include $Include |
  Where-Object {
    $full = $_.FullName
    -not ($ExcludeDir | ForEach-Object { $pattern = $_; $full -like "*\$pattern*" } | Where-Object { $_ }) -and
    ($_.Extension -ne ".pyc")
  } |
  ForEach-Object {
    try {
      $p = $_.FullName
      $bak = "$p.bak"
      Copy-Item -LiteralPath $p -Destination $bak -Force
      $txt = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::GetEncoding(1254))
      [System.IO.File]::WriteAllText($p, $txt, (New-Object System.Text.UTF8Encoding($false)))
      Write-Host "OK  -> $p"
    } catch {
      Write-Warning "Atlandı: $($_.FullName) ($_ )"
    }
  }
'@
