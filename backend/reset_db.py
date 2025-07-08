#!/usr/bin/env python3
"""
Script para resetar o banco de dados SQLite
Execute este script quando tiver problemas com usuários duplicados
"""

import os
import sys

# Caminho para o banco de dados
db_path = "instance/dados.db"

def reset_database():
    """Remove o arquivo do banco de dados"""
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("✅ Banco de dados removido com sucesso!")
            print("🔄 Na próxima execução do Flask, um novo banco será criado.")
        except Exception as e:
            print(f"❌ Erro ao remover banco: {e}")
    else:
        print("ℹ️  Banco de dados não encontrado. Nada para remover.")

def main():
    print("🗃️  Reset do Banco de Dados - TMA/TMR")
    print("=" * 40)
    
    confirm = input("⚠️  Isso vai APAGAR TODOS os dados! Confirmar? (s/N): ")
    
    if confirm.lower() in ['s', 'sim', 'y', 'yes']:
        reset_database()
    else:
        print("❌ Operação cancelada.")

if __name__ == "__main__":
    main()
