# -*- coding: utf-8 -*-
"""
Teste super simples das funções básicas
"""

def testar_funcoes_basicas():
    print("🧪 Testando funções básicas...")
    
    # 1. Testar imports
    try:
        import hashlib
        print("✅ hashlib OK")
        
        from flask import Flask
        print("✅ Flask OK")
        
        from flask_sqlalchemy import SQLAlchemy
        print("✅ SQLAlchemy OK")
        
        import psycopg2
        print("✅ psycopg2 OK")
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False
    
    # 2. Testar função hash
    try:
        def hash_senha_teste(senha):
            return hashlib.sha256(str(senha).encode('utf-8')).hexdigest()
        
        resultado = hash_senha_teste("1234")
        print(f"✅ Hash da senha '1234': {resultado[:20]}...")
        
    except Exception as e:
        print(f"❌ Erro no hash: {e}")
        return False
    
    # 3. Testar criação do Flask
    try:
        app_teste = Flask(__name__)
        print("✅ Flask app criado")
        
    except Exception as e:
        print(f"❌ Erro ao criar Flask app: {e}")
        return False
    
    # 4. Testar configuração básica
    try:
        app_teste.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teste.db'
        app_teste.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        print("✅ Configuração básica OK")
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False
    
    print("🎉 Todas as funções básicas funcionando!")
    return True

def testar_conexao_simples():
    print("\n🔌 Testando conexão PostgreSQL simples...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='TMAeTMR',
            user='postgres',
            password='120990'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        resultado = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print("✅ Conexão PostgreSQL funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE DE FUNÇÕES BÁSICAS")
    print("=" * 40)
    
    if testar_funcoes_basicas():
        if testar_conexao_simples():
            print("\n✅ TUDO OK! O problema pode estar na aplicação específica.")
            print("Execute: python app.py")
            print("E observe os logs de inicialização detalhadamente.")
        else:
            print("\n❌ Problema na conexão PostgreSQL")
    else:
        print("\n❌ Problema nas funções básicas")
