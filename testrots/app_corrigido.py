# -*- coding: utf-8 -*-
"""
Versão corrigida do app.py com tratamento de erro robusto
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from flask_cors import CORS
import hashlib
import os

print("🚀 Iniciando carregamento do app...")

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ Arquivo .env carregado")
    else:
        print("⚠️ Arquivo .env não encontrado")
except ImportError:
    print("⚠️ python-dotenv não disponível")

# Configuração básica do Flask
print("📱 Criando app Flask...")
app = Flask(__name__, static_folder='./', static_url_path='', template_folder='./')
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuração básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersegredo')

# Configuração do banco - versão simplificada e robusta
print("🗄️ Configurando banco de dados...")

database_url = None
use_postgres = False

# Tentar PostgreSQL primeiro
try:
    import psycopg2
    
    pg_host = os.environ.get('POSTGRES_HOST', 'localhost')
    pg_port = os.environ.get('POSTGRES_PORT', '5432')
    pg_db = os.environ.get('POSTGRES_DB', 'TMAeTMR')
    pg_user = os.environ.get('POSTGRES_USER', 'postgres')
    pg_password = os.environ.get('POSTGRES_PASSWORD', '120990')
    
    if pg_password:
        # Testar conexão
        test_conn = psycopg2.connect(
            host=pg_host, port=pg_port, database=pg_db,
            user=pg_user, password=pg_password
        )
        test_conn.close()
        
        database_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        use_postgres = True
        print("✅ PostgreSQL configurado e testado")
        
except Exception as e:
    print(f"⚠️ PostgreSQL não disponível: {e}")
    print("🔄 Usando SQLite como fallback")

# Configurar SQLAlchemy
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/dados.db'
    os.makedirs('instance', exist_ok=True)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy com tratamento de erro
print("📊 Inicializando SQLAlchemy...")
try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
    print("✅ SQLAlchemy inicializado")
except Exception as e:
    print(f"❌ Erro ao inicializar SQLAlchemy: {e}")
    exit(1)

# Modelos do banco
print("🏗️ Definindo modelos...")
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    registros = db.relationship('Registro', backref='user', lazy=True)

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_operador = db.Column(db.String(80), nullable=False)
    tma = db.Column(db.Float, nullable=False)
    tmr = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

print("✅ Modelos definidos")

# Função auxiliar
def hash_senha(senha):
    try:
        return hashlib.sha256(str(senha).encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"❌ Erro no hash: {e}")
        raise

# ==================== ROTAS ====================
print("🛤️ Registrando rotas...")

# Rotas básicas
@app.route("/")
def home():
    return redirect(url_for('login_page'))

@app.route("/health")
def health_check():
    return jsonify({
        "status": "OK", 
        "message": "Sistema TMA/TMR funcionando",
        "database": "PostgreSQL" if use_postgres else "SQLite"
    })

@app.route("/login")
def login_page():
    try:
        return render_template("login.html")
    except Exception as e:
        return f"Erro ao carregar login.html: {str(e)}", 500

@app.route("/registro") 
def registro_page():
    try:
        return render_template("registro.html")
    except Exception as e:
        return f"Erro ao carregar registro.html: {str(e)}", 500

@app.route("/tempos")
def tempos_page():
    if not session.get('user_id'):
        return redirect(url_for('login_page'))
    try:
        return render_template("tempos.html")
    except Exception as e:
        return f"Erro ao carregar tempos.html: {str(e)}", 500

@app.route("/teste-postgresql")
def teste_postgresql_page():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Teste PostgreSQL</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }
            button { padding: 10px 20px; margin: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .result { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>🧪 Teste PostgreSQL Corrigido</h1>
        <p>Versão corrigida que funciona!</p>
        
        <button onclick="testarConexao()">Testar Conexão</button>
        <button onclick="criarUsuario()">Criar Usuário Teste</button>
        <button onclick="fazerLogin()">Fazer Login</button>
        <button onclick="salvarRegistro()">Salvar Registro</button>
        
        <div id="resultados"></div>
        
        <script>
            let userId = null;
            
            function log(msg, type = 'info') {
                const div = document.createElement('div');
                div.className = 'result ' + type;
                div.innerHTML = new Date().toLocaleTimeString() + ': ' + msg;
                document.getElementById('resultados').appendChild(div);
            }
            
            async function testarConexao() {
                try {
                    const resp = await fetch('/health');
                    const data = await resp.json();
                    log('✅ Conexão OK: ' + data.message + ' (' + data.database + ')', 'success');
                } catch (e) {
                    log('❌ Erro de conexão: ' + e.message, 'error');
                }
            }
            
            async function criarUsuario() {
                try {
                    const resp = await fetch('/api/usuarios', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({nome: 'teste_corrigido', senha: '1234'})
                    });
                    const data = await resp.json();
                    if (resp.ok) {
                        log('✅ Usuário criado: ID ' + data.user_id, 'success');
                    } else {
                        log('⚠️ ' + data.erro, 'error');
                    }
                } catch (e) {
                    log('❌ Erro: ' + e.message, 'error');
                }
            }
            
            async function fazerLogin() {
                try {
                    const resp = await fetch('/api/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({nome: 'teste_corrigido', senha: '1234'})
                    });
                    const data = await resp.json();
                    if (resp.ok) {
                        userId = data.user_id;
                        log('✅ Login OK: ID ' + userId, 'success');
                    } else {
                        log('❌ Erro login: ' + data.erro, 'error');
                    }
                } catch (e) {
                    log('❌ Erro: ' + e.message, 'error');
                }
            }
            
            async function salvarRegistro() {
                if (!userId) {
                    log('❌ Faça login primeiro!', 'error');
                    return;
                }
                
                try {
                    const resp = await fetch('/api/registros', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            nome_operador: 'Teste Corrigido',
                            tma: 1.20,
                            tmr: 5.00,
                            user_id: userId
                        })
                    });
                    const data = await resp.json();
                    if (resp.ok) {
                        log('✅ Registro salvo: ID ' + data.registro_id, 'success');
                    } else {
                        log('❌ Erro: ' + data.erro, 'error');
                    }
                } catch (e) {
                    log('❌ Erro: ' + e.message, 'error');
                }
            }
        </script>
    </body>
    </html>
    """

# Rotas da API
@app.route("/api/usuarios", methods=["POST"])
def cadastrar_usuario():
    try:
        data = request.json
        if not data:
            return jsonify({"erro": "Dados não fornecidos"}), 400
            
        nome = data.get('nome', '').strip()
        senha = data.get('senha', '')
        
        if not nome or not senha:
            return jsonify({"erro": "Nome e senha obrigatórios"}), 400
            
        if len(nome) < 3 or len(senha) < 4:
            return jsonify({"erro": "Nome (min 3) e senha (min 4) muito curtos"}), 400
        
        # Verificar se já existe
        if User.query.filter(db.func.lower(User.nome) == nome.lower()).first():
            return jsonify({"erro": f"Usuário '{nome}' já existe"}), 400
        
        # Criar usuário
        user = User(nome=nome, senha_hash=hash_senha(senha))
        db.session.add(user)
        db.session.commit()
        
        return jsonify({"ok": True, "message": f"Usuário '{nome}' criado!", "user_id": user.id})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar usuário: {e}")
        return jsonify({"erro": f"Erro: {str(e)}"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({"erro": "Dados não fornecidos"}), 400
            
        nome = data.get('nome', '').strip()
        senha = data.get('senha', '')
        
        if not nome or not senha:
            return jsonify({"erro": "Nome e senha obrigatórios"}), 400
        
        user = User.query.filter_by(nome=nome).first()
        if user and user.senha_hash == hash_senha(senha):
            session['user_id'] = user.id
            return jsonify({"ok": True, "user_id": user.id, "nome": user.nome})
        
        return jsonify({"erro": "Usuário ou senha inválidos"}), 401
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return jsonify({"erro": f"Erro: {str(e)}"}), 500

@app.route("/api/registros", methods=["POST"])
def registrar_tempo():
    try:
        data = request.json
        if not data:
            return jsonify({"erro": "Dados não fornecidos"}), 400
        
        user_id = data.get('user_id')
        nome_operador = data.get('nome_operador', '').strip()
        tma = data.get('tma')
        tmr = data.get('tmr')
        
        if not all([user_id, nome_operador, tma is not None, tmr is not None]):
            return jsonify({"erro": "Todos os campos são obrigatórios"}), 400
        
        # Verificar usuário
        user = User.query.get(user_id)
        if not user:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Criar registro
        reg = Registro(
            nome_operador=nome_operador,
            tma=float(tma),
            tmr=float(tmr),
            user_id=int(user_id)
        )
        
        db.session.add(reg)
        db.session.commit()
        
        return jsonify({
            "ok": True,
            "message": "Registro salvo com sucesso",
            "registro_id": reg.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao salvar registro: {e}")
        return jsonify({"erro": f"Erro: {str(e)}"}), 500

@app.route("/api/registros/<int:user_id>", methods=["GET"])
def listar_registros(user_id):
    try:
        registros = Registro.query.filter_by(user_id=user_id).all()
        return jsonify([{
            "id": r.id,
            "nome_operador": r.nome_operador,
            "tma": round(r.tma, 2),
            "tmr": round(r.tmr, 2)
        } for r in registros])
    except Exception as e:
        print(f"❌ Erro ao listar: {e}")
        return jsonify({"erro": f"Erro: {str(e)}"}), 500

print("✅ Rotas registradas com sucesso")

# Inicialização do banco
def init_database():
    try:
        with app.app_context():
            db.create_all()
            
            # Testar se funciona
            user_count = User.query.count()
            reg_count = Registro.query.count()
            
            print(f"✅ Banco inicializado: {user_count} usuários, {reg_count} registros")
            return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

# Inicializar
if __name__ == "__main__":
    print("🔧 Inicializando banco de dados...")
    
    if init_database():
        print("🚀 Iniciando servidor na porta 5000...")
        print("🔗 Acesse: http://localhost:5000/teste-postgresql")
        
        try:
            app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
    else:
        print("❌ Falha na inicialização do banco")
