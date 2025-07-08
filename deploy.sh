#!/bin/bash
# Script para preparar deploy

echo "🚀 Preparando sistema TMA/TMR para deploy..."

# Mover arquivos para estrutura correta
echo "📁 Organizando arquivos..."

# Criar pasta static se não existir
mkdir -p static/css static/js static/img

# Copiar arquivos estáticos
cp css/* static/css/
cp js/* static/js/
cp img/* static/img/

# Mover app.py para raiz
cp backend/app.py ./

echo "✅ Arquivos organizados para deploy!"
echo ""
echo "📋 Próximos passos:"
echo "1. Crie um repositório no GitHub"
echo "2. Faça upload destes arquivos"
echo "3. Conecte no Render.com ou Railway.app"
echo "4. Configure comando: python app.py"
echo ""
echo "🌐 Seu sistema estará online em poucos minutos!"
