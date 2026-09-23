$ErrorActionPreference='Stop'
$project=Split-Path $PSScriptRoot -Parent
$record=Join-Path $project 'artifacts\local-processes.json'
if (-not (Test-Path $record)) { Write-Host 'No managed Samjha processes recorded.'; exit }
foreach ($item in (Get-Content $record -Raw | ConvertFrom-Json)) {
 $process=Get-Process -Id $item.id -ErrorAction SilentlyContinue
 if ($process -and $process.StartTime.ToUniversalTime().ToString('o') -eq $item.created) {
   $command=(Get-CimInstance Win32_Process -Filter ("ProcessId="+$item.id)).CommandLine
   if ($command -and $command.Contains($project)) { Stop-Process -Id $item.id }
 }
}
Remove-Item -LiteralPath $record
Write-Host 'Managed Samjha servers stopped. Ollama is managed separately.'
