# -*- coding: utf-8 -*-
"""
Teste simples para verificar se o servidor está funcionando
"""

import requests
import time

def testar_servidor_basico():
    print("🔍 Testando se o servidor está rodando...")
    
    base_url = "http://localhost:5000"
    
    # Lista de rotas para testar
    rotas_teste = [
        ("/", "Página inicial"),
        ("/health", "Health check"),
        ("/login", "Página de login"),
        ("/teste-postgresql", "Página de teste PostgreSQL"),
        ("/debug", "Debug info")
    ]
    
    print(f"🌐 Testando servidor em: {base_url}")
    print("=" * 50)
    
    servidor_funcionando = False
    
    for rota, descricao in rotas_teste:
        try:
            print(f"📋 Testando {rota} ({descricao})...")
            
            response = requests.get(f"{base_url}{rota}", timeout=5)
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                print(f"   ✅ OK")
                servidor_funcionando = True
            elif response.status_code == 404:
                print(f"   ❌ Não encontrado (404)")
            elif response.status_code == 500:
                print(f"   ❌ Erro interno (500)")
            else:
                print(f"   ⚠️ Código: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONEXÃO RECUSADA - Servidor não está rodando!")
            break
        except requests.exceptions.Timeout:
            print(f"   ❌ TIMEOUT")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    if not servidor_funcionando:
        print("\n❌ SERVIDOR NÃO ESTÁ RODANDO OU COM PROBLEMAS!")
        print("📋 Soluções:")
        print("   1. Execute: python app.py")
        print("   2. Verifique se apareceu '🌐 Servidor iniciando'")
        print("   3. Verifique se a porta 5000 está livre")
        print("   4. Olhe os logs de erro no terminal")
        return False
    else:
        print(f"\n✅ Servidor está respondendo!")
        return True

def verificar_porta():
    print("\n🔌 Verificando se a porta 5000 está disponível...")
    
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("✅ Porta 5000 está sendo usada (servidor provavelmente rodando)")
            return True
        else:
            print("❌ Porta 5000 está livre (servidor NÃO está rodando)")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar porta: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE DO SERVIDOR")
    print("=" * 40)
    
    print("⚠️ CERTIFIQUE-SE QUE O SERVIDOR ESTÁ RODANDO:")
    print("   Execute em outro terminal: python app.py")
    print()
    
    # Aguardar um pouco
    time.sleep(1)
    
    # Verificar porta primeiro
    porta_ok = verificar_porta()
    
    if porta_ok:
        # Testar rotas
        testar_servidor_basico()
    else:
        print("\n❌ SERVIDOR NÃO ESTÁ RODANDO!")
        print("📋 Execute estes comandos:")
        print("   1. python app.py")
        print("   2. Aguarde aparecer '🌐 Servidor iniciando'")
        print("   3. Em outro terminal: python teste_servidor.py")
