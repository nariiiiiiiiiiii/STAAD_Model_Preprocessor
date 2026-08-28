$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$TmpRoot = Join-Path $ProjectRoot ".tmp"
$CacheRoot = Join-Path $ProjectRoot ".cache"
$LogRoot = Join-Path $ProjectRoot ".logs"

$RuntimeDirs = @(
    $TmpRoot,
    (Join-Path $TmpRoot "temp"),
    $CacheRoot,
    (Join-Path $CacheRoot "pycache"),
    $LogRoot,
    (Join-Path $ProjectRoot "artifacts"),
    (Join-Path $ProjectRoot "build"),
    (Join-Path $ProjectRoot "dist"),
    (Join-Path $ProjectRoot "vendor")
)

foreach ($Dir in $RuntimeDirs) {
    New-Item -ItemType Directory -Force -Path $Dir | Out-Null
}

$env:TEMP = Join-Path $TmpRoot "temp"
$env:TMP = Join-Path $TmpRoot "temp"
$env:PYTHONPYCACHEPREFIX = Join-Path $CacheRoot "pycache"
$env:STAADPREP_PROJECT_ROOT = $ProjectRoot
$env:STAADPREP_CACHE_DIR = $CacheRoot
$env:STAADPREP_LOG_DIR = $LogRoot
$env:PYTHONPATH = Join-Path $ProjectRoot "src"
$env:PYTHONUTF8 = "1"

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Python = if (Test-Path $VenvPython) { $VenvPython } else { "python" }

Push-Location $ProjectRoot
try {
    & $Python -m staadprep.app @args
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
