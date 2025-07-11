#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir a senha do admin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from TMAeTMR.app import app, db, User, hash_senha

def corrigir_senha_admin():
    """Corrige a senha do admin para 'admin'"""
    with app.app_context():
        try:
            admin = User.query.filter_by(nome='admin').first()
            
            if admin:
                print(f"📝 Corrigindo senha do admin (ID: {admin.id})...")
                
                # Hash correto para a senha 'admin'
                nova_senha_hash = hash_senha('admin')
                print(f"   Novo hash: {nova_senha_hash}")
                
                # Atualizar no banco
                admin.senha_hash = nova_senha_hash
                admin.is_admin = True  # Garantir que is_admin está True
                
                db.session.commit()
                print("✅ Senha corrigida!")
                
                # Verificar se funcionou
                admin_verificado = User.query.filter_by(nome='admin').first()
                if admin_verificado.senha_hash == nova_senha_hash:
                    print("✅ Verificação: Senha salva corretamente!")
                    print(f"   is_admin: {admin_verificado.is_admin}")
                    return True
                else:
                    print("❌ Erro: Senha não foi salva corretamente!")
                    return False
                    
            else:
                print("❌ Admin não encontrado!")
                
                # Criar admin do zero
                print("📝 Criando admin do zero...")
                admin = User(
                    nome='admin',
                    senha_hash=hash_senha('admin'),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin criado!")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao corrigir senha: {e}")
            db.session.rollback()
            return False

def testar_login_corrigido():
    """Testa o login após a correção"""
    with app.app_context():
        try:
            admin = User.query.filter_by(nome='admin').first()
            
            if not admin:
                print("❌ Admin não encontrado!")
                return False
                
            # Testar login
            senha_teste = hash_senha('admin')
            
            print(f"🔍 Testando login após correção...")
            print(f"   Hash calculado: {senha_teste}")
            print(f"   Hash no banco: {admin.senha_hash}")
            print(f"   Iguais? {senha_teste == admin.senha_hash}")
            print(f"   is_admin: {admin.is_admin}")
            
            if admin.senha_hash == senha_teste:
                print("✅ LOGIN FUNCIONANDO!")
                return True
            else:
                print("❌ Login ainda não funciona!")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar login: {e}")
            return False

if __name__ == "__main__":
    print("🔧 CORREÇÃO DO ADMIN")
    print("=" * 50)
    
    print("1. Corrigindo senha do admin...")
    sucesso = corrigir_senha_admin()
    
    if sucesso:
        print("\n2. Testando login após correção...")
        login_ok = testar_login_corrigido()
        
        if login_ok:
            print("\n" + "=" * 50)
            print("✅ ADMIN CORRIGIDO COM SUCESSO!")
            print("🌐 Teste em: http://localhost:5000/login")
            print("👤 Usuário: admin")
            print("🔑 Senha: admin")
        else:
            print("\n❌ Ainda há problemas com o login!")
    else:
        print("\n❌ Falha ao corrigir o admin!")
