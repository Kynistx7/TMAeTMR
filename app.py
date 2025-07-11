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
# Prioridade absoluta para Railway DATABASE_URL
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Railway/Produção - usar DATABASE_URL fornecida
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"🚂 Railway PostgreSQL detectado e configurado!")
    print(f"📊 Banco de dados: PostgreSQL (produção)")
    
elif os.environ.get('RAILWAY_ENVIRONMENT'):
    # Se estamos no Railway mas DATABASE_URL não existe (erro de configuração)
    print("❌ ERRO: Railway detectado mas DATABASE_URL não encontrada!")
    print("🔧 Solução: Adicione PostgreSQL ao projeto Railway")
    raise Exception("DATABASE_URL obrigatória no Railway")
    
else:
    # Desenvolvimento local - tentar PostgreSQL local ou SQLite fallback
    print("🏠 Ambiente de desenvolvimento local detectado")
    
    # Configurações para PostgreSQL local (desenvolvimento)
    pg_host = os.environ.get('POSTGRES_HOST', 'localhost')
    pg_port = os.environ.get('POSTGRES_PORT', '5432')
    pg_db = os.environ.get('POSTGRES_DB', 'tma_tmr_db')
    pg_user = os.environ.get('POSTGRES_USER', 'postgres')
    pg_password = os.environ.get('POSTGRES_PASSWORD', '')
    
    # Tentar PostgreSQL local primeiro
    if pg_password:
        try:
            database_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
            print(f"📊 Testando PostgreSQL local: {pg_host}:{pg_port}/{pg_db}")
            
            # Teste rápido de conexão
            import psycopg2
            test_conn = psycopg2.connect(
                host=pg_host, port=pg_port, database=pg_db, 
                user=pg_user, password=pg_password
            )
            test_conn.close()
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
            print(f"✅ PostgreSQL local conectado com sucesso!")
            
        except ImportError:
            print("⚠️ psycopg2 não instalado. Execute: pip install psycopg2-binary")
            print("🔄 Usando SQLite como fallback...")
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/dados.db'
            
        except Exception as e:
            print(f"⚠️ PostgreSQL local falhou: {e}")
            print("🔄 Usando SQLite como fallback...")
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/dados.db'
    else:
        print("⚠️ PostgreSQL local não configurado (sem senha)")
        print("🔄 Usando SQLite como fallback...")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/dados.db'

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
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
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
            
            # Debug: verificar is_admin
            print(f"🔍 DEBUG LOGIN - User: {user.nome}, ID: {user.id}, is_admin: {user.is_admin}")
            
            return jsonify({
                "ok": True, 
                "user_id": user.id, 
                "nome": user.nome,
                "is_admin": user.is_admin
            })
        
        return jsonify({"erro": "Usuário ou senha inválidos"}), 401
        
    except Exception as e:
        print(f"Erro na rota de login: {str(e)}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop('user_id', None)
    return jsonify({"ok": True})

def verificar_admin():
    """Verifica se o usuário atual é admin"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return False
        
        user = User.query.get(user_id)
        return user and user.is_admin
    except Exception as e:
        print(f"❌ Erro ao verificar admin: {e}")
        return False

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



@app.route("/admin")
def admin_dashboard():
    """Painel administrativo principal"""
    if not verificar_admin():
        return redirect(url_for('login_page'))
    return render_template("admin.html")

@app.route("/api/admin/stats")
def admin_stats():
    """Estatísticas gerais para o dashboard admin"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        # Estatísticas gerais
        total_usuarios = User.query.count()
        total_registros = Registro.query.count()
        
        # Calcular médias gerais
        from sqlalchemy import func
        medias = db.session.query(
            func.avg(Registro.tma).label('tma_medio'),
            func.avg(Registro.tmr).label('tmr_medio')
        ).first()
        
        tma_geral = round(float(medias.tma_medio), 2) if medias.tma_medio else 0
        tmr_geral = round(float(medias.tmr_medio), 2) if medias.tmr_medio else 0
        
        # Top usuários por registros
        usuarios_top = db.session.query(
            User.nome,
            func.count(Registro.id).label('total_registros')
        ).join(Registro).group_by(User.nome).order_by(
            func.count(Registro.id).desc()
        ).limit(10).all()
        
        return jsonify({
            "total_usuarios": total_usuarios,
            "total_registros": total_registros,
            "tma_geral": tma_geral,
            "tmr_geral": tmr_geral,
            "usuarios_top": [
                {
                    "nome": u.nome,
                    "total_registros": u.total_registros
                } for u in usuarios_top
            ]
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar estatísticas: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/graficos")
def admin_graficos():
    """Dados para gráficos de análise"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Gráfico 1: TMA/TMR por PDV
        dados_pdv = db.session.query(
            Registro.numero_pdv,
            func.avg(Registro.tma).label('tma_medio'),
            func.avg(Registro.tmr).label('tmr_medio'),
            func.count(Registro.id).label('total_registros')
        ).group_by(Registro.numero_pdv).all()
        
        # Gráfico 2: Evolução temporal (últimos 30 dias)
        data_limite = datetime.now().date() - timedelta(days=30)
        evolucao_temporal = db.session.query(
            Registro.data_registro,
            func.avg(Registro.tma).label('tma_medio'),
            func.avg(Registro.tmr).label('tmr_medio'),
            func.count(Registro.id).label('total_registros')
        ).filter(
            Registro.data_registro >= data_limite
        ).group_by(Registro.data_registro).order_by(Registro.data_registro).all()
        
        # Gráfico 3: Distribuição por operador
        dados_operador = db.session.query(
            Registro.nome_operador,
            func.avg(Registro.tma).label('tma_medio'),
            func.avg(Registro.tmr).label('tmr_medio'),
            func.count(Registro.id).label('total_registros')
        ).group_by(Registro.nome_operador).order_by(
            func.count(Registro.id).desc()
        ).limit(10).all()
        
        return jsonify({
            "pdv_data": [
                {
                    "pdv": d.numero_pdv,
                    "tma_medio": round(float(d.tma_medio), 2),
                    "tmr_medio": round(float(d.tmr_medio), 2),
                    "total_registros": d.total_registros
                } for d in dados_pdv
            ],
            "evolucao_temporal": [
                {
                    "data": d.data_registro.strftime('%Y-%m-%d'),
                    "tma_medio": round(float(d.tma_medio), 2),
                    "tmr_medio": round(float(d.tmr_medio), 2),
                    "total_registros": d.total_registros
                } for d in evolucao_temporal
            ],
            "operadores_data": [
                {
                    "operador": d.nome_operador,
                    "tma_medio": round(float(d.tma_medio), 2),
                    "tmr_medio": round(float(d.tmr_medio), 2),
                    "total_registros": d.total_registros
                } for d in dados_operador
            ]
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados para gráficos: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/top-tempos")
def admin_top_tempos():
    """Top 10 melhores e piores tempos de TMA e TMR"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        from sqlalchemy import func
        
        # Metas configuráveis (em segundos)
        META_TMA = 180.0  # 3 minutos
        META_TMR = 120.0  # 2 minutos
        
        # Top 10 melhores TMA (menores tempos)
        melhores_tma = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tma,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).order_by(Registro.tma.asc()).limit(10).all()
        
        # Top 10 piores TMA (apenas tempos ACIMA da meta)
        piores_tma = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tma,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).filter(Registro.tma > META_TMA).order_by(Registro.tma.desc()).limit(10).all()
        
        # Top 10 melhores TMR (menores tempos)
        melhores_tmr = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tmr,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).order_by(Registro.tmr.asc()).limit(10).all()
        
        # Top 10 piores TMR (apenas tempos ACIMA da meta)
        piores_tmr = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tmr,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).filter(Registro.tmr > META_TMR).order_by(Registro.tmr.desc()).limit(10).all()
        
        return jsonify({
            "meta_tma": META_TMA,
            "meta_tmr": META_TMR,
            "melhores_tma": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tma": r.tma,
                    "data_registro": r.data_registro.strftime('%d/%m/%Y'),
                    "usuario_nome": r.usuario_nome,
                    "dentro_meta": r.tma <= META_TMA
                } for r in melhores_tma
            ],
            "piores_tma": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tma": r.tma,
                    "data_registro": r.data_registro.strftime('%d/%m/%Y'),
                    "usuario_nome": r.usuario_nome,
                    "acima_meta": r.tma > META_TMA
                } for r in piores_tma
            ],
            "melhores_tmr": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tmr": r.tmr,
                    "data_registro": r.data_registro.strftime('%d/%m/%Y'),
                    "usuario_nome": r.usuario_nome,
                    "dentro_meta": r.tmr <= META_TMR
                } for r in melhores_tmr
            ],
            "piores_tmr": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tmr": r.tmr,
                    "data_registro": r.data_registro.strftime('%d/%m/%Y'),
                    "usuario_nome": r.usuario_nome,
                    "acima_meta": r.tmr > META_TMR
                } for r in piores_tmr
            ]
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar top tempos: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/top-tempos-diario")
def admin_top_tempos_diario():
    """Top 10 melhores e piores tempos de TMA e TMR do dia atual"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        from sqlalchemy import func
        from datetime import date
        
        # Metas configuráveis (em segundos)
        META_TMA = 180.0  # 3 minutos
        META_TMR = 120.0  # 2 minutos
        
        # Data de hoje
        hoje = date.today()
        
        # Top 10 melhores TMA do dia (menores tempos)
        melhores_tma_hoje = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tma,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).filter(
            Registro.data_registro == hoje
        ).order_by(Registro.tma.asc()).limit(10).all()
        
        # Top 10 piores TMA do dia (apenas tempos ACIMA da meta)
        piores_tma_hoje = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tma,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).filter(
            Registro.data_registro == hoje,
            Registro.tma > META_TMA
        ).order_by(Registro.tma.desc()).limit(10).all()
        
        # Top 10 melhores TMR do dia (menores tempos)
        melhores_tmr_hoje = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tmr,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).filter(
            Registro.data_registro == hoje
        ).order_by(Registro.tmr.asc()).limit(10).all()
        
        # Top 10 piores TMR do dia (apenas tempos ACIMA da meta)
        piores_tmr_hoje = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tmr,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).filter(
            Registro.data_registro == hoje,
            Registro.tmr > META_TMR
        ).order_by(Registro.tmr.desc()).limit(10).all()
        
        # Contar total de registros do dia
        total_registros_hoje = db.session.query(Registro).filter(
            Registro.data_registro == hoje
        ).count()
        
        return jsonify({
            "data_consulta": hoje.strftime('%d/%m/%Y'),
            "total_registros_hoje": total_registros_hoje,
            "meta_tma": META_TMA,
            "meta_tmr": META_TMR,
            "melhores_tma_hoje": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tma": r.tma,
                    "data_registro": r.data_registro.strftime('%d/%m/%Y'),
                    "usuario_nome": r.usuario_nome,
                    "dentro_meta": r.tma <= META_TMA
                } for r in melhores_tma_hoje
            ],
            "piores_tma_hoje": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tma": r.tma,
                    "data_registro": r.data_registro.strftime('%d/%m/%Y'),
                    "usuario_nome": r.usuario_nome,
                    "acima_meta": r.tma > META_TMA
                } for r in piores_tma_hoje
            ],
            "melhores_tmr_hoje": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tmr": r.tmr,
                    "data_registro": r.data_registro.strftime('%d/%m/%Y'),
                    "usuario_nome": r.usuario_nome,
                    "dentro_meta": r.tmr <= META_TMR
                } for r in melhores_tmr_hoje
            ],
            "piores_tmr_hoje": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tmr": r.tmr,
                    "data_registro": r.data_registro.strftime('%d/%m/%Y'),
                    "usuario_nome": r.usuario_nome,
                    "acima_meta": r.tmr > META_TMR
                } for r in piores_tmr_hoje
            ]
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar top tempos diário: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/usuarios")
def admin_usuarios():
    """Lista todos os usuários para o painel admin"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        usuarios = User.query.all()
        
        usuarios_data = []
        for user in usuarios:
            # Buscar registros do usuário
            registros_user = Registro.query.filter_by(user_id=user.id).all()
            
            # Preparar dados dos registros
            registros_data = []
            for registro in registros_user:
                registros_data.append({
                    "id": registro.id,
                    "data_registro": registro.data_registro.strftime("%d/%m/%Y"),
                    "nome_operador": registro.nome_operador,
                    "numero_pdv": registro.numero_pdv,
                    "tma": registro.tma,
                    "tmr": registro.tmr
                })
            
            usuarios_data.append({
                "id": user.id,
                "nome": user.nome,
                "is_admin": user.is_admin,
                "total_registros": len(registros_data),
                "registros": registros_data
            })
        
        return jsonify({
            "usuarios": usuarios_data,
            "total": len(usuarios_data)
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar usuários: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/registros")
def admin_registros():
    """Lista todos os registros para o painel admin"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        registros = Registro.query.order_by(Registro.data_registro.desc()).all()
        
        registros_data = []
        for registro in registros:
            registros_data.append({
                "id": registro.id,
                "nome_operador": registro.nome_operador,
                "tma": registro.tma,
                "tmr": registro.tmr,
                "data_registro": registro.data_registro.strftime("%d/%m/%Y"),
                "numero_pdv": registro.numero_pdv,
                "user_id": registro.user_id,
                "usuario_nome": registro.user.nome if registro.user else "N/A"
            })
        
        return jsonify({
            "registros": registros_data,
            "total": len(registros_data)
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar registros: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/usuarios/<int:user_id>", methods=["DELETE"])
def deletar_usuario_admin(user_id):
    """Deleta um usuário e todos seus registros (admin)"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Não permitir deletar outros admins
        if user.is_admin:
            return jsonify({"erro": "Não é possível deletar outros administradores"}), 403
        
        nome_usuario = user.nome
        
        # Deletar todos os registros do usuário primeiro
        Registro.query.filter_by(user_id=user_id).delete()
        
        # Deletar o usuário
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"ok": True, "message": f"Usuário '{nome_usuario}' deletado com sucesso"})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao deletar usuário: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/registros/<int:registro_id>", methods=["DELETE"])
def deletar_registro_admin(registro_id):
    """Deleta um registro específico (admin)"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        registro = Registro.query.get(registro_id)
        if not registro:
            return jsonify({"erro": "Registro não encontrado"}), 404
        
        db.session.delete(registro)
        db.session.commit()
        
        return jsonify({"ok": True, "message": "Registro deletado com sucesso"})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao deletar registro: {e}")
        return jsonify({"erro": str(e)}), 500

# Rota específica para healthcheck do Railway
@app.route("/health")
def health_check():
    """Endpoint de healthcheck para Railway"""
    try:
        # Informações básicas sempre disponíveis
        response_data = {
            "status": "healthy",
            "service": "TMA/TMR System",
            "timestamp": datetime.now().isoformat(),
            "environment": "railway" if os.environ.get('RAILWAY_ENVIRONMENT') else "local"
        }
        
        # Testar conexão com banco de dados apenas se configurado
        try:
            with app.app_context():
                # Teste simples de query
                db.session.execute(db.text("SELECT 1"))
                response_data["database"] = "connected"
                response_data["database_type"] = "postgresql" if "postgresql" in app.config['SQLALCHEMY_DATABASE_URI'] else "sqlite"
        except Exception as db_error:
            # Se banco falhar, ainda retorna healthy mas com aviso
            response_data["database"] = "disconnected"
            response_data["database_error"] = str(db_error)[:100]  # Limitar tamanho do erro
            
            # No Railway, erro de banco é crítico
            if os.environ.get('RAILWAY_ENVIRONMENT'):
                response_data["status"] = "unhealthy"
                return jsonify(response_data), 500
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)[:200],  # Limitar tamanho
            "timestamp": datetime.now().isoformat()
        }), 500

# Rota para diagnostico completo (apenas para desenvolvimento/debug)
@app.route("/debug")
def debug_info():
    """Endpoint de debug para diagnosticar problemas (remover em produção)"""
    if not os.environ.get('RAILWAY_ENVIRONMENT'):
        # Só permite debug em ambiente não-produção
        try:
            import platform
            
            # Informações de ambiente
            env_info = {
                "python_version": platform.python_version(),
                "flask_version": Flask.__version__,
                "environment_vars": {
                    "DATABASE_URL": "SET" if os.environ.get('DATABASE_URL') else "NOT_SET",
                    "RAILWAY_ENVIRONMENT": os.environ.get('RAILWAY_ENVIRONMENT', 'NOT_SET'),
                    "PORT": os.environ.get('PORT', 'NOT_SET'),
                    "POSTGRES_HOST": os.environ.get('POSTGRES_HOST', 'NOT_SET'),
                    "POSTGRES_PASSWORD": "SET" if os.environ.get('POSTGRES_PASSWORD') else "NOT_SET"
                },
                "database_config": {
                    "sqlalchemy_uri": app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT_CONFIGURED')[:50] + "...",
                    "uri_type": "postgresql" if "postgresql" in str(app.config.get('SQLALCHEMY_DATABASE_URI', '')) else "sqlite"
                }
            }
            
            # Testar conexão com banco
            try:
                with app.app_context():
                    db.session.execute(db.text("SELECT 1"))
                    env_info["database_connection"] = "SUCCESS"
                    env_info["tables"] = [table.name for table in db.metadata.tables.values()]
                    env_info["total_users"] = User.query.count()
                    env_info["total_registros"] = Registro.query.count()
            except Exception as db_error:
                env_info["database_connection"] = "FAILED"
                env_info["database_error"] = str(db_error)
            
            return jsonify(env_info)
            
        except Exception as e:
            return jsonify({"debug_error": str(e)}), 500
    else:
        return jsonify({"message": "Debug not available in production"}), 403

if __name__ == "__main__":
    print("🚀 Iniciando Sistema TMA/TMR...")
    
    try:
        # Porta para Railway ou local
        port = int(os.environ.get('PORT', 5000))
        
        # Para Railway, não criar diretório instance (usa PostgreSQL)
        # Para local, criar instance se não existir (para SQLite local)
        if not os.environ.get('DATABASE_URL') and not os.environ.get('RAILWAY_ENVIRONMENT'):
            os.makedirs('instance', exist_ok=True)
            print("📁 Diretório instance criado para SQLite local")
        
        # Criar tabelas automaticamente se não existirem
        with app.app_context():
            db.create_all()
            
            # Criar admin padrão se não existir (apenas em produção/Railway)
            if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL'):
                admin_exists = User.query.filter_by(nome='admin').first()
                if not admin_exists:
                    admin_user = User(
                        nome='admin',
                        senha_hash=hash_senha('admin123'),
                        is_admin=True
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    print("👑 Usuário admin criado: admin/admin123")
                else:
                    print("👑 Usuário admin já existe")
            
            print("✅ Banco de dados inicializado")
        
        # Detectar ambiente
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
        is_production = os.environ.get('DATABASE_URL') is not None
        
        if is_railway:
            print(f"🚂 Rodando no Railway na porta {port}")
            print("🌐 Acesse sua aplicação na URL fornecida pelo Railway")
        else:
            print(f"🌐 Servidor local rodando em http://localhost:{port}")
            print("📱 Acesse /login para usar a aplicação")
        
        # Configurações otimizadas para produção
        debug_mode = not (is_railway or is_production)
        
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=debug_mode,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Erro ao iniciar: {str(e)}")
        raise
