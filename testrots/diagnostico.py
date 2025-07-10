# -*- coding: utf-8 -*-
"""
Diagnóstico simples de conexão PostgreSQL
Execute: python diagnostico.py
"""

print("🔍 Diagnóstico PostgreSQL")
print("=" * 40)

# 1. Testar imports
try:
    import psycopg2
    print("✅ psycopg2 disponível")
except ImportError:
    print("❌ psycopg2 não encontrado")
    print("   Execute: pip install psycopg2-binary")
    exit(1)

# 2. Carregar configurações
import os
dotenv_loaded = False
try:
    from dotenv import load_dotenv
    if os.path.exists('.env'):
        load_dotenv()
        dotenv_loaded = True
        print("✅ Arquivo .env carregado")
    else:
        print("⚠️ Arquivo .env não encontrado")
except ImportError:
    print("⚠️ python-dotenv não disponível")

# Debug: mostrar todas as variáveis de ambiente relacionadas
print(f"\n🔍 Debug - Variáveis de ambiente:")
for key in ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']:
    value = os.environ.get(key)
    if key == 'POSTGRES_PASSWORD' and value:
        print(f"   {key}=***")
    else:
        print(f"   {key}={value}")

# 3. Testar conexão
pg_config = {
    'host': os.environ.get('POSTGRES_HOST', 'localhost'),
    'port': os.environ.get('POSTGRES_PORT', '5432'),
    'database': os.environ.get('POSTGRES_DB', 'TMAeTMR'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', '')
}

print(f"\n📋 Configurações:")
print(f"   Host: {pg_config['host']}")
print(f"   Port: {pg_config['port']}")
print(f"   Database: {pg_config['database']}")
print(f"   User: {pg_config['user']}")
print(f"   Password: {'***' if pg_config['password'] else 'NÃO CONFIGURADA'}")

if not pg_config['password']:
    print("\n⚠️ Senha não carregada do .env, tentando ler diretamente...")
    
    # Tentar ler o arquivo .env diretamente
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('POSTGRES_PASSWORD='):
                    password = line.split('=', 1)[1].strip()
                    if password:
                        pg_config['password'] = password
                        print(f"✅ Senha encontrada no arquivo .env")
                        break
    
    if not pg_config['password']:
        print("\n❌ ERRO: Senha não configurada!")
        print("   Edite o arquivo .env e configure POSTGRES_PASSWORD")
        print("   Conteúdo atual do .env:")
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:10], 1):  # Mostrar primeiras 10 linhas
                    if 'PASSWORD' in line:
                        print(f"   {i}: {line.strip()}")
        exit(1)

print(f"\n🔌 Testando conexão...")

try:
    conn = psycopg2.connect(**pg_config)
    cursor = conn.cursor()
    
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ CONEXÃO SUCESSO!")
    print(f"   PostgreSQL: {version[:50]}...")
    
    cursor.close()
    conn.close()
    
    print(f"\n🎉 PostgreSQL está funcionando!")
    print(f"   Agora execute: python app.py")
    
except psycopg2.OperationalError as e:
    error_str = str(e)
    print(f"❌ ERRO DE CONEXÃO:")
    print(f"   {error_str}")
    
    if "could not connect to server" in error_str:
        print(f"\n💡 SOLUÇÕES:")
        print(f"   1. Abra o pgAdmin e teste a conexão")
        print(f"   2. Verifique se PostgreSQL está rodando")
        print(f"   3. Confirme a porta 5432")
    
    elif "authentication failed" in error_str:
        print(f"\n💡 SOLUÇÕES:")
        print(f"   1. Verifique a senha no arquivo .env")
        print(f"   2. Teste a mesma senha no pgAdmin")
        
    elif "database" in error_str and "does not exist" in error_str:
        print(f"\n💡 SOLUÇÕES:")
        print(f"   1. Crie o banco '{pg_config['database']}' no pgAdmin")
        print(f"   2. Ou mude POSTGRES_DB no .env para um banco existente")

except Exception as e:
    print(f"❌ ERRO INESPERADO: {e}")

print(f"\n" + "=" * 40)
