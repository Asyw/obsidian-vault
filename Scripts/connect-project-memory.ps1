param(
    [Parameter(Position = 0)]
    [string]$ProjectPath = (Get-Location).Path,

    [Parameter(Position = 1)]
    [string]$ProjectName
)

$ErrorActionPreference = "Stop"

$Vault = "C:\Users\NINGMEI\Documents\Obsidian"
$Pjm = Join-Path $Vault ".venv-projectmem\Scripts\pjm.exe"

if (-not (Test-Path -LiteralPath $Pjm)) {
    throw "projectmem CLI not found: $Pjm"
}

$ResolvedProject = (Resolve-Path -LiteralPath $ProjectPath).Path
if (-not $ProjectName) {
    $ProjectName = Split-Path -Leaf $ResolvedProject
}

$SafeName = ($ProjectName -replace '[\\/:*?"<>|]', '-')
$ProjectsDir = Join-Path $Vault "01-Projects"
$Note = Join-Path $ProjectsDir "$SafeName.md"
$Index = Join-Path $ProjectsDir "项目索引.md"

Write-Host "Initializing project memory in: $ResolvedProject"
Push-Location -LiteralPath $ResolvedProject
try {
    & $Pjm init
}
finally {
    Pop-Location
}

New-Item -ItemType Directory -Force -Path $ProjectsDir | Out-Null

if (-not (Test-Path -LiteralPath $Note)) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $content = @"
---
type: project
status: active
project_path: "$ResolvedProject"
memory: "$ResolvedProject\.projectmem"
tags:
  - project
  - ai-memory
---

# $ProjectName

## 项目路径

``$ResolvedProject``

## 记忆入口

- projectmem: ``$ResolvedProject\.projectmem``
- Obsidian 笔记: 本页

## 项目目标


## 关键决策


## 已知问题


## 工作记录

- $timestamp 已接入 Windows Obsidian AI 记忆库。
"@
    Set-Content -LiteralPath $Note -Value $content -Encoding UTF8
}

$indexLine = "| $ProjectName | ``$ResolvedProject`` | 已接入 projectmem | [[$SafeName]] |"
$indexText = if (Test-Path -LiteralPath $Index) { Get-Content -Raw -Encoding UTF8 -LiteralPath $Index } else { "" }
if ($indexText -notlike "*[[$SafeName]]*") {
    Add-Content -LiteralPath $Index -Value $indexLine -Encoding UTF8
}

Push-Location -LiteralPath $ResolvedProject
try {
    & $Pjm note "Connected this project to the Windows Obsidian AI memory vault at $Vault."
}
finally {
    Pop-Location
}

Write-Host "Done."
Write-Host "Project note: $Note"
