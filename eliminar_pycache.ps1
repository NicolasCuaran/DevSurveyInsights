# Directorio del proyecto (usa el directorio actual por defecto)
$projectDir = Get-Location

# Busca todos los directorios __pycache__ en el proyecto
$pycacheDirs = Get-ChildItem -Path $projectDir -Filter "__pycache__" -Directory -Recurse

# Filtra los directorios encontrados, excluyendo los que están en venv
$pycachesToRemove = $pycacheDirs | Where-Object { $_.FullName -notmatch "\\venv\\" }

# Contador para los directorios eliminados
$removedCount = 0

# Muestra los directorios que se van a eliminar y los elimina
Write-Host "Eliminando directorios __pycache__..." -ForegroundColor Yellow

foreach ($dir in $pycachesToRemove) {
    Write-Host "Eliminando: $($dir.FullName)" -ForegroundColor Cyan
    Remove-Item -Path $dir.FullName -Recurse -Force
    $removedCount++
}

# Muestra el resumen de la operación
Write-Host "`nResumen de la limpieza:" -ForegroundColor Green
Write-Host "- Total de directorios __pycache__ encontrados: $($pycacheDirs.Count)" -ForegroundColor White
Write-Host "- Directorios __pycache__ eliminados: $removedCount" -ForegroundColor White
Write-Host "- Directorios __pycache__ en venv (preservados): $($pycacheDirs.Count - $removedCount)" -ForegroundColor White

Write-Host "`nLimpieza completada." -ForegroundColor Green