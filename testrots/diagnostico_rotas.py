# -*- coding: utf-8 -*-
"""
Teste para verificar rotas registradas
"""

import requests

def testar_rotas_especificas():
    print("🔍 Testando rotas específicas...")
    
    base_url = "http://localhost:5000"
    
    # Lista de rotas para testar
    rotas = [
        "/",
        "/health", 
        "/login",
        "/debug",
        "/debug/rotas",
        "/teste",
        "/teste-postgresql",
        "/teste-postgresql-simples",
        "/api/usuarios"
    ]
    
    print(f"🌐 Testando {len(rotas)} rotas em {base_url}")
    print("=" * 60)
    
    for rota in rotas:
        try:
            if rota == "/api/usuarios":
                # POST para esta rota
                response = requests.post(f"{base_url}{rota}", 
                                       json={"nome": "teste", "senha": "1234"},
                                       timeout=3)
            else:
                # GET para outras rotas
                response = requests.get(f"{base_url}{rota}", timeout=3)
            
            status = response.status_code
            
            if status == 200:
                print(f"✅ {rota} - OK")
            elif status == 404:
                print(f"❌ {rota} - NÃO ENCONTRADA (404)")
            elif status == 400:
                print(f"⚠️ {rota} - Erro de dados (400) - Normal para APIs")
            elif status == 500:
                print(f"💥 {rota} - ERRO INTERNO (500)")
            else:
                print(f"🔍 {rota} - Status: {status}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {rota} - SERVIDOR NÃO CONECTA")
            break
        except requests.exceptions.Timeout:
            print(f"⏰ {rota} - TIMEOUT")
        except Exception as e:
            print(f"💥 {rota} - ERRO: {e}")

    # Verificar se consegue acessar debug de rotas
    print(f"\n🔍 Tentando acessar debug de rotas...")
    try:
        response = requests.get(f"{base_url}/debug/rotas", timeout=5)
        if response.status_code == 200:
            print("✅ Debug de rotas acessível!")
            print("🌐 Acesse: http://localhost:5000/debug/rotas para ver todas as rotas")
        else:
            print(f"❌ Debug de rotas retornou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar debug: {e}")

if __name__ == "__main__":
    print("🧪 DIAGNÓSTICO DE ROTAS")
    print("=" * 30)
    print("⚠️ Certifique-se que o servidor está rodando:")
    print("   python app.py")
    print()
    
    testar_rotas_especificas()
