# 🚂 GUIA COMPLETO DE DEPLOY NO RAILWAY

## 📋 Pré-requisitos
- ✅ Conta no GitHub
- ✅ Projeto no GitHub (este repositório)
- ✅ Conta no Railway (railway.app)

## 🚀 PASSO A PASSO DO DEPLOY

### 1️⃣ Preparar o Repositório GitHub

```bash
# Se ainda não está no GitHub, faça:
git init
git add .
git commit -m "Projeto TMA/TMR pronto para deploy"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/TMAeTMR.git
git push -u origin main
```

### 2️⃣ Criar Projeto no Railway

1. **Acesse**: https://railway.app
2. **Clique em "Login"** e conecte com GitHub
3. **Clique em "New Project"**
4. **Selecione "Deploy from GitHub repo"**
5. **Escolha o repositório "TMAeTMR"**
6. **Railway detectará automaticamente** que é um projeto Python Flask

### 3️⃣ Adicionar Banco PostgreSQL

1. **No dashboard do projeto**, clique no botão **"+ New"**
2. **Selecione "Database"**
3. **Clique em "Add PostgreSQL"**
4. **Aguarde a criação** (1-2 minutos)
5. **PostgreSQL será conectado automaticamente** ao seu projeto

### 4️⃣ Configurar Variáveis de Ambiente (Opcional)

1. **Clique no serviço** da sua aplicação (não no banco)
2. **Vá na aba "Variables"**
3. **Adicione se necessário**:
   ```
   SECRET_KEY=sua_chave_super_secreta_aqui_123456789
   ```

### 5️⃣ Deploy Automático

- ✅ **Railway fará o deploy automaticamente**
- ✅ **Detectará Python 3.11** (pelo runtime.txt)
- ✅ **Instalará dependências** (pelo requirements.txt)
- ✅ **Executará** `python app.py` (pelo Procfile)
- ✅ **Conectará ao PostgreSQL** automaticamente

### 6️⃣ Verificar Deploy

1. **Aguarde** o processo de build (2-5 minutos)
2. **Clique na URL** gerada pelo Railway (algo como: xxx.railway.app)
3. **Teste o acesso** à aplicação

## 🔧 RESOLUÇÃO DE PROBLEMAS

### ❌ Erro de Build
```bash
# Verifique se os arquivos estão corretos:
requirements.txt ✅
Procfile ✅
runtime.txt ✅
railway.json ✅
app.py ✅
```

### ❌ Erro de Banco
- Certifique-se que PostgreSQL foi adicionado ao projeto
- Railway conecta automaticamente via DATABASE_URL

### ❌ Erro 500
- Verifique os logs no Railway Dashboard
- Clique em "View Logs" para ver detalhes

## 🎯 ACESSO APÓS DEPLOY

### 👑 Admin Padrão
- **Usuário**: `admin`
- **Senha**: `admin123`
- **URL**: `sua-url-railway.app/admin`

### 📱 Usuários Normais
- **Registro**: `sua-url-railway.app/register`
- **Login**: `sua-url-railway.app/login`
- **Sistema**: `sua-url-railway.app/tempos`

## 🔄 ATUALIZAÇÕES

Para atualizar o sistema:
```bash
git add .
git commit -m "Atualização do sistema"
git push origin main
```
**Railway fará re-deploy automaticamente!**

## 📊 MONITORAMENTO

No Railway Dashboard você pode:
- 📈 **Ver logs** em tempo real
- 📊 **Monitorar recursos** (CPU, RAM)
- 🔧 **Gerenciar variáveis** de ambiente
- 🗄️ **Acessar banco** PostgreSQL
- 📱 **Ver métricas** de uso

## 💡 DICAS IMPORTANTES

1. **Primeiro deploy** pode demorar mais (5-10 min)
2. **Deploys subsequentes** são mais rápidos (2-3 min)
3. **URL personalizada** pode ser configurada no Railway
4. **Domínio próprio** pode ser conectado (plano pago)
5. **Backup do banco** é feito automaticamente
6. **SSL/HTTPS** é configurado automaticamente

## 🏆 SUCESSO!

Se tudo deu certo, você terá:
- ✅ **Sistema TMA/TMR** rodando na nuvem
- ✅ **Banco PostgreSQL** configurado
- ✅ **SSL/HTTPS** ativo
- ✅ **Admin criado** automaticamente
- ✅ **URL pública** para acessar
- ✅ **Deploy automático** a cada push

---

**Pronto para usar!** 🚀
Compartilhe a URL com sua equipe e comece a monitorar os tempos TMA/TMR!
