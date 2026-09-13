param(
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$SourceRoot = Join-Path $ProjectRoot "src"
$BuildRoot = Join-Path $ProjectRoot "build\windows\final"
$TempRoot = Join-Path $ProjectRoot ".tmp\nuitka"
$CacheRoot = Join-Path $ProjectRoot ".cache\nuitka"
$BrandingAsset = Join-Path $ProjectRoot "assets\branding\staad-model-preprocessor.png"
$IconPath = Join-Path $BuildRoot "staad-model-preprocessor.ico"
$IconBuilder = Join-Path $PSScriptRoot "build_windows_icon.py"

if (-not $IsWindows) {
    throw "T22 Windows package build requires Windows."
}

New-Item -ItemType Directory -Force -Path $BuildRoot, $TempRoot, $CacheRoot | Out-Null
$env:TEMP = $TempRoot
$env:TMP = $TempRoot
$env:PYTHONPYCACHEPREFIX = Join-Path $CacheRoot "pycache"
$env:NUITKA_CACHE_DIR = $CacheRoot
$env:PYTHONPATH = $SourceRoot

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

& $Python -c "import platform,sys; assert sys.maxsize > 2**32; assert platform.system() == 'Windows'; assert sys.version_info >= (3,12)"
if ($LASTEXITCODE -ne 0) {
    throw "Selected Python must be Windows x64 and Python >= 3.12."
}

& $Python -m nuitka --version
if ($LASTEXITCODE -ne 0) {
    throw "Nuitka is not available in the selected Python environment."
}

$Version = & $Python -c "import sys; sys.path.insert(0, r'$SourceRoot'); from staadprep.version import __version__; print(__version__)"
if ($LASTEXITCODE -ne 0 -or -not $Version) {
    throw "Unable to resolve canonical STAAD Prep version."
}
$Version = $Version.Trim()
$WindowsVersion = if (($Version.Split('.')).Count -eq 3) { "$Version.0" } else { $Version }

if (-not (Test-Path -LiteralPath $BrandingAsset -PathType Leaf)) {
    throw "Application branding image is missing: $BrandingAsset"
}

& $Python $IconBuilder --source $BrandingAsset --output $IconPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to generate the Windows application icon."
}

$NuitkaArgs = @(
    "-m", "nuitka",
    "--mode=standalone",
    "--enable-plugin=pyside6",
    "--assume-yes-for-downloads",
    "--windows-console-mode=disable",
    "--output-dir=$BuildRoot",
    "--output-filename=STAAD Model Preprocessor.exe",
    "--report=$BuildRoot\\nuitka-report.xml",
    "--report-diffable",
    "--product-name=STAAD Model Preprocessor",
    "--file-description=STAAD Model Preprocessor",
    "--file-version=$WindowsVersion",
    "--product-version=$WindowsVersion",
    "--windows-icon-from-ico=$IconPath",
    "--include-data-files=$BrandingAsset=branding/staad-model-preprocessor.png",
    "--include-package=staadprep",
    "--include-package-data=pyvista",
    (Join-Path $SourceRoot "staadprep\app.py")
)

Write-Host "Building STAAD Model Preprocessor $Version portable standalone..."
Write-Host "Python: $Python"
Write-Host "Output: $BuildRoot"

& $Python @NuitkaArgs
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$Executable = Get-ChildItem -Path $BuildRoot -Recurse -Filter "STAAD Model Preprocessor.exe" |
    Select-Object -First 1
if (-not $Executable) {
    throw "Nuitka completed without producing STAAD Model Preprocessor.exe."
}

Write-Host "Standalone executable: $($Executable.FullName)"
exit 0
