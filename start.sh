#!/bin/bash

# Script de inicialização para Railway
echo "🚀 Iniciando aplicação TMA/TMR..."

# Verificar se DATABASE_URL existe
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️ DATABASE_URL não configurada, usando SQLite como fallback"
else
    echo "✅ PostgreSQL detectado via DATABASE_URL"
fi

# Executar migrações se necessário
echo "📊 Inicializando banco de dados..."

# Iniciar aplicação
echo "🌐 Iniciando servidor web..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --preload app:app
