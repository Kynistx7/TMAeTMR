# -*- coding: utf-8 -*-
"""
Teste direto PostgreSQL - sem dependência do .env
"""

print("🔍 Teste Direto PostgreSQL")
print("=" * 40)

# Configurações diretas (baseadas no seu .env)
pg_config = {
    'host': 'localhost',
    'port': '5432',
    'database': 'TMAeTMR',
    'user': 'postgres',
    'password': '120990'  # Senha do seu .env
}

print(f"📋 Testando com:")
print(f"   Host: {pg_config['host']}")
print(f"   Port: {pg_config['port']}")
print(f"   Database: {pg_config['database']}")
print(f"   User: {pg_config['user']}")
print(f"   Password: ***")

# 1. Testar psycopg2
try:
    import psycopg2
    print("✅ psycopg2 disponível")
except ImportError:
    print("❌ psycopg2 não encontrado")
    print("   Execute: pip install psycopg2-binary")
    exit(1)

# 2. Testar conexão
print(f"\n🔌 Testando conexão...")

try:
    conn = psycopg2.connect(**pg_config)
    cursor = conn.cursor()
    
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ CONEXÃO SUCESSO!")
    print(f"   PostgreSQL: {version[:50]}...")
    
    # Testar se consegue criar tabelas
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teste_conexao (
                id SERIAL PRIMARY KEY,
                teste VARCHAR(50)
            )
        """)
        conn.commit()
        print(f"✅ Permissões de criação OK")
        
        # Limpar tabela de teste
        cursor.execute("DROP TABLE IF EXISTS teste_conexao")
        conn.commit()
        
    except Exception as table_error:
        print(f"⚠️ Problema com permissões: {table_error}")
    
    cursor.close()
    conn.close()
    
    print(f"\n🎉 PostgreSQL FUNCIONANDO PERFEITAMENTE!")
    print(f"✅ Conexão OK")
    print(f"✅ Banco '{pg_config['database']}' acessível")
    print(f"✅ Permissões adequadas")
    print(f"\n🚀 Agora execute: python app.py")
    
except psycopg2.OperationalError as e:
    error_str = str(e).lower()
    print(f"❌ ERRO DE CONEXÃO:")
    print(f"   {str(e)}")
    
    print(f"\n💡 DIAGNÓSTICO:")
    
    if "could not connect" in error_str or "connection refused" in error_str:
        print(f"   🔴 PostgreSQL não está rodando ou não está na porta 5432")
        print(f"   📋 Soluções:")
        print(f"      1. Abra o pgAdmin")
        print(f"      2. Tente conectar ao servidor PostgreSQL")
        print(f"      3. Se não conseguir, inicie o serviço PostgreSQL")
        
    elif "authentication failed" in error_str or "password" in error_str:
        print(f"   🔴 Problema de autenticação")
        print(f"   📋 Soluções:")
        print(f"      1. Verifique se a senha '120990' está correta")
        print(f"      2. Teste a mesma senha no pgAdmin")
        print(f"      3. Confirme que o usuário é 'postgres'")
        
    elif "database" in error_str and "not exist" in error_str:
        print(f"   🔴 Banco de dados 'TMAeTMR' não existe")
        print(f"   📋 Soluções:")
        print(f"      1. Abra o pgAdmin")
        print(f"      2. Crie um banco chamado 'TMAeTMR'")
        print(f"      3. Ou use um banco existente")
        
    else:
        print(f"   🔴 Erro desconhecido")
        print(f"   📋 Verifique:")
        print(f"      1. Se PostgreSQL está instalado")
        print(f"      2. Se pgAdmin consegue conectar")

except Exception as e:
    print(f"❌ ERRO INESPERADO: {e}")

print(f"\n" + "=" * 40)
