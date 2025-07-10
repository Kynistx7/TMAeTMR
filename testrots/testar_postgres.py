# -*- coding: utf-8 -*-
"""
Script para testar a conexão e funcionamento do PostgreSQL
"""

import os
import sys

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ Arquivo .env carregado")
    else:
        print("⚠️ Arquivo .env não encontrado")
except ImportError:
    print("⚠️ python-dotenv não disponível")

# Testar importações
try:
    import psycopg2
    print("✅ psycopg2 instalado")
except ImportError:
    print("❌ psycopg2 não instalado - execute: pip install psycopg2-binary")
    sys.exit(1)

# Testar conexão direta com PostgreSQL
def testar_conexao_postgres():
    pg_config = {
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('POSTGRES_PORT', '5432'),
        'database': os.environ.get('POSTGRES_DB', 'tma_tmr_db'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', '')
    }
    
    print(f"🔄 Testando conexão com PostgreSQL...")
    print(f"   Host: {pg_config['host']}")
    print(f"   Porta: {pg_config['port']}")
    print(f"   Banco: {pg_config['database']}")
    print(f"   Usuário: {pg_config['user']}")
    
    try:
        conn = psycopg2.connect(**pg_config)
        cursor = conn.cursor()
        
        # Testar query simples
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Conexão bem-sucedida!")
        print(f"   Versão PostgreSQL: {version}")
        
        # Verificar se o banco existe e está acessível
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tabelas = cursor.fetchall()
        print(f"📊 Tabelas existentes: {len(tabelas)}")
        for tabela in tabelas:
            print(f"   - {tabela[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro de conexão PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

# Testar Flask App
def testar_flask_app():
    print(f"\n🔄 Testando Flask App...")
    
    try:
        from app import app, db, User, Registro
        
        with app.app_context():
            print("✅ App Flask carregado")
            print(f"   Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # Tentar criar as tabelas
            try:
                db.create_all()
                print("✅ Tabelas criadas/verificadas com sucesso")
                
                # Testar contagem de registros
                users_count = User.query.count()
                registros_count = Registro.query.count()
                
                print(f"📊 Dados atuais:")
                print(f"   Usuários: {users_count}")
                print(f"   Registros: {registros_count}")
                
                return True
                
            except Exception as db_error:
                print(f"❌ Erro ao criar/acessar tabelas: {db_error}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao carregar Flask App: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste de Configuração PostgreSQL")
    print("=" * 50)
    
    # Teste 1: Conexão direta
    conexao_ok = testar_conexao_postgres()
    
    # Teste 2: Flask App
    if conexao_ok:
        app_ok = testar_flask_app()
        
        if app_ok:
            print("\n🎉 Todos os testes passaram!")
            print("✅ PostgreSQL configurado corretamente")
            print("✅ Flask App funcionando")
            print("\n🚀 Você pode executar: python app.py")
        else:
            print("\n⚠️ PostgreSQL OK, mas Flask App com problemas")
    else:
        print("\n❌ Verifique a configuração do PostgreSQL")
        print("📋 Dicas:")
        print("   1. Certifique-se que o PostgreSQL está rodando")
        print("   2. Verifique as credenciais no arquivo .env")
        print("   3. Confirme que o banco 'tma_tmr_db' existe no pgAdmin")
