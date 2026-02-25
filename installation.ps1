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
# $IsWindows is only available in PowerShell 6+; fall back to $env:OS for Windows PowerShell 5.x
$onWindows = if ($null -ne $IsWindows) { $IsWindows } else { $env:OS -eq 'Windows_NT' }
$ext = if ($onWindows) { '.exe' } else { '' }

Get-ChildItem -Directory -Path .\cmd | ForEach-Object {
  $name = $_.Name
  Write-Host "Building $name..."
  $out = Join-Path -Path $root -ChildPath ("bin\$name$ext")
  & go build -o $out (Join-Path -Path $root -ChildPath "cmd\$name")
}

# Ensure Windows PE executables have .exe suffix even if built in a non-Windows environment
if ($onWindows) {
  Get-ChildItem -Path .\bin -File | Where-Object { $_.Extension -eq '' } | ForEach-Object {
    $bytes = Get-Content -Path $_.FullName -Encoding Byte -TotalCount 2 -ErrorAction SilentlyContinue
    if ($bytes.Count -ge 2 -and $bytes[0] -eq 0x4D -and $bytes[1] -eq 0x5A) {
      Rename-Item -Path $_.FullName -NewName ($_.Name + '.exe')
      Write-Host "Renamed $($_.Name) -> $($_.Name).exe"
    }
  }
}

Write-Host "Done. Binaries are in $root\bin"

# Add bin to the current user's PATH if not already present
$binPath = Join-Path $root 'bin'
$userPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
if ($userPath -split ';' -notcontains $binPath) {
  [Environment]::SetEnvironmentVariable('PATH', "$userPath;$binPath", 'User')
  Write-Host "Added $binPath to your user PATH. Restart your shell to pick it up."
} else {
  Write-Host "$binPath is already in your user PATH."
}
# Also update the current session's PATH immediately
if ($env:PATH -split ';' -notcontains $binPath) {
  $env:PATH = "$env:PATH;$binPath"
}
