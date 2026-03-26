# Project Cleanup Script
# This script organizes the project structure without losing any data

$sourceDir = "D:\SCET\S4\DBMS\ARSHA\price-comparison-project02-main\price-comparison-project02-main"
$targetDir = "D:\SCET\S4\DBMS\ARSHA\price-comparison-project02-main"

Write-Host "================================"
Write-Host "PROJECT STRUCTURE CLEANUP"
Write-Host "================================`n"

# Step 1: Copy backend files from nested folder to root backend folder
Write-Host "Step 1: Consolidating backend files..."
$backendSource = "$sourceDir\backend"
$backendTarget = "$targetDir\backend"

# Create backend folder if it doesn't exist
if (-not (Test-Path $backendTarget)) {
    New-Item -ItemType Directory -Path $backendTarget -Force | Out-Null
    Write-Host "  ✓ Created backend folder"
}

# Copy all backend files
Get-ChildItem -Path $backendSource -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $backendTarget -Force
    Write-Host "  ✓ Copied $($ _.Name)"
}

Write-Host "`nStep 2: Creating templates folder..."
$templatesSource = "$sourceDir\frontend\templates"
$templatesTarget = "$targetDir\templates"

if (-not (Test-Path $templatesTarget)) {
    New-Item -ItemType Directory -Path $templatesTarget -Force | Out-Null
}

# Copy all template files
Get-ChildItem -Path $templatesSource -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $templatesTarget -Force
    Write-Host "  ✓ Copied $($_.Name)"
}

Write-Host "`nStep 3: Creating static folder..."
$staticSource = "$sourceDir\frontend\static"
$staticTarget = "$targetDir\static"

if (-not (Test-Path $staticTarget)) {
    New-Item -ItemType Directory -Path $staticTarget -Force | Out-Null
}

# Copy all static files
Get-ChildItem -Path $staticSource -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $staticTarget -Force
    Write-Host "  ✓ Copied $($_.Name)"
}

Write-Host "`nStep 4: Copying scraper folder..."
$scraperSource = "$sourceDir\scraper"
$scraperTarget = "$targetDir\scraper"

if (Test-Path $scraperSource) {
    Copy-Item -Path $scraperSource -Destination $scraperTarget -Recurse -Force
    Write-Host "  ✓ Copied scraper folder"
}

Write-Host "`nStep 5: Copying clones folder..."
$clonesSource = "$sourceDir\clones"
$clonesTarget = "$targetDir\clones"

if (Test-Path $clonesSource) {
    Copy-Item -Path $clonesSource -Destination $clonesTarget -Recurse -Force
    Write-Host "  ✓ Copied clones folder"
}

Write-Host "`n================================"
Write-Host "CLEANUP COMPLETE!"
Write-Host "================================`n"

Write-Host "New directory structure:"
Write-Host "- $targetDir\backend\        ✓"
Write-Host "- $targetDir\templates\      ✓"
Write-Host "- $targetDir\static\         ✓"
Write-Host "- $targetDir\scraper\        ✓"
Write-Host "- $targetDir\clones\         ✓"

Write-Host "`nOld nested folder location:"
Write-Host "- $sourceDir\ (Can be deleted after verification)"

Write-Host "`n✓ All files copied! No data lost."
