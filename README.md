# Sistema TMA/TMR - Tempo Médio de Atendimento e Resposta

Sistema web para monitoramento e análise de tempos de atendimento (TMA) e resposta (TMR) em pontos de venda.

## 🚀 Features

- ✅ **Sistema de Login e Registro** - Autenticação segura de usuários
- ✅ **Registro de Tempos** - Interface para inserir dados de TMA e TMR
- ✅ **Dashboard Administrativo** - Painel completo com estatísticas e análises
- ✅ **Monitoramento de Desempenho** - Identificação automática de operadores que precisam de atenção
- ✅ **Top 10 Rankings** - Melhores e piores tempos (geral e diário)
- ✅ **Sistema de Metas** - Filtragem inteligente por metas configuráveis
- ✅ **Gráficos Interativos** - Visualização de dados com Chart.js
- ✅ **Design Responsivo** - Interface moderna com glassmorphism
- ✅ **Banco PostgreSQL** - Suporte completo para produção

## 🛠️ Tecnologias

### Backend
- **Python 3.11** - Linguagem principal
- **Flask** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados principal
- **SQLite** - Fallback para desenvolvimento local

### Frontend
- **HTML5/CSS3** - Interface moderna
- **JavaScript Vanilla** - Interatividade
- **Chart.js** - Gráficos e visualizações
- **Glassmorphism Design** - Estilo visual moderno

## 📊 Deploy no Railway

### 1. Preparação do Projeto

O projeto já está configurado para Railway com:
- ✅ `railway.json` - Configurações do Railway
- ✅ `Procfile` - Comando de inicialização
- ✅ `runtime.txt` - Versão do Python
- ✅ `requirements.txt` - Dependências Python

### 2. Deploy Automático

1. **Acesse** [railway.app](https://railway.app)
2. **Faça login** com GitHub/Google
3. **Clique em "New Project"**
4. **Selecione "Deploy from GitHub repo"**
5. **Conecte seu repositório**
6. **Railway detectará automaticamente** como projeto Python

### 3. Configurar Banco PostgreSQL

1. **No dashboard do Railway**, clique em **"+ New"**
2. **Selecione "Database" → "PostgreSQL"**
3. **Conecte o banco ao seu projeto**
4. **Railway gerará automaticamente** a `DATABASE_URL`

### 4. Variáveis de Ambiente (Opcional)

Se necessário, configure no Railway:
```bash
SECRET_KEY=sua_chave_secreta_super_forte
```

### 5. Acesso ao Sistema

Após o deploy:
- 🌐 **URL da aplicação**: Fornecida pelo Railway
- 👑 **Admin padrão**: `admin` / `admin123` (criado automaticamente)
- 📱 **Usuários**: Podem se registrar normalmente

## 🏃‍♂️ Desenvolvimento Local

### 1. Requisitos
```bash
Python 3.11+
PostgreSQL (opcional, usa SQLite como fallback)
```

### 2. Instalação
```bash
# Clone o repositório
git clone [seu-repo]
cd TMAeTMR

# Instale dependências
pip install -r requirements.txt

# Configure variáveis (opcional)
cp .env.example .env
# Edite .env com suas configurações

# Execute a aplicação
python app.py
```

### 3. Acesso Local
- 🌐 **URL**: http://localhost:5000
- 📱 **Login**: Crie uma conta ou use admin local

## 📱 Como Usar

### Para Usuários Comuns:
1. **Registre-se** em `/register`
2. **Faça login** em `/login`
3. **Registre tempos** em `/tempos`
4. **Visualize dados** no dashboard

### Para Administradores:
1. **Acesse** `/admin` após login
2. **Visualize estatísticas** gerais
3. **Analise Top 10** rankings
4. **Gerencie usuários** e dados
5. **Monitore gráficos** de performance

## 🎯 Sistema de Metas

- **Meta TMA**: 180 segundos (3 minutos)
- **Meta TMR**: 120 segundos (2 minutos)
- **Filtragem Inteligente**: Piores tempos só mostram valores acima da meta
- **Mensagens Motivacionais**: Celebra quando todos estão na meta

## 🔧 Estrutura do Projeto

```
TMAeTMR/
├── app.py              # Aplicação principal Flask
├── requirements.txt    # Dependências Python
├── railway.json       # Configuração Railway
├── Procfile           # Comando de inicialização
├── runtime.txt        # Versão Python
├── .env.example       # Exemplo de variáveis
├── css/               # Estilos CSS
│   ├── admin.css      # Estilos do painel admin
│   ├── login.css      # Estilos de login
│   └── ...
├── js/                # Scripts JavaScript
│   └── script.js      # Funcionalidades frontend
├── img/               # Imagens e recursos
├── *.html             # Templates HTML
└── instance/          # Banco SQLite local (desenvolvimento)
```

## 🔒 Segurança

- ✅ **Hashing de senhas** com SHA256
- ✅ **Sessões seguras** com Flask sessions
- ✅ **Validação de entrada** em todos os formulários
- ✅ **Proteção de rotas** administrativas
- ✅ **CORS configurado** adequadamente

## 📈 Funcionalidades Avançadas

### Dashboard Administrativo
- 📊 **Estatísticas gerais** (total usuários, registros, médias)
- 📈 **Gráficos interativos** (por PDV, evolução temporal, operadores)
- 🏆 **Rankings dinâmicos** (geral e diário)
- 👥 **Gestão de usuários** (visualizar, deletar)
- 🗃️ **Gestão de registros** (visualizar, deletar)

### Top 10 Inteligente
- 🥇 **Melhores tempos** (sempre visíveis)
- 🚨 **Piores tempos** (apenas acima da meta)
- 📅 **Filtros por período** (geral vs. diário)
- 🎯 **Indicadores visuais** (dentro/fora da meta)
- 🎉 **Mensagens motivacionais** (quando todos na meta)

## 🚀 Performance

- ⚡ **Backend otimizado** com SQLAlchemy
- 🔄 **Consultas eficientes** com índices adequados
- 📱 **Interface responsiva** para mobile
- 🎨 **CSS otimizado** com glassmorphism
- 📊 **Charts.js** para gráficos performáticos

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs no Railway Dashboard
2. Confirme que o banco PostgreSQL está conectado
3. Valide as variáveis de ambiente
4. Teste localmente primeiro

---

**Sistema TMA/TMR** - Desenvolvido para otimizar o monitoramento de performance operacional 🚀
