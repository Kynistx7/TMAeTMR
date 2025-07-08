from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import hashlib
import os

# Configuração do Flask para trabalhar na raiz do projeto
app = Flask(__name__, static_folder='./', static_url_path='', template_folder='./')
CORS(app)

# Configuração do banco de dados
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Para deploy (Railway/Render) - ajustar PostgreSQL URL se necessário
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"📊 Usando banco de dados: PostgreSQL")
else:
    # Para desenvolvimento local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/dados.db'
    print(f"📊 Usando banco de dados: SQLite local")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersegredo')
db = SQLAlchemy(app)

# Rota para servir arquivos estáticos (CSS, JS, imagens)
@app.route('/css/<path:filename>')
def css_files(filename):
    return send_from_directory('css', filename)

@app.route('/js/<path:filename>')
def js_files(filename):
    return send_from_directory('js', filename)

@app.route('/img/<path:filename>')
def img_files(filename):
    return send_from_directory('img', filename)

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


def hash_senha(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

@app.route("/")
def home():
    return redirect(url_for('login_page'))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("registro.html")

@app.route("/registro")
def registro_page():
    return render_template("registro.html")

@app.route("/tempos")
def tempos_page():
    if not session.get('user_id'):
        return redirect(url_for('login_page'))
    return render_template("tempos.html")

@app.route("/tma")
def tma_page():
    if not session.get('user_id'):
        return redirect(url_for('login_page'))
    return render_template("tempos.html")

@app.route("/tmr")
def tmr_page():
    if not session.get('user_id'):
        return redirect(url_for('login_page'))
    return render_template("tempos.html")

@app.route("/dashboard")
def dashboard_page():
    # Checa login por sessão (opcional, só visual)
    if not session.get('user_id'):
        return redirect(url_for('login_page'))
    return render_template("index.html")

@app.route("/index")
def index_page():
    return render_template("index.html")

@app.route("/teste")
def teste_page():
    return render_template("teste.html")

# --- API ---

@app.route("/api/usuarios", methods=["POST"])
def cadastrar_usuario():
    data = request.json
    nome = data.get('nome', '').strip()
    senha = data.get('senha', '')
    
    # Validações
    if not nome or not senha:
        return jsonify({"erro": "Nome e senha são obrigatórios"}), 400
    
    if len(nome) < 3:
        return jsonify({"erro": "Nome deve ter pelo menos 3 caracteres"}), 400
    
    if len(senha) < 4:
        return jsonify({"erro": "Senha deve ter pelo menos 4 caracteres"}), 400
    
    # Verifica se usuário já existe (case-insensitive)
    existing_user = User.query.filter(db.func.lower(User.nome) == nome.lower()).first()
    if existing_user:
        return jsonify({"erro": f"Usuário '{nome}' já existe"}), 400
    
    try:
        user = User(nome=nome, senha_hash=hash_senha(senha))
        db.session.add(user)
        db.session.commit()
        return jsonify({"ok": True, "message": f"Usuário '{nome}' cadastrado com sucesso!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao cadastrar usuário: {str(e)}"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(nome=data['nome']).first()
    if user and user.senha_hash == hash_senha(data['senha']):
        session['user_id'] = user.id
        return jsonify({"ok": True, "user_id": user.id, "nome": user.nome})
    return jsonify({"erro": "Usuário ou senha inválidos"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop('user_id', None)
    return jsonify({"ok": True})

@app.route("/api/registros", methods=["POST"])
def registrar_tempo():
    try:
        data = request.json
        print(f"Dados recebidos: {data}")
        
        user_id = data.get('user_id')
        if not user_id:
            print("Erro: user_id não fornecido")
            return jsonify({"erro": "Não autenticado"}), 401
        
        # Verificar se o usuário existe
        user = User.query.get(user_id)
        if not user:
            print(f"Erro: Usuário {user_id} não encontrado")
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        reg = Registro(
            nome_operador=data['nome_operador'],
            tma=float(data['tma']),
            tmr=float(data['tmr']),
            user_id=int(user_id)
        )
        
        db.session.add(reg)
        db.session.commit()
        
        print(f"Registro salvo: ID={reg.id}, Nome={reg.nome_operador}, TMA={reg.tma}, TMR={reg.tmr}")
        
        return jsonify({
            "ok": True, 
            "message": "Registro salvo com sucesso",
            "registro_id": reg.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar registro: {str(e)}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@app.route("/api/registros/<int:user_id>", methods=["GET"])
def listar_registros(user_id):
    try:
        print(f"Buscando registros para user_id: {user_id}")
        
        # Verificar se o usuário existe
        user = User.query.get(user_id)
        if not user:
            print(f"Usuário {user_id} não encontrado")
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        regs = Registro.query.filter_by(user_id=user_id).all()
        print(f"Encontrados {len(regs)} registros")
        
        resultado = []
        for r in regs:
            reg_data = {
                "id": r.id,
                "nome_operador": r.nome_operador,
                "tma": round(r.tma, 2),
                "tmr": round(r.tmr, 2)
            }
            resultado.append(reg_data)
            print(f"Registro: {reg_data}")
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Erro ao listar registros: {str(e)}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@app.route("/api/registros/clear/<int:user_id>", methods=["DELETE"])
def deletar_registros(user_id):
    regs = Registro.query.filter_by(user_id=user_id).all()
    for r in regs:
        db.session.delete(r)
    db.session.commit()
    return jsonify({"ok": True})

@app.route("/api/reset", methods=["POST"])
def reset_db():
    db.drop_all()
    db.create_all()
    return jsonify({"ok": True})

@app.route("/api/reset-db", methods=["POST"])
def reset_database():
    """Reseta o banco de dados - CUIDADO: apaga todos os dados!"""
    try:
        # Remove todas as tabelas
        db.drop_all()
        # Recria todas as tabelas
        db.create_all()
        return jsonify({"ok": True, "message": "Banco de dados resetado com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/api/init-db", methods=["POST"])
def init_database():
    """Inicializa o banco de dados se não existir"""
    try:
        db.create_all()
        return jsonify({"ok": True, "message": "Banco de dados inicializado"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    """Lista todos os usuários (para debug) - REMOVER EM PRODUÇÃO"""
    try:
        users = User.query.all()
        return jsonify([{
            "id": u.id,
            "nome": u.nome,
            "total_registros": len(u.registros)
        } for u in users])
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/debug/database")
def debug_database():
    """Rota para visualizar todos os dados do banco - APENAS PARA DEBUG"""
    try:
        users = User.query.all()
        registros = Registro.query.all()
        
        html = "<h1>🗃️ Debug do Banco de Dados</h1>"
        
        html += f"<h2>👥 Usuários ({len(users)} total):</h2><ul>"
        for user in users:
            html += f"<li>ID: {user.id} | Nome: {user.nome} | Registros: {len(user.registros)}</li>"
        html += "</ul>"
        
        html += f"<h2>📊 Registros ({len(registros)} total):</h2><table border='1' style='border-collapse: collapse;'>"
        html += "<tr><th>ID</th><th>Operador</th><th>TMA</th><th>TMR</th><th>User ID</th></tr>"
        
        for reg in registros:
            html += f"<tr><td>{reg.id}</td><td>{reg.nome_operador}</td><td>{reg.tma}</td><td>{reg.tmr}</td><td>{reg.user_id}</td></tr>"
        
        html += '</table>'
        html += "<br><a href='/teste'>← Voltar para teste</a>"
        
        return html
        
    except Exception as e:
        return f"<h1>Erro ao acessar banco:</h1><p>{str(e)}</p>"

# Rota de health check para deploy
@app.route("/health")
def health_check():
    return jsonify({"status": "OK", "message": "Sistema TMA/TMR funcionando"})

# Rota de debug para Railway
@app.route("/debug")
def debug_info():
    import sys
    return jsonify({
        "status": "OK",
        "python_version": sys.version,
        "port": os.environ.get('PORT', 'não definida'),
        "database_url": "configurada" if os.environ.get('DATABASE_URL') else "não configurada",
        "flask_env": os.environ.get('FLASK_ENV', 'não definido'),
        "working_directory": os.getcwd(),
        "files": os.listdir('.')[:10]  # Primeiros 10 arquivos
    })

if __name__ == "__main__":
    print("🚀 Iniciando Sistema TMA/TMR...")
    
    try:
        # Configurar porta
        port = int(os.environ.get('PORT', 5000))
        print(f"📡 Porta configurada: {port}")
        
        # Criar diretório instance se não existir (para SQLite local)
        if not os.environ.get('DATABASE_URL'):
            os.makedirs('instance', exist_ok=True)
            print("📁 Diretório instance criado para SQLite")
        
        # Criar tabelas automaticamente se não existirem
        with app.app_context():
            try:
                db.create_all()
                print("✅ Banco de dados inicializado com sucesso")
            except Exception as db_error:
                print(f"⚠️ Aviso no banco de dados: {str(db_error)}")
        
        print(f"🌐 Servidor iniciando em 0.0.0.0:{port}")
        print("🔗 Acesse /health para verificar status")
        
        # Iniciar servidor
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Erro crítico ao iniciar aplicação: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Última tentativa - servidor básico
        try:
            port = int(os.environ.get('PORT', 5000))
            print(f"🔄 Tentativa de emergência na porta {port}")
            app.run(host='0.0.0.0', port=port, debug=False)
        except:
            print("💥 Falha total ao iniciar servidor")
            raise
