# 🚀 Deploy no Render - Sistema TMA/TMR

## ✅ Correções Aplicadas para Deploy

### Problemas Resolvidos:
- ✅ **"python: não pode abrir arquivo"** - App.py movido para raiz
- ✅ **Procfile corrigido** - comando simplificado
- ✅ **Configuração de banco** - PostgreSQL para deploy
- ✅ **Variáveis de ambiente** - SECRET_KEY e DATABASE_URL
- ✅ **Health check** - rota `/health` adicionada

## 📋 Passo a Passo Completo

### 1. **Preparar o Repositório GitHub**

1. Acesse: https://github.com
2. Crie uma conta (se não tiver)
3. Clique em "New repository"
4. Nome: `projeto-tma-tmr`
5. Deixe público
6. Clique "Create repository"

### 2. **Subir o código para o GitHub**

Execute no PowerShell na pasta do projeto:

```powershell
# Inicializar git (se não foi feito ainda)
git init

# Adicionar todos os arquivos
git add .

# Fazer commit
git commit -m "Deploy: app.py na raiz + correções"

# Adicionar origem remota (substitua SEU_USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU_USUARIO/projeto-tma-tmr.git

# Enviar para o GitHub
git push -u origin main
```

### 3. **Deploy no Render**

1. **Acesse:** https://render.com
2. **Clique** "Get Started" e crie uma conta
3. **Conecte** sua conta GitHub
4. **Clique** "New" → "Web Service"
5. **Selecione** seu repositório `projeto-tma-tmr`
6. **Configure:**
   - **Name**: `projeto-tma-tmr`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### 4. **Variáveis de Ambiente (IMPORTANTE!)**

No painel do Render, adicione estas variáveis:

```
SECRET_KEY = sua_chave_secreta_123456
FLASK_ENV = production
```

### 5. **Configurar Banco PostgreSQL (Recomendado)**

1. **No Render**, clique "New" → "PostgreSQL"
2. **Nome**: `tma-tmr-database`
3. **Copie** a `DATABASE_URL` gerada
4. **Adicione** como variável de ambiente no Web Service:
```
DATABASE_URL = postgresql://[URL_FORNECIDA_PELO_RENDER]
```

### 6. **Deploy e Teste**

1. **Clique** "Create Web Service"
2. **Aguarde** o build (3-5 minutos)
3. **Acesse** seu site: `https://projeto-tma-tmr.onrender.com`

### 7. **URLs para Testar:**

```
https://seu-app.onrender.com/health ← Health check
https://seu-app.onrender.com/login ← Página de login
https://seu-app.onrender.com/teste ← Página de teste
https://seu-app.onrender.com/debug/database ← Ver dados do banco
```

## 🔧 Resolução de Problemas

### ✅ "python: não pode abrir arquivo" - RESOLVIDO
- App.py agora está na raiz do projeto
- Procfile atualizado para `gunicorn app:app`

### Database Errors
- **Certifique-se** de ter criado o PostgreSQL no Render
- **Verifique** se `DATABASE_URL` está configurada
- **Para SQLite local**: remova `DATABASE_URL` das variáveis

### Build Failures
- **Confirme** que `requirements.txt` está na raiz
- **Verifique** se todas as dependências estão listadas

## 🎯 Sucesso!

Seu sistema TMA/TMR estará online e funcionando! 🎉

⚠️ **Importante**: O plano gratuito do Render "hiberna" após 15 min sem uso. O primeiro acesso após hibernação pode demorar ~30 segundos.
