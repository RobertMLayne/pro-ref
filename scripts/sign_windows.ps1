<# Optional MSI signing. Certificate values remain environment data. #>
param(
    [string]$ArtifactPath = 'pro-ref.msi',
    [string]$SignToolPath = 'C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe'
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrEmpty($env:WINDOWS_CERT_PFX)) {
    Write-Host 'No signing certificate configured; retaining unsigned MSI.'
    exit 0
}
if (-not (Test-Path -LiteralPath $SignToolPath -PathType Leaf)) {
    throw 'The Windows signing tool is unavailable.'
}
if ([string]::IsNullOrEmpty($env:RUNNER_TEMP)) {
    throw 'RUNNER_TEMP is required for temporary certificate storage.'
}

$pfx = Join-Path $env:RUNNER_TEMP ('pro-ref-' + [guid]::NewGuid() + '.pfx')
$certificateCreated = $false
try {
    $bytes = [Convert]::FromBase64String($env:WINDOWS_CERT_PFX)
    # Exclusive creation prevents adopting or overwriting another file.
    $stream = [IO.File]::Open(
        $pfx, [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write, [IO.FileShare]::None
    )
    $certificateCreated = $true
    try {
        $stream.Write($bytes, 0, $bytes.Length)
    }
    finally {
        $stream.Dispose()
    }
    & $SignToolPath sign /f $pfx /p $env:WINDOWS_CERT_PWD `
        /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 $ArtifactPath
    if ($LASTEXITCODE -ne 0) {
        throw "The Windows signing tool failed with exit code $LASTEXITCODE."
    }
}
finally {
    if ($certificateCreated) {
        Remove-Item -LiteralPath $pfx -Force
    }
}
