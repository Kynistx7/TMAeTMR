-- Script para criar usuário admin no PostgreSQL
-- Execute este script no pgAdmin ou psql

-- Adicionar coluna is_admin se não existir
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Inserir usuário admin (ou atualizar se já existir)
INSERT INTO "user" (nome, senha_hash, is_admin) 
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', TRUE)
ON CONFLICT (nome) 
DO UPDATE SET is_admin = TRUE, senha_hash = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9';

-- Verificar se foi criado
SELECT id, nome, is_admin FROM "user" WHERE is_admin = TRUE;

-- Informações do admin criado
SELECT 'Usuario: admin | Senha: admin123 | URL: http://localhost:5000/admin' as info;
