$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot -Parent
Set-Location $project
foreach ($port in @(8000,5173)) {
 if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) { throw "Port $port is already in use. Stop the previous server first." }
}
$python = Join-Path $project '.venv\Scripts\python.exe'
$vite = Join-Path $project 'frontend\samjha-frontend\node_modules\vite\bin\vite.js'
if (-not (Test-Path $python)) { throw 'Install the backend environment using README.md first.' }
if (-not (Test-Path $vite)) { throw 'Run npm ci in frontend\samjha-frontend first.' }
New-Item -ItemType Directory -Force artifacts | Out-Null
$backend = Start-Process $python -ArgumentList @('-m','uvicorn','main:app','--app-dir',('"' + (Join-Path $project 'backend') + '"'),'--host','127.0.0.1','--port','8000') -WorkingDirectory $project -WindowStyle Hidden -PassThru -RedirectStandardOutput artifacts\backend.log -RedirectStandardError artifacts\backend-error.log
try {
 $frontend = Start-Process (Get-Command node).Source -ArgumentList @(('"' + $vite + '"'),'--host','127.0.0.1') -WorkingDirectory (Join-Path $project 'frontend\samjha-frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $project 'artifacts\frontend.log') -RedirectStandardError (Join-Path $project 'artifacts\frontend-error.log')
 @(@{id=$backend.Id;created=$backend.StartTime.ToUniversalTime().ToString('o')},@{id=$frontend.Id;created=$frontend.StartTime.ToUniversalTime().ToString('o')}) | ConvertTo-Json | Set-Content artifacts\local-processes.json
 Write-Host 'Open http://127.0.0.1:5173 . Keep Ollama running. Stop with scripts\stop.ps1 . Logs are under artifacts.'
} catch { Stop-Process -Id $backend.Id; throw }
