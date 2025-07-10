# -*- coding: utf-8 -*-
"""
Script para iniciar o servidor com logs detalhados
"""

print("🚀 INICIANDO SERVIDOR COM DIAGNÓSTICO")
print("=" * 50)

# 1. Verificar se tudo está OK antes de iniciar
print("1. Verificando dependências...")

try:
    from flask import Flask
    print("✅ Flask")
    
    from flask_sqlalchemy import SQLAlchemy
    print("✅ SQLAlchemy")
    
    from flask_cors import CORS
    print("✅ CORS")
    
    import psycopg2
    print("✅ psycopg2")
    
    import os
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado")
    else:
        print("⚠️ Arquivo .env não encontrado")
    
except Exception as e:
    print(f"❌ Erro nas dependências: {e}")
    exit(1)

# 2. Testar conexão PostgreSQL antes de iniciar o Flask
print("\n2. Testando PostgreSQL...")

try:
    conn = psycopg2.connect(
        host='localhost',
        port='5432', 
        database='TMAeTMR',
        user='postgres',
        password='120990'
    )
    conn.close()
    print("✅ PostgreSQL conectado")
    
except Exception as e:
    print(f"❌ Erro PostgreSQL: {e}")
    print("⚠️ Continuando com SQLite como fallback...")

# 3. Iniciar aplicação
print("\n3. Iniciando aplicação Flask...")

try:
    # Importar e iniciar
    from app import app
    
    print("✅ App importado com sucesso")
    print("🌐 Servidor vai iniciar na porta 5000")
    print("🔗 Acesse: http://localhost:5000/teste-postgresql")
    print("=" * 50)
    
    # Iniciar servidor
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    
except Exception as e:
    print(f"❌ Erro ao iniciar: {e}")
    import traceback
    traceback.print_exc()
