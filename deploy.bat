@echo off
REM Script para Windows - Preparar deploy

echo 🚀 Preparando sistema TMA/TMR para deploy...

REM Criar pastas
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\img" mkdir static\img

REM Copiar arquivos
copy css\*.* static\css\
copy js\*.* static\js\
copy img\*.* static\img\

REM Copiar app.py
copy backend\app.py .\

echo ✅ Arquivos organizados para deploy!
echo.
echo 📋 Próximos passos:
echo 1. Crie um repositório no GitHub
echo 2. Faça upload destes arquivos
echo 3. Conecte no Render.com ou Railway.app
echo 4. Configure comando: python app.py
echo.
echo 🌐 Seu sistema estará online em poucos minutos!

pause
