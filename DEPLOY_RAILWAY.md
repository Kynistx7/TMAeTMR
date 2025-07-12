# 🚂 GUIA COMPLETO DE DEPLOY NO RAILWAY

## 📋 Pré-requisitos
- ✅ Conta no GitHub
- ✅ Projeto no GitHub (este repositório)
- ✅ Conta no Railway (railway.app)

## 🚀 PASSO A PASSO DO DEPLOY

### 1️⃣ Acesse o Railway
1. Vá para https://railway.app
2. Faça login com sua conta GitHub
3. Clique em **"New Project"**

### 2️⃣ Conecte seu Repositório
1. Selecione **"Deploy from GitHub repo"**
2. Escolha o repositório **TMAeTMR**
3. Confirme a conexão

### 3️⃣ Adicione PostgreSQL
1. No dashboard do projeto, clique em **"+ Add Service"**
2. Selecione **"Database"** → **"PostgreSQL"**
3. Aguarde a criação da instância (1-2 minutos)

### 4️⃣ Configure Variáveis de Ambiente
No serviço da aplicação Flask:
1. Vá em **"Variables"** ou **"Settings"**
2. Adicione estas variáveis:

```env
SECRET_KEY=seu_secret_key_super_seguro_aqui_12345
RAILWAY_ENVIRONMENT=production
```

⚠️ **Importante**: A variável `DATABASE_URL` é criada automaticamente pelo Railway quando você adiciona PostgreSQL.

### 5️⃣ Deploy Automático
1. O Railway fará o deploy automaticamente
2. Aguarde o processo (5-10 minutos)
3. Verifique os logs em **"Deployments"**

### 6️⃣ Configuração Pós-Deploy
Após o deploy bem-sucedido:

1. **Usuário Admin Padrão**:
   - **Login**: `admin`
   - **Senha**: `admin123`
   - ⚠️ **IMPORTANTE**: Altere a senha imediatamente após o primeiro login!

2. **URL da Aplicação**:
   - Encontre a URL pública no dashboard do Railway
   - Acesse: `sua-url.railway.app`

### 7️⃣ Verificar Funcionamento
1. Acesse a URL pública
2. Teste o login admin
3. Verifique se o banco está funcionando
4. Teste criação de usuários e registros

## 🔧 Arquivos de Configuração Incluídos

- ✅ `railway.json` - Configuração específica do Railway
- ✅ `Procfile` - Comando de inicialização
- ✅ `requirements.txt` - Dependências Python
- ✅ `runtime.txt` - Versão do Python
- ✅ `init_railway.py` - Script de inicialização do banco

## 🚨 Solução de Problemas

### Erro: "DATABASE_URL não encontrada"
- Verifique se PostgreSQL foi adicionado ao projeto
- Aguarde alguns minutos após adicionar o PostgreSQL

### Erro: "Build failed"
- Verifique os logs de build no Railway
- Confirme se `requirements.txt` está correto

### Erro: "Health check failed"
- Verifique se a aplicação está rodando na porta correta (`$PORT`)
- Confirme se o endpoint `/health` está funcionando

### Deploy não inicia
- Verifique as variáveis de ambiente
- Confirme se `SECRET_KEY` está definida

## 📊 Monitoramento

Após o deploy:
- Monitor logs em tempo real no dashboard
- Verifique métricas de performance
- Configure alertas se necessário

## 🔄 Atualizações

Para atualizar a aplicação:
1. Faça push das mudanças para o GitHub
2. Railway fará redeploy automaticamente
3. Monitore os logs durante a atualização

---

## 💡 Dicas Importantes

1. **Backup**: Railway faz backup automático do PostgreSQL
2. **Logs**: Sempre monitore os logs após deploy
3. **Variáveis**: Mantenha `SECRET_KEY` segura
4. **Performance**: Monitor uso de recursos
5. **Segurança**: Altere senhas padrão imediatamente

✅ **Pronto! Sua aplicação TMA/TMR está no ar!** 🎉
