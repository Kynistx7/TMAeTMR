@echo off
echo Preparando arquivos para produção...

REM Cria diretório para arquivos minificados se não existir
if not exist "dist" mkdir dist

REM Comprime CSS
type css\admin.css css\admin-alert.css css\ranking-compact.css > dist\all.css
echo CSS combinado em dist\all.css

REM Comprime JS 
copy js\script.js dist\script.js
echo JS copiado para dist\script.js

echo.
echo ✅ Arquivos preparados para produção com sucesso!
echo Arquivos gerados:
echo - dist\all.css
echo - dist\script.js
echo.
echo Para usar estes arquivos em produção, atualize os links nos HTMLs
