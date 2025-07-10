# -*- coding: utf-8 -*-
"""
Teste simples para diagnosticar erro 500
"""

import requests
import json

def testar_erro_500():
    print("🔍 Diagnosticando Erro 500")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # 1. Testar se servidor responde
    print("1. Testando servidor básico...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Servidor respondendo")
        else:
            print("❌ Servidor com problemas")
            return
    except Exception as e:
        print(f"❌ Servidor não acessível: {e}")
        return
    
    # 2. Testar rota de usuários com dados mínimos
    print("\n2. Testando criação de usuário...")
    
    test_data = {
        "nome": "teste123",
        "senha": "1234"
    }
    
    try:
        print(f"   Enviando: {test_data}")
        
        response = requests.post(
            f"{base_url}/api/usuarios",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status HTTP: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        # Tentar obter o texto da resposta
        response_text = response.text
        print(f"   Resposta (texto): {response_text[:200]}...")
        
        # Tentar fazer parse do JSON
        if response_text.strip():
            try:
                response_json = response.json()
                print(f"   Resposta (JSON): {response_json}")
            except json.JSONDecodeError as je:
                print(f"   ❌ Erro ao decodificar JSON: {je}")
                print(f"   Resposta completa: {response_text}")
        else:
            print("   ❌ Resposta vazia!")
        
        if response.status_code == 200:
            print("✅ Usuário criado com sucesso!")
        elif response.status_code == 400:
            print("⚠️ Usuário já existe ou dados inválidos (normal)")
        else:
            print(f"❌ Erro {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição")
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
    # 3. Testar outras rotas básicas
    print("\n3. Testando outras rotas...")
    
    test_routes = [
        ("/", "GET"),
        ("/login", "GET"),
        ("/debug", "GET")
    ]
    
    for route, method in test_routes:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{route}", timeout=5)
            
            print(f"   {method} {route}: {response.status_code}")
            
        except Exception as e:
            print(f"   {method} {route}: ERRO - {e}")

if __name__ == "__main__":
    print("⚠️ CERTIFIQUE-SE que o servidor está rodando:")
    print("   python app.py")
    print()
    
    testar_erro_500()
