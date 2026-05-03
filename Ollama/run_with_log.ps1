param(
    [Parameter(Mandatory = $true)]
    [string]$BatchFile,

    [Parameter(Mandatory = $true)]
    [string]$LogFile
)

$ErrorActionPreference = "Stop"
$env:RUN_MAIN_LOGGING = "1"

$logDir = Split-Path -Parent $LogFile
if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# Stream command output to the console and the log file at the same time.
# Python is already launched with -u in run_main_debug.bat, so its lines appear live.
$cmdArgs = @("/d", "/c", "`"$BatchFile`" 2>&1")
& $env:ComSpec @cmdArgs | Tee-Object -LiteralPath $LogFile

exit $LASTEXITCODE
