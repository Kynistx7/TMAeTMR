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

@app.route("/api/admin/chart-data")
def admin_chart_data():
    """Dados específicos para gráficos da aba relatórios"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Parâmetros de data
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        if not start_date or not end_date:
            return jsonify({"erro": "Parâmetros de data obrigatórios"}), 400
            
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Metas
        META_TMA = 92.0
        META_TMR = 6.0
        
        # 1. TMA e TMR médios por dia
        tma_por_dia = db.session.query(
            Registro.data_registro,
            func.avg(Registro.tma).label('tma_medio')
        ).filter(
            Registro.data_registro >= start_date,
            Registro.data_registro <= end_date
        ).group_by(Registro.data_registro).order_by(Registro.data_registro).all()
        
        tmr_por_dia = db.session.query(
            Registro.data_registro,
            func.avg(Registro.tmr).label('tmr_medio')
        ).filter(
            Registro.data_registro >= start_date,
            Registro.data_registro <= end_date
        ).group_by(Registro.data_registro).order_by(Registro.data_registro).all()
        
        # 2. Distribuição TMA (conformidade)
        tma_dentro_meta = db.session.query(func.count(Registro.id)).filter(
            Registro.data_registro >= start_date,
            Registro.data_registro <= end_date,
            Registro.tma <= META_TMA
        ).scalar() or 0
        
        tma_acima_meta = db.session.query(func.count(Registro.id)).filter(
            Registro.data_registro >= start_date,
            Registro.data_registro <= end_date,
            Registro.tma > META_TMA
        ).scalar() or 0
        
        # 3. Distribuição TMR (conformidade)
        tmr_dentro_meta = db.session.query(func.count(Registro.id)).filter(
            Registro.data_registro >= start_date,
            Registro.data_registro <= end_date,
            Registro.tmr <= META_TMR
        ).scalar() or 0
        
        tmr_acima_meta = db.session.query(func.count(Registro.id)).filter(
            Registro.data_registro >= start_date,
            Registro.data_registro <= end_date,
            Registro.tmr > META_TMR
        ).scalar() or 0
        
        # 4. Performance por usuário
        user_performance = db.session.query(
            User.nome.label('usuario'),
            func.avg(Registro.tma).label('tma_medio'),
            func.avg(Registro.tmr).label('tmr_medio'),
            func.count(Registro.id).label('total_registros')
        ).join(Registro).filter(
            Registro.data_registro >= start_date,
            Registro.data_registro <= end_date
        ).group_by(User.id, User.nome).order_by(func.count(Registro.id).desc()).all()
        
        # 5. Estatísticas resumo
        total_registros = db.session.query(func.count(Registro.id)).filter(
            Registro.data_registro >= start_date,
            Registro.data_registro <= end_date
        ).scalar() or 0
        
        if total_registros > 0:
            tma_medio_geral = db.session.query(func.avg(Registro.tma)).filter(
                Registro.data_registro >= start_date,
                Registro.data_registro <= end_date
            ).scalar() or 0
            
            tmr_medio_geral = db.session.query(func.avg(Registro.tmr)).filter(
                Registro.data_registro >= start_date,
                Registro.data_registro <= end_date
            ).scalar() or 0
            
            conformidade_tma = round((tma_dentro_meta / total_registros) * 100, 1)
            conformidade_tmr = round((tmr_dentro_meta / total_registros) * 100, 1)
            
            usuarios_ativos = db.session.query(func.count(func.distinct(Registro.user_id))).filter(
                Registro.data_registro >= start_date,
                Registro.data_registro <= end_date
            ).scalar() or 0
        else:
            tma_medio_geral = tmr_medio_geral = 0
            conformidade_tma = conformidade_tmr = 0
            usuarios_ativos = 0
        
        return jsonify({
            "tma_por_dia": [
                {
                    "data": d.data_registro.strftime('%Y-%m-%d'),
                    "tma_medio": round(float(d.tma_medio), 1)
                } for d in tma_por_dia
            ],
            "tmr_por_dia": [
                {
                    "data": d.data_registro.strftime('%Y-%m-%d'),
                    "tmr_medio": round(float(d.tmr_medio), 1)
                } for d in tmr_por_dia
            ],
            "tma_distribution": {
                "dentro_meta": tma_dentro_meta,
                "acima_meta": tma_acima_meta
            },
            "tmr_distribution": {
                "dentro_meta": tmr_dentro_meta,
                "acima_meta": tmr_acima_meta
            },
            "user_performance": [
                {
                    "usuario": d.usuario,
                    "tma_medio": round(float(d.tma_medio), 1),
                    "tmr_medio": round(float(d.tmr_medio), 1),
                    "total_registros": d.total_registros
                } for d in user_performance
            ],
            "stats_summary": {
                "total_registros": total_registros,
                "tma_medio": round(float(tma_medio_geral), 1),
                "tmr_medio": round(float(tmr_medio_geral), 1),
                "conformidade_tma": conformidade_tma,
                "conformidade_tmr": conformidade_tmr,
                "usuarios_ativos": usuarios_ativos
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados dos gráficos: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/usuarios")
def admin_usuarios():
    """Lista usuários para o painel admin"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        from sqlalchemy import func
        
        usuarios = db.session.query(
            User.id,
            User.nome,
            User.is_admin,
            func.count(Registro.id).label('total_registros')
        ).outerjoin(Registro).group_by(User.id, User.nome, User.is_admin).all()
        
        return jsonify({
            "usuarios": [
                {
                    "id": u.id,
                    "nome": u.nome,
                    "is_admin": u.is_admin,
                    "total_registros": u.total_registros
                } for u in usuarios
            ]
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar usuários: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/usuarios/<int:user_id>", methods=["DELETE"])
def admin_delete_user(user_id):
    """Deletar usuário"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        if user.is_admin:
            return jsonify({"erro": "Não é possível deletar um administrador"}), 400
        
        # Deletar registros do usuário primeiro
        Registro.query.filter_by(user_id=user_id).delete()
        
        # Deletar o usuário
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": f"Usuário '{user.nome}' deletado com sucesso"})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao deletar usuário: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/registros/<int:record_id>", methods=["DELETE"])
def admin_delete_record(record_id):
    """Deletar registro específico"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        record = Registro.query.get(record_id)
        if not record:
            return jsonify({"erro": "Registro não encontrado"}), 404
        
        # Deletar o registro
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({"message": "Registro deletado com sucesso"})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao deletar registro: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/top-tempos")
def admin_top_tempos():
    """Top 10 melhores e piores tempos de TMA e TMR"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        from sqlalchemy import func
        
        # Metas configuráveis (em segundos)
        META_TMA = 92.0   # 1:32 (1 minuto e 32 segundos)
        META_TMR = 6.0    # 6 segundos
        
        # Top 10 melhores TMA (apenas tempos DENTRO da meta)
        melhores_tma = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tma,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).filter(Registro.tma <= META_TMA).order_by(Registro.tma.asc()).limit(10).all()
        
        # Top 10 piores TMA (apenas tempos ACIMA da meta)
        piores_tma = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tma,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).filter(Registro.tma > META_TMA).order_by(Registro.tma.desc()).limit(10).all()
        
        # Top 10 melhores TMR (apenas tempos DENTRO da meta)
        melhores_tmr = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tmr,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).filter(Registro.tmr <= META_TMR).order_by(Registro.tmr.asc()).limit(10).all()
        
        # Top 10 piores TMR (apenas tempos ACIMA da meta)
        piores_tmr = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tmr,
            Registro.data_registro,
            User.nome.label('usuario_nome')
        ).join(User).filter(Registro.tmr > META_TMR).order_by(Registro.tmr.desc()).limit(10).all()
        
        return jsonify({
            "melhores_tma": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tma": round(float(r.tma), 2),
                    "data_registro": r.data_registro.strftime('%Y-%m-%d'),
                    "usuario_nome": r.usuario_nome
                } for r in melhores_tma
            ],
            "piores_tma": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tma": round(float(r.tma), 2),
                    "data_registro": r.data_registro.strftime('%Y-%m-%d'),
                    "usuario_nome": r.usuario_nome
                } for r in piores_tma
            ],
            "melhores_tmr": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tmr": round(float(r.tmr), 2),
                    "data_registro": r.data_registro.strftime('%Y-%m-%d'),
                    "usuario_nome": r.usuario_nome
                } for r in melhores_tmr
            ],
            "piores_tmr": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tmr": round(float(r.tmr), 2),
                    "data_registro": r.data_registro.strftime('%Y-%m-%d'),
                    "usuario_nome": r.usuario_nome
                } for r in piores_tmr
            ]
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar top tempos: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/admin/top-tempos-diario")
def admin_top_tempos_diario():
    """Top tempos do dia ou data específica"""
    if not verificar_admin():
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        from datetime import datetime, date
        
        # Verificar se foi passada uma data específica
        data_param = request.args.get('data')
        if data_param:
            data_filtro = datetime.strptime(data_param, '%Y-%m-%d').date()
        else:
            data_filtro = date.today()
        
        META_TMA = 92.0
        META_TMR = 6.0
        
        # Contar registros da data
        total_registros_hoje = Registro.query.filter_by(data_registro=data_filtro).count()
        
        # Melhores TMA do dia
        melhores_tma_hoje = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tma,
            User.nome.label('usuario_nome')
        ).join(User).filter(
            Registro.data_registro == data_filtro,
            Registro.tma <= META_TMA
        ).order_by(Registro.tma.asc()).limit(10).all()
        
        # Piores TMA do dia
        piores_tma_hoje = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tma,
            User.nome.label('usuario_nome')
        ).join(User).filter(
            Registro.data_registro == data_filtro,
            Registro.tma > META_TMA
        ).order_by(Registro.tma.desc()).limit(10).all()
        
        # Melhores TMR do dia
        melhores_tmr_hoje = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tmr,
            User.nome.label('usuario_nome')
        ).join(User).filter(
            Registro.data_registro == data_filtro,
            Registro.tmr <= META_TMR
        ).order_by(Registro.tmr.asc()).limit(10).all()
        
        # Piores TMR do dia
        piores_tmr_hoje = db.session.query(
            Registro.nome_operador,
            Registro.numero_pdv,
            Registro.tmr,
            User.nome.label('usuario_nome')
        ).join(User).filter(
            Registro.data_registro == data_filtro,
            Registro.tmr > META_TMR
        ).order_by(Registro.tmr.desc()).limit(10).all()
        
        return jsonify({
            "total_registros_hoje": total_registros_hoje,
            "melhores_tma_hoje": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tma": round(float(r.tma), 2),
                    "usuario_nome": r.usuario_nome
                } for r in melhores_tma_hoje
            ],
            "piores_tma_hoje": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tma": round(float(r.tma), 2),
                    "usuario_nome": r.usuario_nome
                } for r in piores_tma_hoje
            ],
            "melhores_tmr_hoje": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tmr": round(float(r.tmr), 2),
                    "usuario_nome": r.usuario_nome
                } for r in melhores_tmr_hoje
            ],
            "piores_tmr_hoje": [
                {
                    "nome_operador": r.nome_operador,
                    "numero_pdv": r.numero_pdv,
                    "tmr": round(float(r.tmr), 2),
                    "usuario_nome": r.usuario_nome
                } for r in piores_tmr_hoje
            ]
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar top tempos diário: {e}")
        return jsonify({"erro": str(e)}), 500

# Rota específica para healthcheck do Railway
@app.route("/health") 
def health_check():
    """Endpoint simples de healthcheck"""
    return {"status": "ok"}, 200

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

# Inicialização automática do banco (Railway)
def init_database_tables():
    """Inicializa tabelas automaticamente se necessário"""
    try:
        print("🔧 Verificando e inicializando banco de dados...")
        with app.app_context():
            # Sempre criar as tabelas (safe - não apaga dados existentes)
            db.create_all()
            print("✅ Tabelas verificadas/criadas")
            
            # Verificar se existe admin
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                print("👤 Criando usuário admin...")
                admin = User(
                    nome='admin',
                    senha_hash=hash_senha('admin123'),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin criado: login=admin, senha=admin123")
            else:
                print("✅ Usuário admin já existe")
                
    except Exception as e:
        print(f"⚠️ Erro na inicialização: {e}")
        # Não falhar o app por causa disso

# SEMPRE inicializar no Railway
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL'):
    print("🚂 Ambiente Railway detectado - inicializando...")
    init_database_tables()

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
