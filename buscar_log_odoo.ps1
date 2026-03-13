# Script para buscar el log de Odoo en Windows
# Ejecutar: .\buscar_log_odoo.ps1

Write-Host "=== Buscando Odoo y archivos de log ===" -ForegroundColor Cyan

# 1. Buscar odoo.conf
Write-Host "`n1. Buscando odoo.conf..." -ForegroundColor Yellow
$confFiles = Get-ChildItem -Path "C:\Users\$env:USERNAME" -Filter "odoo.conf" -Recurse -ErrorAction SilentlyContinue -Depth 5
if ($confFiles) {
    foreach ($f in $confFiles) {
        Write-Host "   Encontrado: $($f.FullName)" -ForegroundColor Green
        $logLine = Select-String -Path $f.FullName -Pattern "logfile|log_file" -ErrorAction SilentlyContinue
        if ($logLine) { Write-Host "   $logLine" }
    }
} else {
    Write-Host "   No se encontró odoo.conf en el perfil del usuario" -ForegroundColor Gray
}

# 2. Buscar archivos .log en carpetas Odoo
Write-Host "`n2. Buscando archivos .log en carpetas Odoo..." -ForegroundColor Yellow
$odooDirs = @("C:\Users\$env:USERNAME\Odoo 18 Sicore", "C:\odoo", "C:\Program Files\Odoo", "C:\Users\$env:USERNAME\odoo-argentina-ce")
foreach ($dir in $odooDirs) {
    if (Test-Path $dir) {
        $logs = Get-ChildItem -Path $dir -Filter "*.log" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 5
        if ($logs) {
            Write-Host "   En $dir :" -ForegroundColor Green
            $logs | ForEach-Object { Write-Host "     $($_.FullName)" }
        }
    }
}

# 3. AppData
Write-Host "`n3. Buscando en AppData\Local..." -ForegroundColor Yellow
$appData = "C:\Users\$env:USERNAME\AppData\Local"
if (Test-Path $appData) {
    $odooLogs = Get-ChildItem -Path $appData -Filter "*.log" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match "odoo|Odoo" } | Select-Object -First 5
    if ($odooLogs) {
        $odooLogs | ForEach-Object { Write-Host "   $($_.FullName)" -ForegroundColor Green }
    }
}

Write-Host "`n=== Para ver el error en vivo, ejecutá Odoo desde consola ===" -ForegroundColor Cyan
Write-Host "cd C:\ruta\a\tu\odoo" 
Write-Host "python odoo-bin -c odoo.conf"
Write-Host "`nLuego intentá instalar el módulo. El error aparecerá en la consola." -ForegroundColor Yellow
