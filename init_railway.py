#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚂 Script de Inicialização para Railway
Cria todas as tabelas necessárias no PostgreSQL
"""
import sys
import os

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def init_railway_database():
    """Inicializa o banco de dados no Railway"""
    try:
        print("🚂 Iniciando configuração do banco Railway...")
        
        # Importar a aplicação
        from app import app, db
        
        # Configurar contexto da aplicação
        with app.app_context():
            print("📊 Conectando ao PostgreSQL...")
            
            # Criar todas as tabelas
            print("🔧 Criando tabelas...")
            db.create_all()
            
            # Verificar se existe usuário admin
            from app import Usuario
            admin_user = Usuario.query.filter_by(is_admin=True).first()
            
            if not admin_user:
                print("👤 Criando usuário administrador padrão...")
                
                # Criar admin padrão
                admin = Usuario(
                    nome='admin',
                    password_hash=Usuario.hash_password('admin123'),
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
