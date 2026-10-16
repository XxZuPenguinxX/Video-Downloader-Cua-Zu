param(
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$pythonCommand = $null
$pythonArgs = @()
if ($PythonPath) {
    $pythonCommand = Get-Command $PythonPath -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Không tìm thấy Python tại: $PythonPath"
    }
} else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
}

$bits = ""
if ($pythonCommand) {
    $bits = & $pythonCommand.Source -c "import struct; print(struct.calcsize('P') * 8)"
}
if ($bits.Trim() -ne "32" -and -not $PythonPath) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        $pythonCommand = $launcher
        $pythonArgs = @("-3-32")
        $bits = & $pythonCommand.Source @pythonArgs -c "import struct; print(struct.calcsize('P') * 8)"
    }
}
if ($LASTEXITCODE -ne 0 -or $bits.Trim() -ne "32") {
    throw "Cần cài Python 3.10+ bản 32-bit hoặc truyền -PythonPath tới Python 32-bit."
}

$buildEnvironment = Join-Path $PSScriptRoot ".venv-build-win32"
& $pythonCommand.Source @pythonArgs -m venv $buildEnvironment
if ($LASTEXITCODE -ne 0) { throw "Không tạo được môi trường build." }
$buildPython = Join-Path $buildEnvironment "Scripts\python.exe"
& $buildPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Không cài được pip." }
& $buildPython -m pip install -e ".[build]"
if ($LASTEXITCODE -ne 0) { throw "Không cài được các gói build." }
& $buildPython -m PyInstaller --clean --noconfirm --onefile --windowed --name install linktai.py
if ($LASTEXITCODE -ne 0) { throw "Build Windows x86 thất bại." }

Write-Output "Đã tạo dist\install.exe"
