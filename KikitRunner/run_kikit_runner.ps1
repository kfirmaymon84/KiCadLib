Set-Location "C:\Dev\Scripts\KikitRunner"
try {
    python KikitRunner.py
}
catch {
    Write-Host "Error running KiKit Runner: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}