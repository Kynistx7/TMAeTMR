# -*- coding: utf-8 -*-
"""
Versão simplificada do app para teste de rotas
"""

from flask import Flask, jsonify
from flask_cors import CORS

# Criar app básico
app = Flask(__name__)
CORS(app)

print("🚀 Criando app Flask simplificado...")

# Rotas básicas para teste
@app.route("/")
def home():
    return "🏠 Servidor funcionando!"

@app.route("/health")
def health():
    return jsonify({"status": "OK", "message": "Servidor funcionando"})

@app.route("/teste-simples")
def teste_simples():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste Simples</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>🧪 Teste de Rotas - Funcionando!</h1>
        <p>Se você está vendo isso, as rotas estão funcionando.</p>
        <button onclick="testarAPI()">Testar API</button>
        <div id="resultado"></div>
        
        <script>
        async function testarAPI() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                document.getElementById('resultado').innerHTML = 
                    '<p style="color: green;">✅ API funcionando: ' + data.status + '</p>';
            } catch (error) {
                document.getElementById('resultado').innerHTML = 
                    '<p style="color: red;">❌ Erro na API: ' + error.message + '</p>';
            }
        }
        </script>
    </body>
    </html>
    """

@app.route("/debug/rotas-simples")
def debug_rotas_simples():
    """Lista rotas do app simplificado"""
    rotas = []
    for rule in app.url_map.iter_rules():
        rotas.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    
    html = "<h1>🔍 Rotas do App Simplificado</h1>"
    html += f"<p>Total: {len(rotas)} rotas</p><ul>"
    
    for rota in sorted(rotas, key=lambda x: x['rule']):
        methods = ', '.join([m for m in rota['methods'] if m not in ['HEAD', 'OPTIONS']])
        html += f"<li><strong>{rota['rule']}</strong> ({methods})</li>"
    
    html += "</ul>"
    html += "<p><a href='/teste-simples'>← Voltar para teste</a></p>"
    return html

if __name__ == "__main__":
    print("🌐 Iniciando servidor simplificado na porta 5001...")
    print("🔗 Acesse: http://localhost:5001/teste-simples")
    print("🔍 Debug: http://localhost:5001/debug/rotas-simples")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        print(f"❌ Erro: {e}")
