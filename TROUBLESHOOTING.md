# 🚨 TROUBLESHOOTING - RAILWAY DEPLOY

## ❌ ERRO: "Healthcheck failed!"

### 🔍 CAUSA MAIS COMUM
O Railway não consegue acessar a rota de healthcheck `/health` ou ela está retornando erro.

### ✅ SOLUÇÕES IMPLEMENTADAS

#### 1. **Nova Rota de Healthcheck**
```python
@app.route("/health")
def health_check():
    # Testa conexão com banco e retorna status
```
- ✅ Rota específica `/health` criada
- ✅ Testa conexão com banco de dados
- ✅ Retorna JSON com status detalhado

#### 2. **Configurações Otimizadas**
```json
{
  "healthcheckPath": "/health",
  "healthcheckTimeout": 300,
  "startCommand": "gunicorn ..."
}
```
- ✅ Timeout aumentado para 300s (5 minutos)
- ✅ Usando Gunicorn em vez de Flask development server
- ✅ Workers configurados para produção

#### 3. **Gunicorn para Produção**
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
```
- ✅ Servidor WSGI robusto
- ✅ 2 workers para performance
- ✅ Timeout de 120s por request

## 🛠️ PASSOS PARA RESOLVER

### 1. **Re-deploy com Novas Configurações**
```bash
git add .
git commit -m "Fix: Healthcheck e configurações Railway"
git push origin main
```

### 2. **Verificar Logs no Railway**
1. Acesse Railway Dashboard
2. Clique no seu projeto
3. Vá em "Deployments"
4. Clique no deploy mais recente
5. Veja "Build Logs" e "Deploy Logs"

### 3. **Testar Healthcheck Manualmente**
Após deploy, acesse:
```
https://sua-url-railway.app/health
```
Deve retornar:
```json
{
  "status": "healthy",
  "service": "TMA/TMR System",
  "timestamp": "2025-07-11T...",
  "database": "connected"
}
```

### 4. **Debug (se necessário)**
Em caso de problemas, temporariamente acesse:
```
https://sua-url-railway.app/debug
```
(Só funciona fora de produção)

## 🔧 OUTROS ERROS COMUNS

### ❌ **Database Connection Error**
**Solução**: Verificar se PostgreSQL foi adicionado ao projeto
```bash
# No Railway Dashboard:
1. Clique em "+ New"
2. Selecione "Database" > "PostgreSQL"
3. Aguarde conexão automática
```

### ❌ **Module Not Found**
**Solução**: Verificar requirements.txt
```bash
# Deve conter:
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
...
```

### ❌ **Port Binding Error**
**Solução**: Usar `$PORT` do Railway
```python
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

### ❌ **Import Errors**
**Solução**: Verificar estrutura do projeto
```
TMAeTMR/
├── app.py          ✅ Arquivo principal
├── requirements.txt ✅ Dependências
├── Procfile        ✅ Comando start
├── runtime.txt     ✅ Python version
└── railway.json    ✅ Configurações
```

## 📊 MONITORAMENTO

### ✅ **Deploy Bem-sucedido**
Você deve ver nos logs:
```
✅ Build completed
✅ Deployment successful
✅ Health check passed
🌐 Application available at: xxx.railway.app
```

### ✅ **Aplicação Funcionando**
Teste estas URLs:
```
https://sua-url.railway.app/health    → Status da aplicação
https://sua-url.railway.app/login     → Página de login
https://sua-url.railway.app/admin     → Painel admin
```

### ✅ **Admin Criado Automaticamente**
```
Usuário: admin
Senha: admin123
```

## 🚀 PRÓXIMOS PASSOS

1. **Faça o push** das correções
2. **Aguarde o re-deploy** (2-5 minutos)
3. **Teste o healthcheck** na URL
4. **Acesse a aplicação** e faça login
5. **Sucesso!** 🎉

---

## 📞 **Se Ainda Não Funcionar**

1. **Copie os logs** do Railway e me envie
2. **Teste localmente** primeiro: `python app.py`
3. **Verifique** se todos os arquivos foram commitados
4. **Confirme** que PostgreSQL está conectado

**O sistema está otimizado e deve funcionar!** 🚀
