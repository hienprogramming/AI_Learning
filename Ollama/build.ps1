# Build Pipeline for Embedded C Code
# PowerShell version for Windows

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Title)
    Write-Host "`n" -ForegroundColor White
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
}

function Main {
    Write-Header "EMBEDDED C BUILD PIPELINE"
    
    # Check Python
    try {
        $version = python --version 2>&1
        Write-Host "✓ Found: $version" -ForegroundColor Green
    } catch {
        Write-Host "✗ Python not found. Install Python 3.8+" -ForegroundColor Red
        exit 1
    }
    
    # Get script arguments
    $args_str = $args -join " "
    
    # Run build
    Write-Host "`nStarting build pipeline...`n" -ForegroundColor Cyan
    
    if ($args_str) {
        & python build.py @args
    } else {
        & python build.py
    }
    
    $exitCode = $LASTEXITCODE
    
    Write-Host "`n"
    if ($exitCode -eq 0) {
        Write-Header "✅ BUILD COMPLETED SUCCESSFULLY"
    } else {
        Write-Header "❌ BUILD FAILED"
    }
    
    exit $exitCode
}

# Run main
Main @args
