[CmdletBinding()]
param(
    [switch]$Install,
    [switch]$Configure,
    [ValidateSet('all','github','grafana','loki','servicenow')][string]$Service='all',
    [switch]$Check,
    [switch]$Live,
    [switch]$Test,
    [switch]$InstallLab,
    [switch]$StartLab,
    [switch]$SeedLab,
    [switch]$EnableHook,
    [switch]$Run,
    [ValidateRange(1,65535)][int]$Port=8765,
    [string]$Python,
    [switch]$Help
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest

function Invoke-CheckedPython {
    param([string[]]$PythonArguments)
    & $script:VenvPython @PythonArguments
    if ($LASTEXITCODE -ne 0) { throw 'The previous step failed. Resolve it before continuing; later steps were not run.' }
}

if ($Help -or -not ($Install -or $Configure -or $Check -or $Live -or $Test -or $InstallLab -or $StartLab -or $SeedLab -or $EnableHook -or $Run)) {
    Write-Host @'
TechOpsagent setup - Armando Gomez

  .\setup.ps1 -Install                    Create/reuse .venv and install pinned dependencies
  .\setup.ps1 -Configure -Service github  Privately create/edit one integration
  .\setup.ps1 -Check                      Offline prerequisites and configuration check
  .\setup.ps1 -Check -Live -Port 8765     Also check localhost services and stale app builds
  .\setup.ps1 -Test                       Run the complete offline test suite
  .\setup.ps1 -InstallLab                 Download verified Windows Grafana/Loki builds
  .\setup.ps1 -StartLab                   Start installed lab and wait for healthy services
  .\setup.ps1 -SeedLab                    Send 3 synthetic events only to local Loki
  .\setup.ps1 -EnableHook                 Enable repository pre-push privacy checks
  .\setup.ps1 -Run -Port 8765             Run the app in this terminal; Ctrl+C stops it

Combine flags in the order above, for example: -Install -Check -Test -EnableHook
Optional: -Python <installed-python.exe> selects Python 3.12+ for initial installation.
No action flags: show this guide only. No model downloads or cloud calls are made.
'@
    exit 0
}

Push-Location -LiteralPath $PSScriptRoot
try {
    if ($Live -and $Run) { throw 'Run keeps this terminal open. Use -Check -Live in a second terminal after startup.' }
    $script:VenvPython=Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    if ($Install -and -not (Test-Path -LiteralPath $VenvPython)) {
        $baseArguments=@()
        if ($Python) { $basePython=$Python }
        elseif (Get-Command python -ErrorAction SilentlyContinue) { $basePython=(Get-Command python).Source }
        elseif (Get-Command py -ErrorAction SilentlyContinue) { $basePython=(Get-Command py).Source; $baseArguments=@('-3') }
        else { throw 'Install Python 3.12 or newer, then rerun with -Python pointing to its executable.' }
        & $basePython @baseArguments -c 'import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)'
        if ($LASTEXITCODE -ne 0) { throw 'Python 3.12+ is required. Use -Python to select a supported interpreter.' }
        & $basePython @baseArguments -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed; no later steps ran.' }
    }
    if (-not (Test-Path -LiteralPath $VenvPython)) { throw 'No project .venv. Run .\setup.ps1 -Install first.' }
    Invoke-CheckedPython @('-c','import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)')
    if ($Install) {
        Invoke-CheckedPython @('-m','pip','install','-r','requirements.txt')
        Invoke-CheckedPython @('-m','pip','check')
    }
    if ($Configure) { Invoke-CheckedPython @('-m','techops.settings','--edit','--service',$Service) }
    if ($InstallLab) { Invoke-CheckedPython @('-m','tools.local_lab','--install') }
    if ($StartLab) { Invoke-CheckedPython @('-m','tools.local_lab','--start') }
    if ($SeedLab) { Invoke-CheckedPython @('-m','tools.seed_loki','--send-local') }
    if ($Check -or $Live) {
        $checkArguments=@('-m','techops.diagnostics','--port',"$Port")
        if ($Live) { $checkArguments+='--live' }
        Invoke-CheckedPython $checkArguments
    }
    if ($Test) { Invoke-CheckedPython @('-m','unittest','discover','-s','tests') }
    if ($EnableHook) {
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git is required to enable the publication hook.' }
        $existingHook=git config --get core.hooksPath
        if ($LASTEXITCODE -gt 1) { throw 'Could not read Git configuration.' }
        if ($existingHook -and $existingHook -ne '.githooks') { throw 'Another hooksPath is configured; merge hooks manually to preserve it.' }
        git config core.hooksPath .githooks
        if ($LASTEXITCODE -ne 0) { throw 'Could not enable the publication hook.' }
        Write-Host 'Pre-push privacy hook enabled.'
    }
    if ($Run) {
        Invoke-CheckedPython @('-m','techops.diagnostics')
        Invoke-CheckedPython @('-c','import socket,sys; s=socket.socket(); busy=s.connect_ex(("127.0.0.1",int(sys.argv[1])))==0; s.close(); print("Port is occupied. Stop the verified old preview or choose -Port; nothing was stopped." if busy else "Port available."); sys.exit(1 if busy else 0)',"$Port")
        Write-Host "Open http://127.0.0.1:$Port . Keep this terminal open; press Ctrl+C to stop."
        Invoke-CheckedPython @('-m','techops.server','--port',"$Port")
    }
} catch {
    Write-Host ('Setup stopped: '+$_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
