# 📊 Sistema TMA e TMR

Sistema web para cálculo de Tempo Médio de Atendimento (TMA) e Tempo Médio por Item (TMR) para operadores.

## 🚀 Deploy na Web

### **Opção 1: Render.com (Recomendado)**

1. **Prepare os arquivos**:
   ```bash
   # Execute no Windows:
   deploy.bat
   
   # Ou no Linux/Mac:
   bash deploy.sh
   ```

2. **Suba para GitHub**:
   - Crie um novo repositório no GitHub
   - Faça upload de todos os arquivos

3. **Deploy no Render**:
   - Acesse [render.com](https://render.com)
   - Conecte sua conta GitHub
   - Clique "New" → "Web Service"
   - Selecione seu repositório
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --host 0.0.0.0 --port $PORT`
     - **Environment**: Python 3

4. **Aguarde o deploy** (2-5 minutos)

### **Opção 2: Railway.app**

1. Acesse [railway.app](https://railway.app)
2. Conecte GitHub
3. Selecione seu repositório
4. Deploy automático!

### **Opção 3: Vercel**

1. Acesse [vercel.com](https://vercel.com)
2. Conecte GitHub
3. Selecione repositório
4. Deploy automático

## 🛠️ Tecnologias

- **Backend**: Flask + SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Banco**: SQLite
- **Deploy**: Render/Railway/Vercel

## 📋 Funcionalidades

- ✅ Sistema de login/registro
- ✅ Cálculo automático de TMA e TMR
- ✅ Tabela de resultados com status das metas
- ✅ Interface responsiva
- ✅ Validações em tempo real
- ✅ Persistência de dados

## 🎯 Fórmulas

- **TMA**: (Tempo de Venda + Tempo de Recebimento) ÷ Quantidade de Cupons
- **TMR**: Tempo de Venda ÷ Quantidade de Itens

## 📱 Compatibilidade

- ✅ Desktop
- ✅ Tablet  
- ✅ Mobile

---

**Desenvolvido com ❤️ para otimização de operações comerciais**
