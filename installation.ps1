#!/usr/bin/env pwsh
<#
Cross-platform PowerShell installer to build Go binaries found in ./cmd and place them in ./bin
#>
param()
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Building Go binaries from .\cmd into .\bin"
New-Item -ItemType Directory -Path .\bin -Force | Out-Null

# Use .exe extension on Windows, none otherwise
$ext = if ($IsWindows) { '.exe' } else { '' }

Get-ChildItem -Directory -Path .\cmd | ForEach-Object {
  $name = $_.Name
  Write-Host "Building $name..."
  $out = Join-Path -Path $root -ChildPath ("bin\$name$ext")
  & go build -o $out (Join-Path -Path $root -ChildPath "cmd\$name")
}

Write-Host "Done. Binaries are in $root\bin"
