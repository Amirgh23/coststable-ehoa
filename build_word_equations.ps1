$ErrorActionPreference='Stop'
$path='C:\Users\a.ghafarian\Downloads\SUBMIT_TO_PROFESSOR_MOATTAR\CostStableEHOA_English_BAIC2026_Native.docx'
$word=$null; $doc=$null
try {
  $word=New-Object -ComObject Word.Application
  $word.Visible=$false
  $word.DisplayAlerts=0
  $doc=$word.Documents.Open($path,$false,$false)
  $sum=[char]0x2211
  $leq=[char]0x2264
  $alpha=[char]0x03B1
  $epsilon=[char]0x03B5
  $repls=@{
    '[[EQ1]]'=($sum + '_(j=1)^D z_j c_j ' + $leq + ' B')
    '[[EQ2]]'=('u_j=max(0,Ibar_j-z_' + $alpha + ' s_j),   q_j=u_j/max(c_j,' + $epsilon + ')')
  }
  foreach($key in $repls.Keys){
    $rng=$doc.Content
    $find=$rng.Find
    $find.Text=$key
    if($find.Execute()){
      $rng.Text=$repls[$key]
      $doc.OMaths.Add($rng) | Out-Null
    }
  }
  $doc.Save()
} finally {
  if($doc){$doc.Close(0)}
  if($word){$word.Quit()}
}
