$ErrorActionPreference = 'Stop'
$inputDoc = 'C:\Users\a.ghafarian\Downloads\SUBMIT_TO_PROFESSOR_MOATTAR\.docx_work\paper_final.docx'
$outputPdf = 'C:\Users\a.ghafarian\Downloads\SUBMIT_TO_PROFESSOR_MOATTAR\.docx_work\final_render\paper.pdf'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPdf) | Out-Null
$word = $null
$doc = $null
try {
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0
  $doc = $word.Documents.Open($inputDoc, $false, $true)
  $doc.ExportAsFixedFormat($outputPdf, 17)
  Write-Output ('WORD_VERSION=' + $word.Version)
  Write-Output ('PAGES=' + $doc.ComputeStatistics(2))
} finally {
  if ($doc) { $doc.Close(0) }
  if ($word) { $word.Quit() }
}
