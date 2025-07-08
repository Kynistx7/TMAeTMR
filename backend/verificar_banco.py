#!/usr/bin/env python3
"""
Script para verificar o conteúdo do banco de dados SQLite
"""

import sqlite3
import os

def verificar_banco():
    db_path = "instance/dados.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    print("🗃️  Verificando banco de dados...")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        print(f"📋 Tabelas encontradas: {[t[0] for t in tabelas]}")
        
        # Verificar usuários
        cursor.execute("SELECT COUNT(*) FROM user;")
        total_users = cursor.fetchone()[0]
        print(f"👥 Total de usuários: {total_users}")
        
        if total_users > 0:
            cursor.execute("SELECT id, nome FROM user;")
            users = cursor.fetchall()
            for user in users:
                print(f"   - ID {user[0]}: {user[1]}")
        
        # Verificar registros
        cursor.execute("SELECT COUNT(*) FROM registro;")
        total_registros = cursor.fetchone()[0]
        print(f"📊 Total de registros: {total_registros}")
        
        if total_registros > 0:
            cursor.execute("""
                SELECT r.id, r.nome_operador, r.tma, r.tmr, r.user_id, u.nome 
                FROM registro r 
                LEFT JOIN user u ON r.user_id = u.id;
            """)
            registros = cursor.fetchall()
            print("\n📋 Registros detalhados:")
            for reg in registros:
                print(f"   - ID {reg[0]}: {reg[1]} | TMA: {reg[2]} | TMR: {reg[3]} | User: {reg[5]} (ID: {reg[4]})")
        
        conn.close()
        print("\n✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")

if __name__ == "__main__":
    verificar_banco()
