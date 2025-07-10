# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import hashlib
import os
from datetime import datetime, date

# Carregar variáveis de ambiente do arquivo .env se existir
try:
    from dotenv import load_dotenv
    if os.path.exists('.env'):
        load_dotenv()
        print("📋 Arquivo .env carregado")
except ImportError:
    print("⚠️ python-dotenv não instalado. Instale com: pip install python-dotenv")

# Configuração do Flask para trabalhar na raiz do projeto
app = Flask(__name__, static_folder='./', static_url_path='', template_folder='./')
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuração do banco de dados
database_url = os.environ.get('DATABASE_URL')

# Configuração para PostgreSQL local (pgAdmin)
if not database_url:
    # Configurações para PostgreSQL local - ajuste conforme sua configuração no pgAdmin
    pg_host = os.environ.get('POSTGRES_HOST', 'localhost')
    pg_port = os.environ.get('POSTGRES_PORT', '5432')
    pg_db = os.environ.get('POSTGRES_DB', 'tma_tmr_db')
    pg_user = os.environ.get('POSTGRES_USER', 'postgres')
    pg_password = os.environ.get('POSTGRES_PASSWORD', '')
    
    # Tentar PostgreSQL primeiro
    if pg_password:  # Só tentar se tiver senha configurada
        try:
            database_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
            print(f"📊 Tentando PostgreSQL: {pg_host}:{pg_port}/{pg_db}")
            
            # Teste rápido de conexão
            import psycopg2
            test_conn = psycopg2.connect(
                host=pg_host, port=pg_port, database=pg_db, 
                user=pg_user, password=pg_password
            )
            test_conn.close()
            print(f"✅ PostgreSQL conectado com sucesso!")
            
        except ImportError:
            print("⚠️ psycopg2 não instalado. Execute: pip install psycopg2-binary")
            database_url = None
        except Exception as e:
            print(f"⚠️ Erro ao conectar PostgreSQL: {e}")
            print(f"🔄 Alternativas:")
            print(f"   1. Verifique se PostgreSQL está rodando")
            print(f"   2. Confirme as credenciais no arquivo .env")
            print(f"   3. Teste a conexão no pgAdmin primeiro")
            database_url = None
    else:
        print("⚠️ Senha do PostgreSQL não configurada no .env")
        database_url = None

if database_url:
    # Para deploy (Railway/Render) - ajustar PostgreSQL URL se necessário
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"📊 Banco de dados configurado: PostgreSQL")
else:
    # Fallback para SQLite se não conseguir configurar PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/dados.db'
    print(f"📊 Fallback: Usando SQLite local (dados em instance/dados.db)")
    print(f"💡 Para usar PostgreSQL, configure o arquivo .env corretamente")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersegredo')
db = SQLAlchemy(app)

# Middleware para capturar erros não tratados
@app.errorhandler(500)
def handle_500_error(e):
    print(f"❌ ERRO 500 CAPTURADO: {str(e)}")
    import traceback
    traceback.print_exc()
    return jsonify({"erro": "Erro interno do servidor", "detalhes": str(e)}), 500

@app.errorhandler(404)
def handle_404_error(e):
    print(f"❌ ERRO 404: {str(e)}")
    return jsonify({"erro": "Recurso não encontrado"}), 404

@app.errorhandler(Exception)
def handle_generic_error(e):
    print(f"❌ ERRO GENÉRICO CAPTURADO: {str(e)}")
    import traceback
    traceback.print_exc()
    return jsonify({"erro": "Erro interno", "tipo": type(e).__name__, "mensagem": str(e)}), 500

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
    data_registro = db.Column(db.Date, nullable=False)
    numero_pdv = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def hash_senha(senha):
    try:
        if not senha:
            raise ValueError("Senha não pode estar vazia")
        return hashlib.sha256(str(senha).encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"❌ Erro ao fazer hash da senha: {e}")
        raise

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
    try:
        return render_template("teste.html")
    except Exception as e:
        print(f"❌ Erro ao renderizar teste.html: {e}")
        return f"Erro ao carregar teste.html: {str(e)}", 500

@app.route("/teste-postgresql")
def teste_postgresql_page():
    try:
        print("🧪 Acessando rota /teste-postgresql")
        return render_template("teste_postgresql.html")
    except Exception as e:
        print(f"❌ Erro ao renderizar teste_postgresql.html: {e}")
        return f"Erro ao carregar teste_postgresql.html: {str(e)}", 500

@app.route("/teste-postgresql-simples")
def teste_postgresql_simples():
    """Versão simples sem template para teste"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste PostgreSQL Simples</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>🧪 Teste PostgreSQL - Versão Simples</h1>
        <button onclick="testarConexao()">Testar Conexão</button>
        <div id="resultado"></div>
        
        <script>
        async function testarConexao() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                document.getElementById('resultado').innerHTML = 
                    '<p style="color: green;">✅ Servidor funcionando: ' + data.status + '</p>';
            } catch (error) {
                document.getElementById('resultado').innerHTML = 
                    '<p style="color: red;">❌ Erro: ' + error.message + '</p>';
            }
        }
        </script>
    </body>
    </html>
    """

@app.route("/debug/rotas")
def debug_rotas():
    """Lista todas as rotas registradas no Flask"""
    rotas = []
    for rule in app.url_map.iter_rules():
        rotas.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    
    html = "<h1>🔍 Debug - Rotas Registradas</h1>"
    html += f"<p>Total de rotas: {len(rotas)}</p>"
    html += "<table border='1' style='border-collapse: collapse;'>"
    html += "<tr><th>Rota</th><th>Métodos</th><th>Endpoint</th></tr>"
    
    for rota in sorted(rotas, key=lambda x: x['rule']):
        methods = ', '.join([m for m in rota['methods'] if m not in ['HEAD', 'OPTIONS']])
        html += f"<tr><td>{rota['rule']}</td><td>{methods}</td><td>{rota['endpoint']}</td></tr>"
    
    html += "</table>"
    return html

# --- API ---

@app.route("/api/usuarios", methods=["POST"])
def cadastrar_usuario():
    try:
        # Verificar se dados foram enviados
        data = request.json
        if not data:
            print("❌ Erro: Nenhum dado JSON recebido na criação de usuário")
            return jsonify({"erro": "Nenhum dado fornecido"}), 400
            
        print(f"📥 Criando usuário: {data}")
        
        nome = data.get('nome', '').strip()
        senha = data.get('senha', '')
        
        # Validações
        if not nome or not senha:
            print("❌ Erro: Nome ou senha não fornecidos")
            return jsonify({"erro": "Nome e senha são obrigatórios"}), 400
        
        if len(nome) < 3:
            print("❌ Erro: Nome muito curto")
            return jsonify({"erro": "Nome deve ter pelo menos 3 caracteres"}), 400
        
        if len(senha) < 4:
            print("❌ Erro: Senha muito curta")
            return jsonify({"erro": "Senha deve ter pelo menos 4 caracteres"}), 400
        
        # Verifica se usuário já existe (case-insensitive)
        existing_user = User.query.filter(db.func.lower(User.nome) == nome.lower()).first()
        if existing_user:
            print(f"⚠️ Usuário '{nome}' já existe")
            return jsonify({"erro": f"Usuário '{nome}' já existe"}), 400
        
        # Criar usuário
        user = User(nome=nome, senha_hash=hash_senha(senha))
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Usuário '{nome}' criado com sucesso! ID: {user.id}")
        return jsonify({"ok": True, "message": f"Usuário '{nome}' cadastrado com sucesso!", "user_id": user.id})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro crítico ao cadastrar usuário: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"erro": f"Erro ao cadastrar usuário: {str(e)}"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({"erro": "Dados não fornecidos"}), 400
            
        nome = data.get('nome', '').strip()
        senha = data.get('senha', '')
        
        if not nome or not senha:
            return jsonify({"erro": "Nome e senha são obrigatórios"}), 400
        
        user = User.query.filter_by(nome=nome).first()
        if user and user.senha_hash == hash_senha(senha):
            session['user_id'] = user.id
            return jsonify({"ok": True, "user_id": user.id, "nome": user.nome})
        
        return jsonify({"erro": "Usuário ou senha inválidos"}), 401
        
    except Exception as e:
        print(f"Erro na rota de login: {str(e)}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop('user_id', None)
    return jsonify({"ok": True})

@app.route("/api/registros", methods=["POST"])
def registrar_tempo():
    try:
        # Verificar se dados foram enviados
        data = request.json
        if not data:
            print("Erro: Nenhum dado JSON recebido")
            return jsonify({"erro": "Nenhum dado fornecido"}), 400
            
        print(f"📥 Dados recebidos: {data}")
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['user_id', 'nome_operador', 'tma', 'tmr', 'data_registro', 'numero_pdv']
        for campo in campos_obrigatorios:
            if campo not in data or data[campo] is None:
                print(f"Erro: Campo '{campo}' não fornecido")
                return jsonify({"erro": f"Campo '{campo}' é obrigatório"}), 400
        
        user_id = data.get('user_id')
        nome_operador = data.get('nome_operador', '').strip()
        numero_pdv = data.get('numero_pdv', '').strip()
        data_registro_str = data.get('data_registro', '').strip()
        
        # Validações específicas
        if not nome_operador:
            return jsonify({"erro": "Nome do operador não pode estar vazio"}), 400
            
        if not numero_pdv:
            return jsonify({"erro": "Número do PDV não pode estar vazio"}), 400
            
        # Validar e converter data
        try:
            if data_registro_str:
                data_registro = datetime.strptime(data_registro_str, '%Y-%m-%d').date()
            else:
                data_registro = date.today()  # Se não fornecida, usar hoje
        except ValueError:
            return jsonify({"erro": "Data inválida. Use o formato YYYY-MM-DD"}), 400
            
        # Verificar se o usuário existe
        user = User.query.get(user_id)
        if not user:
            print(f"❌ Usuário {user_id} não encontrado no banco")
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        print(f"✅ Usuário encontrado: {user.nome}")
        
        # Criar registro
        try:
            reg = Registro(
                nome_operador=nome_operador,
                tma=float(data['tma']),
                tmr=float(data['tmr']),
                data_registro=data_registro,
                numero_pdv=numero_pdv,
                user_id=int(user_id)
            )
            
            print(f"📊 Criando registro: Operador={nome_operador}, TMA={data['tma']}, TMR={data['tmr']}, Data={data_registro}, PDV={numero_pdv}")
            
            db.session.add(reg)
            db.session.commit()
            
            print(f"✅ Registro salvo com sucesso: ID={reg.id}")
            
            return jsonify({
                "ok": True, 
                "message": "Registro salvo com sucesso",
                "registro_id": reg.id,
                "dados": {
                    "nome_operador": reg.nome_operador,
                    "tma": reg.tma,
                    "tmr": reg.tmr
                }
            })
            
        except ValueError as ve:
            print(f"❌ Erro de conversão de valores: {ve}")
            return jsonify({"erro": f"Valores inválidos: {str(ve)}"}), 400
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro crítico ao salvar registro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"erro": f"Erro interno do servidor: {str(e)}"}), 500

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
                "tmr": round(r.tmr, 2),
                "data_registro": r.data_registro.strftime('%Y-%m-%d'),
                "numero_pdv": r.numero_pdv
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
                # Para PostgreSQL, garantir que as tabelas sejam criadas com encoding correto
                if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
                    print("🐘 Configurando tabelas PostgreSQL...")
                    db.create_all()
                    print("✅ Tabelas PostgreSQL criadas com sucesso")
                    
                    # Testar se consegue fazer uma query simples
                    test_user_count = User.query.count()
                    test_registro_count = Registro.query.count()
                    print(f"📊 Estado atual: {test_user_count} usuários, {test_registro_count} registros")
                    
                else:
                    db.create_all()
                    print("✅ Banco de dados inicializado com sucesso")
            except Exception as db_error:
                print(f"⚠️ Aviso no banco de dados: {str(db_error)}")
                # Tentar criar as tabelas uma por vez se houver erro
                try:
                    print("🔄 Tentando criar tabelas individualmente...")
                    db.create_all()
                    print("✅ Tabelas criadas com sucesso na segunda tentativa")
                except Exception as retry_error:
                    print(f"❌ Erro persistente: {str(retry_error)}")
                    print("🔄 Aplicação continuará, mas pode haver problemas com o banco")
        
        print(f"🌐 Servidor iniciando em 0.0.0.0:{port}")
        print("🔗 Acesse /health para verificar status")
        print("🧪 Acesse /teste-postgresql para testar PostgreSQL")
        print("📱 Acesse /login para usar a aplicação")
        
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
