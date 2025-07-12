#!/bin/bash
# 🚂 Script de inicialização para Railway

echo "🚂 Iniciando aplicação Railway..."

# Aguardar um pouco para garantir que o PostgreSQL está pronto
echo "⏳ Aguardando serviços..."
sleep 5

# Executar inicialização do banco de dados
echo "🔧 Inicializando banco de dados..."
python init_railway.py

# Verificar se a inicialização foi bem-sucedida
if [ $? -eq 0 ]; then
    echo "✅ Inicialização concluída com sucesso!"
    echo "🚀 Iniciando servidor..."
    exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
else
    echo "❌ Erro na inicialização. Tentando iniciar apenas o servidor..."
    echo "⚠️ As tabelas podem precisar ser criadas manualmente."
    exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
fi
