# Deploy no Render - Guia Passo a Passo

## 1. Preparar o Repositório GitHub

1. Acesse: https://github.com
2. Crie uma conta (se não tiver)
3. Clique em "New repository"
4. Nome: `projeto-tma-tmr`
5. Deixe público
6. Clique "Create repository"

## 2. Subir o código para o GitHub

Execute no PowerShell na pasta do projeto:

```powershell
# Inicializar git (se não foi feito ainda)
git init

# Adicionar todos os arquivos
git add .

# Fazer commit
git commit -m "Primeiro commit - Sistema TMA/TMR"

# Adicionar origem remota (substitua SEU_USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU_USUARIO/projeto-tma-tmr.git

# Enviar para o GitHub
git push -u origin main
```

## 3. Deploy no Render

1. Acesse: https://render.com
2. Clique "Get Started" e crie uma conta
3. Conecte sua conta GitHub
4. Clique "New" → "Web Service"
5. Selecione seu repositório `projeto-tma-tmr`
6. Configure:
   - **Name**: `projeto-tma-tmr`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn app:app --host 0.0.0.0 --port $PORT`
7. Clique "Create Web Service"

## 4. Pronto!

Seu site estará disponível em: `https://projeto-tma-tmr.onrender.com`

⚠️ **Importante**: O plano gratuito do Render "hiberna" após 15 min sem uso. O primeiro acesso após hibernação pode demorar ~30 segundos.
