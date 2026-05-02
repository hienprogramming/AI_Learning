param(
    [Parameter(Mandatory = $true)]
    [string]$BatchFile,

    [Parameter(Mandatory = $true)]
    [string]$LogFile
)

$env:RUN_MAIN_LOGGING = "1"

$psi = [System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName = $env:ComSpec
$psi.Arguments = "/d /c `"`"$BatchFile`" 2>&1`""
$psi.WorkingDirectory = Split-Path -Parent $BatchFile
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $false
$psi.CreateNoWindow = $true

$process = [System.Diagnostics.Process]::new()
$process.StartInfo = $psi

$logLines = [System.Collections.Generic.List[string]]::new()

$outputHandler = {
    if ($null -ne $EventArgs.Data) {
        Write-Host $EventArgs.Data
        $Event.MessageData.Add($EventArgs.Data)
    }
}

$outputEvent = Register-ObjectEvent -InputObject $process -EventName OutputDataReceived -Action $outputHandler -MessageData $logLines

[void]$process.Start()
$process.BeginOutputReadLine()
$process.WaitForExit()

Unregister-Event -SubscriptionId $outputEvent.Id

$logDir = Split-Path -Parent $LogFile
if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

$logLines | Set-Content -LiteralPath $LogFile -Encoding UTF8
exit $process.ExitCode
