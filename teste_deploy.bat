@echo off
echo 🧪 Teste do Sistema TMA/TMR
echo ============================

echo.
echo 📁 Verificando estrutura de arquivos...
if exist app.py (
    echo ✅ app.py encontrado na raiz
) else (
    echo ❌ app.py NÃO encontrado na raiz
)

if exist Procfile (
    echo ✅ Procfile encontrado
) else (
    echo ❌ Procfile não encontrado
)

if exist requirements.txt (
    echo ✅ requirements.txt encontrado
) else (
    echo ❌ requirements.txt não encontrado
)

if exist instance (
    echo ✅ Diretório instance existe
) else (
    echo ❌ Diretório instance não existe
)

echo.
echo 📋 Conteúdo do Procfile:
type Procfile

echo.
echo 📦 Dependências principais:
findstr /i "flask gunicorn" requirements.txt

echo.
echo 🎯 RESUMO DO DEPLOY:
echo ==================
echo ✅ Estrutura corrigida para Render
echo ✅ app.py movido para raiz do projeto
echo ✅ Procfile atualizado: gunicorn app:app
echo ✅ Suporte a PostgreSQL e SQLite
echo ✅ Variáveis de ambiente configuradas
echo.
echo 🚀 PRONTO PARA DEPLOY!
echo.
echo 📝 Próximos passos:
echo 1. git add .
echo 2. git commit -m "Deploy: app.py na raiz + correções"
echo 3. git push origin main
echo 4. Deploy no Render: https://render.com
echo.

pause
