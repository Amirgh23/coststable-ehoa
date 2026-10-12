param([Parameter(Mandatory=$true)][string]$InputDoc,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPdf) | Out-Null
$word = $null
$doc = $null
try {
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0
  $doc = $word.Documents.Open($InputDoc, $false, $true)
  $doc.ExportAsFixedFormat($OutputPdf, 17)
  Write-Output ('PAGES=' + $doc.ComputeStatistics(2))
} finally {
  if ($doc) { $doc.Close(0) }
  if ($word) { $word.Quit() }
}
