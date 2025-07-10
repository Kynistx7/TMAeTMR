#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico final das rotas do Flask
Testa se todas as rotas estão registradas e funcionando
"""

import requests
import time
import threading
from app import app

def test_route(url, description):
    """Testa uma rota específica"""
    try:
        response = requests.get(url, timeout=5)
        status = "✅ OK" if response.status_code == 200 else f"⚠️ {response.status_code}"
        print(f"{status} {url} - {description}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"❌ CONEXÃO FALHOU {url} - {description}")
        return False
    except Exception as e:
        print(f"❌ ERRO {url} - {description}: {str(e)}")
        return False

def run_server():
    """Executa o servidor Flask em thread separada"""
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def main():
    print("🔍 DIAGNÓSTICO FINAL DAS ROTAS")
    print("=" * 50)
    
    # Iniciar servidor em thread separada
    print("🚀 Iniciando servidor Flask...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Aguardar servidor inicializar
    time.sleep(3)
    
    # Testar rotas básicas
    print("\n📄 ROTAS DE PÁGINAS:")
    test_route("http://127.0.0.1:5000/", "Redirecionamento raiz")
    test_route("http://127.0.0.1:5000/login", "Página de login")
    test_route("http://127.0.0.1:5000/register", "Página de registro")
    test_route("http://127.0.0.1:5000/registro", "Página de registro alternativa")
    test_route("http://127.0.0.1:5000/tempos", "Página de tempos")
    test_route("http://127.0.0.1:5000/index", "Página index")
    test_route("http://127.0.0.1:5000/teste", "Página de teste")
    
    print("\n🧪 ROTAS DE TESTE POSTGRESQL:")
    test_route("http://127.0.0.1:5000/teste-postgresql", "Teste PostgreSQL com template")
    test_route("http://127.0.0.1:5000/teste-postgresql-simples", "Teste PostgreSQL simples")
    
    print("\n🔍 ROTAS DE DEBUG:")
    test_route("http://127.0.0.1:5000/debug/rotas", "Lista de todas as rotas")
    test_route("http://127.0.0.1:5000/debug/database", "Debug do banco de dados")
    test_route("http://127.0.0.1:5000/health", "Health check")
    test_route("http://127.0.0.1:5000/debug", "Debug info")
    
    print("\n🚀 ROTAS DA API:")
    # Teste apenas GET que não requer dados
    try:
        response = requests.get("http://127.0.0.1:5000/api/usuarios", timeout=5)
        print(f"✅ GET /api/usuarios - {response.status_code}")
    except Exception as e:
        print(f"❌ GET /api/usuarios - {str(e)}")
    
    print("\n📁 ROTAS DE ARQUIVOS ESTÁTICOS:")
    test_route("http://127.0.0.1:5000/css/styles.css", "CSS principal")
    test_route("http://127.0.0.1:5000/js/script.js", "JavaScript principal")
    
    # Listar todas as rotas registradas
    print("\n📋 TODAS AS ROTAS REGISTRADAS:")
    try:
        response = requests.get("http://127.0.0.1:5000/debug/rotas", timeout=5)
        if response.status_code == 200:
            print("✅ Rota /debug/rotas funcionando - veja no navegador para lista completa")
        else:
            print(f"⚠️ /debug/rotas retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar /debug/rotas: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNÓSTICO CONCLUÍDO")
    print("💡 Acesse http://127.0.0.1:5000/debug/rotas no navegador para ver lista completa")
    print("📱 Acesse http://127.0.0.1:5000/teste-postgresql para testar PostgreSQL")
    
    # Manter servidor rodando por um tempo
    try:
        print("\n⏰ Servidor ficará ativo por 30 segundos para testes manuais...")
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n🛑 Diagnóstico interrompido pelo usuário")

if __name__ == "__main__":
    main()
