$ErrorActionPreference = 'Stop'
$inputPdf = 'C:\Users\a.ghafarian\Downloads\SUBMIT_TO_PROFESSOR_MOATTAR\final_latex\english\cost_stable_ieee_en_compact.pdf'
$outputDocx = 'C:\Users\a.ghafarian\Downloads\SUBMIT_TO_PROFESSOR_MOATTAR\CostStableEHOA_English_BAIC2026_Compact.docx'
$word = $null
$doc = $null
try {
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0
  $doc = $word.Documents.Open($inputPdf, $false, $false)
  $doc.SaveAs2($outputDocx, 16)
  Write-Output ('DOCX=' + $outputDocx)
  Write-Output ('PAGES=' + $doc.ComputeStatistics(2))
} finally {
  if ($doc) { $doc.Close(0) }
  if ($word) { $word.Quit() }
}
