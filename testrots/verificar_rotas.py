#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples para verificar se o Flask está registrando todas as rotas
"""

# Importar o app
try:
    from app import app
    print("✅ App importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar app: {e}")
    exit(1)

# Listar todas as rotas registradas
print("\n🔍 ROTAS REGISTRADAS NO FLASK:")
print("=" * 60)

total_rotas = 0
for rule in app.url_map.iter_rules():
    methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
    print(f"📍 {rule.rule:<30} [{methods:<15}] -> {rule.endpoint}")
    total_rotas += 1

print("=" * 60)
print(f"📊 Total de rotas registradas: {total_rotas}")

# Verificar rotas específicas que deveriam existir
rotas_esperadas = [
    '/',
    '/login',
    '/register',
    '/registro', 
    '/tempos',
    '/teste',
    '/teste-postgresql',
    '/teste-postgresql-simples',
    '/debug/rotas',
    '/api/usuarios',
    '/api/login',
    '/api/registros',
    '/health'
]

print(f"\n🎯 VERIFICANDO ROTAS ESPECÍFICAS:")
rotas_encontradas = [str(rule.rule) for rule in app.url_map.iter_rules()]

for rota in rotas_esperadas:
    if rota in rotas_encontradas:
        print(f"✅ {rota}")
    else:
        print(f"❌ {rota} - NÃO ENCONTRADA")

# Testar se o app consegue inicializar
print(f"\n🧪 TESTE DE INICIALIZAÇÃO:")
try:
    with app.app_context():
        print("✅ Contexto da aplicação criado com sucesso")
        
        # Testar se as funções de view existem
        test_functions = [
            ('home', '/'),
            ('login_page', '/login'),
            ('teste_postgresql_page', '/teste-postgresql'),
            ('debug_rotas', '/debug/rotas')
        ]
        
        for func_name, rota in test_functions:
            if hasattr(app.view_functions, func_name):
                print(f"✅ Função {func_name} registrada para {rota}")
            else:
                print(f"❌ Função {func_name} NÃO encontrada para {rota}")
                
except Exception as e:
    print(f"❌ Erro ao criar contexto: {e}")

print(f"\n💡 PRÓXIMOS PASSOS:")
print("1. Se todas as rotas estão registradas, teste manualmente no navegador")
print("2. Se alguma rota não foi encontrada, verifique se há erro de sintaxe no app.py")
print("3. Execute: python -c \"from app import app; app.run(debug=True)\" para teste manual")
