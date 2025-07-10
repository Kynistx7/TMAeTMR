#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo das rotas - inicia servidor e testa todas as rotas
"""

import threading
import time
import requests
from app import app

def run_server():
    """Executa o servidor Flask"""
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def test_routes():
    """Testa todas as rotas importantes"""
    print("\n🧪 TESTANDO ROTAS PRINCIPAIS:")
    print("=" * 50)
    
    # Aguardar servidor inicializar
    time.sleep(2)
    
    routes_to_test = [
        ("http://127.0.0.1:5000/health", "Health Check"),
        ("http://127.0.0.1:5000/debug/rotas", "Debug Rotas"),
        ("http://127.0.0.1:5000/teste-postgresql-simples", "Teste PostgreSQL Simples"),
        ("http://127.0.0.1:5000/login", "Página de Login"),
        ("http://127.0.0.1:5000/register", "Página de Registro"),
        ("http://127.0.0.1:5000/debug/database", "Debug Database"),
        ("http://127.0.0.1:5000/api/usuarios", "API Usuários (GET)"),
    ]
    
    successful = 0
    total = len(routes_to_test)
    
    for url, description in routes_to_test:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {description} - OK")
                successful += 1
            else:
                print(f"⚠️ {description} - Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {description} - Conexão falhou")
        except Exception as e:
            print(f"❌ {description} - Erro: {str(e)}")
    
    print("=" * 50)
    print(f"📊 RESULTADO: {successful}/{total} rotas funcionando")
    
    if successful == total:
        print("🎉 SUCESSO! Todas as rotas principais estão funcionando!")
    elif successful >= total * 0.8:
        print("✅ BOM! A maioria das rotas está funcionando")
    else:
        print("⚠️ ATENÇÃO! Várias rotas com problemas")
    
    print("\n🌐 ACESSE NO NAVEGADOR:")
    print("   • http://127.0.0.1:5000/debug/rotas - Lista todas as rotas")
    print("   • http://127.0.0.1:5000/teste-postgresql-simples - Teste PostgreSQL")
    print("   • http://127.0.0.1:5000/login - Página de login")
    print("   • http://127.0.0.1:5000/health - Status do sistema")
    
    return successful == total

def main():
    print("🚀 TESTE COMPLETO DO SISTEMA TMA/TMR")
    print("=" * 50)
    
    # Iniciar servidor em thread separada
    print("⏳ Iniciando servidor Flask...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Testar rotas
    success = test_routes()
    
    if success:
        print("\n🎯 PRÓXIMOS PASSOS PARA TESTAR O SISTEMA COMPLETO:")
        print("1. ✅ Abra http://127.0.0.1:5000/login no navegador")
        print("2. ✅ Registre um novo usuário")
        print("3. ✅ Faça login")
        print("4. ✅ Acesse a página de tempos")
        print("5. ✅ Registre alguns dados TMA/TMR")
        print("6. ✅ Verifique se os dados foram salvos no PostgreSQL")
        
        print("\n🔧 COMANDOS ÚTEIS PARA DEBUG:")
        print("• Acessar http://127.0.0.1:5000/debug/database para ver dados do banco")
        print("• Acessar http://127.0.0.1:5000/debug/rotas para ver todas as rotas")
    else:
        print("\n🔧 PROBLEMAS DETECTADOS - VERIFIQUE:")
        print("1. Se o PostgreSQL está rodando")
        print("2. Se as credenciais no .env estão corretas")
        print("3. Se há erros no console do servidor")
    
    # Manter servidor ativo
    try:
        print(f"\n⏰ Servidor ativo por 60 segundos para testes manuais...")
        print("   Pressione Ctrl+C para parar")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")

if __name__ == "__main__":
    main()
