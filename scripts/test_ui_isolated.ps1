param(
    [string]$Python = "",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RunnerArgs
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $Python) {
    if ($env:STAADPREP_TEST_PYTHON) {
        $Python = $env:STAADPREP_TEST_PYTHON
    }
    elseif ($env:VIRTUAL_ENV -and (Test-Path (Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"))) {
        $Python = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
    }
    elseif (Test-Path (Join-Path $ProjectRoot ".venv\Scripts\python.exe")) {
        $Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    }
    else {
        $Python = "python"
    }
}

Push-Location $ProjectRoot
try {
    & $Python (Join-Path $PSScriptRoot "test_ui_isolated.py") --project-root $ProjectRoot @RunnerArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
