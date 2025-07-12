#!/bin/bash
# 🚂 Script de inicialização para Railway

echo "🚂 Iniciando aplicação Railway..."
echo "🔍 Variáveis de ambiente:"
echo "   PORT: $PORT"
echo "   DATABASE_URL: ${DATABASE_URL:0:20}..."
echo "   RAILWAY_ENVIRONMENT: $RAILWAY_ENVIRONMENT"

# Aguardar um pouco mais para garantir que o PostgreSQL está pronto
echo "⏳ Aguardando serviços estarem prontos..."
sleep 10

# Executar inicialização do banco de dados
echo "🔧 Inicializando banco de dados..."
python init_railway.py

# Verificar se a inicialização foi bem-sucedida
if [ $? -eq 0 ]; then
    echo "✅ Inicialização concluída com sucesso!"
else
    echo "⚠️ Inicialização com problemas, mas continuando..."
fi

echo "🚀 Iniciando servidor Gunicorn..."
echo "🌐 Servidor rodará na porta: $PORT"

# Iniciar servidor com configurações otimizadas para Railway
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class gthread \
    --threads 4 \
    --timeout 120 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    app:app
