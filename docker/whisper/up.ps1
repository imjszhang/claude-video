# Start local Whisper (base, CPU) and wait until the API responds.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "[watch-whisper] building image (first run downloads base model ~145 MB)..."
docker compose up -d --build

$healthUrl = "http://127.0.0.1:9000/v1/models"
Write-Host "[watch-whisper] waiting for API at $healthUrl ..."
for ($i = 1; $i -le 60; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5
        if ($resp.StatusCode -eq 200) {
            Write-Host "[watch-whisper] ready."
            Write-Host ""
            Write-Host "Add to ~/.config/watch/.env:"
            Write-Host "  LOCAL_WHISPER_URL=http://127.0.0.1:9000/v1/audio/transcriptions"
            exit 0
        }
    } catch {
        Start-Sleep -Seconds 5
    }
}

Write-Host "[watch-whisper] timed out — check logs: docker compose logs -f"
exit 1
