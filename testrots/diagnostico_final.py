#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste direto do sistema - sem threading
Apenas verifica se o app pode ser inicializado e se as principais funcionalidades funcionam
"""

from app import app, db, User, Registro

def test_database():
    """Testa conexão e operações básicas do banco"""
    print("🗃️ TESTANDO BANCO DE DADOS:")
    print("-" * 40)
    
    try:
        with app.app_context():
            # Testar se consegue criar tabelas
            db.create_all()
            print("✅ Tabelas criadas/verificadas com sucesso")
            
            # Testar contagem de usuários
            user_count = User.query.count()
            registro_count = Registro.query.count()
            print(f"📊 Estado atual: {user_count} usuários, {registro_count} registros")
            
            # Teste básico de criação de usuário (se não existir)
            test_user = User.query.filter_by(nome='teste_diagnostico').first()
            if not test_user:
                from app import hash_senha
                test_user = User(nome='teste_diagnostico', senha_hash=hash_senha('123456'))
                db.session.add(test_user)
                db.session.commit()
                print("✅ Usuário de teste criado com sucesso")
            else:
                print("✅ Usuário de teste já existe")
                
            # Teste de criação de registro
            test_registro = Registro(
                nome_operador='Operador Teste',
                tma=120.5,
                tmr=90.3,
                user_id=test_user.id
            )
            db.session.add(test_registro)
            db.session.commit()
            print("✅ Registro de teste criado com sucesso")
            
            # Limpeza - remover dados de teste
            db.session.delete(test_registro)
            if test_user.nome == 'teste_diagnostico':
                # Só remove se for o usuário que criamos agora
                existing_registros = Registro.query.filter_by(user_id=test_user.id).all()
                if len(existing_registros) == 0:  # Só tinha o registro que acabamos de criar
                    db.session.delete(test_user)
            db.session.commit()
            print("✅ Dados de teste removidos")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro no banco de dados: {str(e)}")
        return False

def test_routes_config():
    """Testa se as rotas estão configuradas corretamente"""
    print("\n🛣️ TESTANDO CONFIGURAÇÃO DAS ROTAS:")
    print("-" * 40)
    
    critical_routes = [
        '/',
        '/login',
        '/register', 
        '/tempos',
        '/api/usuarios',
        '/api/login',
        '/api/registros',
        '/health'
    ]
    
    route_rules = [str(rule.rule) for rule in app.url_map.iter_rules()]
    
    missing_routes = []
    for route in critical_routes:
        if route in route_rules:
            print(f"✅ {route}")
        else:
            print(f"❌ {route} - NÃO ENCONTRADA")
            missing_routes.append(route)
    
    if not missing_routes:
        print("✅ Todas as rotas críticas estão registradas")
        return True
    else:
        print(f"❌ {len(missing_routes)} rotas críticas ausentes")
        return False

def test_static_files():
    """Verifica se arquivos estáticos existem"""
    print("\n📁 VERIFICANDO ARQUIVOS ESTÁTICOS:")
    print("-" * 40)
    
    import os
    
    static_files = [
        ('login.html', 'Template de login'),
        ('registro.html', 'Template de registro'),
        ('tempos.html', 'Template de tempos'),
        ('index.html', 'Template principal'),
        ('css/styles.css', 'CSS principal'),
        ('js/script.js', 'JavaScript principal')
    ]
    
    all_exist = True
    for file_path, description in static_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} - ARQUIVO NÃO ENCONTRADO")
            all_exist = False
    
    return all_exist

def test_environment():
    """Testa configuração do ambiente"""
    print("\n🌍 TESTANDO AMBIENTE:")
    print("-" * 40)
    
    import os
    
    config_items = [
        ('DATABASE_URL', os.environ.get('DATABASE_URL')),
        ('POSTGRES_HOST', os.environ.get('POSTGRES_HOST')),
        ('POSTGRES_DB', os.environ.get('POSTGRES_DB')),
        ('POSTGRES_USER', os.environ.get('POSTGRES_USER')),
        ('POSTGRES_PASSWORD', os.environ.get('POSTGRES_PASSWORD'))
    ]
    
    for key, value in config_items:
        if value:
            if 'PASSWORD' in key:
                print(f"✅ {key} = ****** (configurado)")
            else:
                print(f"✅ {key} = {value}")
        else:
            print(f"⚠️ {key} = não configurado")
    
    # Verificar qual banco está sendo usado
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'postgresql' in db_url:
        print("✅ Usando PostgreSQL")
        return True
    elif 'sqlite' in db_url:
        print("⚠️ Usando SQLite (fallback)")
        return True
    else:
        print("❌ Configuração de banco desconhecida")
        return False

def main():
    print("🔍 DIAGNÓSTICO COMPLETO DO SISTEMA TMA/TMR")
    print("=" * 60)
    
    # Lista de testes
    tests = [
        ("Ambiente", test_environment),
        ("Rotas", test_routes_config),
        ("Arquivos Estáticos", test_static_files),
        ("Banco de Dados", test_database)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 TESTE: {test_name.upper()}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERRO no teste {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name:<20} : {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("\n📱 PRÓXIMOS PASSOS:")
        print("1. Execute: python app.py")
        print("2. Acesse: http://127.0.0.1:5000/login")
        print("3. Registre um usuário e teste o sistema")
        
    elif passed >= total * 0.75:
        print("✅ SISTEMA MAJORITARIAMENTE FUNCIONAL")
        print("⚠️ Alguns componentes podem ter problemas menores")
        
    else:
        print("⚠️ SISTEMA COM PROBLEMAS SIGNIFICATIVOS")
        print("🔧 Revise os testes que falharam antes de usar")
    
    print(f"\n💡 Para iniciar o servidor:")
    print(f"   python app.py")

if __name__ == "__main__":
    main()
