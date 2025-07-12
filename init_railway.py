#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚂 Script de Inicialização para Railway
Cria todas as tabelas necessárias no PostgreSQL
"""
import sys
import os
import time

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def wait_for_database():
    """Aguarda o banco de dados estar disponível"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Importar a aplicação
            from app import app, db
            
            # Configurar contexto da aplicação
            with app.app_context():
                # Tentar conectar ao banco
                db.engine.execute('SELECT 1')
                print("✅ Banco de dados disponível!")
                return True
                
        except Exception as e:
            retry_count += 1
            print(f"⏳ Aguardando banco... tentativa {retry_count}/{max_retries}")
            print(f"   Erro: {e}")
            time.sleep(2)
    
    print("❌ Timeout: Banco de dados não disponível")
    return False

def init_railway_database():
    """Inicializa o banco de dados no Railway"""
    try:
        print("🚂 Iniciando configuração do banco Railway...")
        
        # Aguardar banco estar disponível
        if not wait_for_database():
            return False
        
        # Importar a aplicação
        from app import app, db
        
        # Configurar contexto da aplicação
        with app.app_context():
            print("📊 Conectando ao PostgreSQL...")
            
            # Criar todas as tabelas
            print("🔧 Criando tabelas...")
            db.create_all()
            
            # Verificar se existe usuário admin
            from app import User
            admin_user = User.query.filter_by(is_admin=True).first()
            
            if not admin_user:
                print("👤 Criando usuário administrador padrão...")
                
                # Criar admin padrão
                from app import hash_senha
                admin = User(
                    nome='admin',
                    senha_hash=hash_senha('admin123'),
                    is_admin=True
                )
                
                db.session.add(admin)
                db.session.commit()
                
                print("✅ Usuário admin criado!")
                print("📋 Login: admin")
                print("🔑 Senha: admin123")
            else:
                print("✅ Usuário administrador já existe")
            
            print("🎉 Banco de dados inicializado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_railway_database()
    sys.exit(0 if success else 1)
