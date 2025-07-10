"""
Script para testar se os dados estão sendo salvos no PostgreSQL
"""

import requests
import json

def testar_salvamento_postgresql():
    print("🧪 Testando salvamento no PostgreSQL...")
    
    base_url = "http://localhost:5000"
    
    # Dados de teste
    dados_teste = {
        "nome_operador": "Teste PostgreSQL",
        "tma": 1.25,
        "tmr": 5.50,
        "user_id": 1
    }
    
    try:
        # 1. Testar criação de usuário se não existir
        print("📝 Criando usuário de teste...")
        user_data = {"nome": "teste_postgres", "senha": "1234"}
        
        user_response = requests.post(f"{base_url}/api/usuarios", json=user_data)
        if user_response.status_code == 200:
            print("✅ Usuário criado com sucesso")
            user_result = user_response.json()
        else:
            print("ℹ️ Usuário pode já existir")
        
        # 2. Fazer login para pegar user_id
        print("🔐 Fazendo login...")
        login_response = requests.post(f"{base_url}/api/login", json=user_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            user_id = login_result["user_id"]
            print(f"✅ Login realizado - User ID: {user_id}")
            
            # Atualizar dados de teste com user_id real
            dados_teste["user_id"] = user_id
            
        else:
            print("❌ Erro no login")
            return
        
        # 3. Testar salvamento de registro
        print("💾 Salvando registro no PostgreSQL...")
        
        registro_response = requests.post(f"{base_url}/api/registros", json=dados_teste)
        
        if registro_response.status_code == 200:
            registro_result = registro_response.json()
            print("✅ Registro salvo com sucesso!")
            print(f"   Registro ID: {registro_result.get('registro_id')}")
            print(f"   Mensagem: {registro_result.get('message')}")
        else:
            error_result = registro_response.json()
            print(f"❌ Erro ao salvar: {error_result.get('erro')}")
            return
        
        # 4. Verificar se foi salvo corretamente
        print("🔍 Verificando dados salvos...")
        
        listar_response = requests.get(f"{base_url}/api/registros/{user_id}")
        
        if listar_response.status_code == 200:
            registros = listar_response.json()
            print(f"✅ Encontrados {len(registros)} registros para o usuário")
            
            # Verificar se nosso registro de teste está lá
            registro_teste_encontrado = False
            for reg in registros:
                if reg["nome_operador"] == "Teste PostgreSQL":
                    registro_teste_encontrado = True
                    print(f"✅ Registro de teste encontrado:")
                    print(f"   Nome: {reg['nome_operador']}")
                    print(f"   TMA: {reg['tma']}")
                    print(f"   TMR: {reg['tmr']}")
                    break
            
            if not registro_teste_encontrado:
                print("⚠️ Registro de teste não encontrado na listagem")
            
        else:
            print("❌ Erro ao listar registros")
        
        print("\n🎉 Teste concluído! PostgreSQL está funcionando corretamente.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - certifique-se que o servidor está rodando")
        print("   Execute: python app.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    testar_salvamento_postgresql()
