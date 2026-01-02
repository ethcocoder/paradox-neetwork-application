# Universal Encoder/Decoder Model Setup
#
# Run this script to generate the TFLite models needed for real-time data compression
#
# Requirements:
#   - Python 3.8+
#   - TensorFlow 2.x
#   - NumPy

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Universal TFLite Model Generator" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check if TensorFlow is installed
Write-Host "`nChecking dependencies..." -ForegroundColor Yellow
$tfCheck = python -c "import tensorflow; print(tensorflow.__version__)" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ TensorFlow not installed" -ForegroundColor Red
    Write-Host "`nInstalling TensorFlow..." -ForegroundColor Yellow
    pip install tensorflow numpy
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install TensorFlow" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ TensorFlow $tfCheck found" -ForegroundColor Green
}

# Run the model generation script
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Starting Model Generation..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

python "$PSScriptRoot\generate_tflite_models.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "  ✓ Models Generated Successfully!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    
    Write-Host "Generated models:" -ForegroundColor Cyan
    Get-ChildItem "$PSScriptRoot\..\assets\models\*.tflite" | ForEach-Object {
        $sizeMB = [math]::Round($_.Length / 1MB, 2)
        Write-Host "  - $($_.Name) ($sizeMB MB)" -ForegroundColor White
    }
    
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "  1. The models are now in assets/models/" -ForegroundColor White
    Write-Host "  2. Run 'pnpm dev' to start the app" -ForegroundColor White
    Write-Host "  3. Test encoding/decoding in your app!`n" -ForegroundColor White
} else {
    Write-Host "`n✗ Model generation failed!" -ForegroundColor Red
    Write-Host "Check the error messages above for details.`n" -ForegroundColor Yellow
    exit 1
}
