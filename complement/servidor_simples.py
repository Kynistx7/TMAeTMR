#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iniciar servidor de forma simples
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 INICIANDO SERVIDOR FLASK")
    print("=" * 50)
    
    try:
        from TMAeTMR.app import app
        print("✅ App importado com sucesso")
        
        # Mostrar rotas registradas
        print("\n📋 Rotas registradas:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if not rule.rule.startswith('/static'):
                    methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
                    print(f"   {rule.rule:25s} → {methods}")
        
        print("\n🌐 Servidor iniciando em: http://127.0.0.1:5000")
        print("🔗 URLs para testar:")
        print("   • http://127.0.0.1:5000/login")
        print("   • http://127.0.0.1:5000/admin")
        print("   • http://127.0.0.1:5000/teste-admin")
        print("\n🛑 Para parar: Ctrl+C")
        print("=" * 50)
        
        # Iniciar servidor
        app.run(debug=True, host='127.0.0.1', port=5000)
        
    except ImportError as e:
        print(f"❌ Erro ao importar app: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
