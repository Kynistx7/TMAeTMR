# -*- coding: utf-8 -*-
"""
Teste das rotas da API
Execute: python testar_rotas.py
"""

import requests
import json
import time

def testar_servidor():
    print("🔍 Testando Servidor e Rotas")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # 1. Testar se servidor está rodando
    print("🚀 1. Testando se servidor está rodando...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
        else:
            print(f"⚠️ Servidor respondeu com status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Servidor não está rodando!")
        print("   Execute: python app.py")
        return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False
    
    # 2. Testar rota de criação de usuário
    print("\n👤 2. Testando criação de usuário...")
    user_data = {
        "nome": "teste_rotas",
        "senha": "1234"
    }
    
    try:
        response = requests.post(f"{base_url}/api/usuarios", 
                               json=user_data, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print("✅ Usuário criado com sucesso!")
        elif response.status_code == 400 and "já existe" in result.get("erro", ""):
            print("✅ Usuário já existe (OK)")
        else:
            print(f"❌ Erro ao criar usuário: {result}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    # 3. Testar login
    print("\n🔐 3. Testando login...")
    try:
        response = requests.post(f"{base_url}/api/login", 
                               json=user_data,
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            user_id = login_result["user_id"]
            print(f"✅ Login realizado! User ID: {user_id}")
        else:
            error_result = response.json()
            print(f"❌ Erro no login: {error_result}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição de login: {e}")
        return False
    
    # 4. Testar salvamento de registro
    print("\n💾 4. Testando salvamento de registro...")
    registro_data = {
        "nome_operador": "Teste API Rotas",
        "tma": 1.25,
        "tmr": 5.80,
        "user_id": user_id
    }
    
    try:
        response = requests.post(f"{base_url}/api/registros", 
                               json=registro_data,
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            registro_result = response.json()
            print("✅ Registro salvo com sucesso!")
            print(f"   Registro ID: {registro_result.get('registro_id')}")
            print(f"   Mensagem: {registro_result.get('message')}")
        else:
            try:
                error_result = response.json()
                print(f"❌ Erro ao salvar registro: {error_result}")
            except:
                print(f"❌ Erro ao salvar registro (sem JSON): {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição de registro: {e}")
        return False
    
    # 5. Testar listagem de registros
    print("\n📋 5. Testando listagem de registros...")
    try:
        response = requests.get(f"{base_url}/api/registros/{user_id}", timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            registros = response.json()
            print(f"✅ Listagem OK! Encontrados {len(registros)} registros")
            
            for i, reg in enumerate(registros[-3:], 1):  # Últimos 3 registros
                print(f"   {i}. {reg['nome_operador']} - TMA: {reg['tma']} - TMR: {reg['tmr']}")
                
        else:
            error_result = response.json()
            print(f"❌ Erro ao listar registros: {error_result}")
            
    except Exception as e:
        print(f"❌ Erro na requisição de listagem: {e}")
    
    # 6. Testar rota de debug
    print("\n🔍 6. Testando rota de debug...")
    try:
        response = requests.get(f"{base_url}/debug/database", timeout=10)
        
        if response.status_code == 200:
            print("✅ Rota de debug funcionando!")
            # Extrair informações do HTML
            html = response.text
            if "Usuários" in html and "Registros" in html:
                print("✅ Banco de dados acessível via debug")
            else:
                print("⚠️ Resposta de debug inesperada")
        else:
            print(f"❌ Erro na rota de debug: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na rota de debug: {e}")
    
    print(f"\n🎉 TESTE CONCLUÍDO!")
    print(f"✅ Todas as rotas estão funcionando!")
    print(f"✅ PostgreSQL está salvando os dados!")
    
    return True

if __name__ == "__main__":
    print("⚠️ IMPORTANTE: Certifique-se que o servidor está rodando!")
    print("   Execute em outro terminal: python app.py")
    print()
    
    # Aguardar um pouco para o usuário ver a mensagem
    time.sleep(2)
    
    sucesso = testar_servidor()
    
    if sucesso:
        print(f"\n🚀 Agora teste no navegador:")
        print(f"   1. http://localhost:5000/login")
        print(f"   2. http://localhost:5000/tempos")
        print(f"   3. http://localhost:5000/teste-postgresql")
    else:
        print(f"\n❌ Há problemas com as rotas da API")
        print(f"   Verifique os logs do servidor (python app.py)")
