# -*- coding: utf-8 -*-
"""
Versão de emergência - app mínimo com PostgreSQL
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import json

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "🏠 App de emergência funcionando!"

@app.route("/health")
def health():
    return jsonify({"status": "OK", "message": "Sistema TMA/TMR funcionando"})

@app.route("/teste-postgresql-emergencia")
def teste_postgresql():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Teste PostgreSQL</title><meta charset="UTF-8"></head>
    <body>
        <h1>🧪 Teste PostgreSQL - Versão Emergência</h1>
        <button onclick="testarPostgreSQL()">Testar PostgreSQL</button>
        <div id="resultado"></div>
        
        <script>
        async function testarPostgreSQL() {
            try {
                const response = await fetch('/api/test-postgres');
                const data = await response.json();
                document.getElementById('resultado').innerHTML = 
                    '<p style="color: green;">✅ ' + data.message + '</p>';
            } catch (error) {
                document.getElementById('resultado').innerHTML = 
                    '<p style="color: red;">❌ Erro: ' + error.message + '</p>';
            }
        }
        </script>
    </body>
    </html>
    """

@app.route("/api/test-postgres")
def test_postgres():
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='TMAeTMR', 
            user='postgres',
            password='120990'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": f"PostgreSQL funcionando! Versão: {version[:50]}..."
        })
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Erro PostgreSQL: {str(e)}"
        }), 500

if __name__ == "__main__":
    print("🚀 App de emergência na porta 5002")
    print("🔗 Acesse: http://localhost:5002/teste-postgresql-emergencia")
    app.run(host='0.0.0.0', port=5002, debug=True)
