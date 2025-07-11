-- Script para criar novos usuários administradores
-- Execute este arquivo no PostgreSQL ou use os comandos individualmente

-- TEMPLATE: Substitua 'NOVO_LOGIN' e 'NOVA_SENHA' pelos valores desejados

-- Exemplo 1: Criar admin com login "supervisor" e senha "admin123"
INSERT INTO users (nome, senha, is_admin) 
VALUES ('supervisor', 'admin123', true);

-- Exemplo 2: Criar admin com login "gerente" e senha "senha456"
INSERT INTO users (nome, senha, is_admin) 
VALUES ('gerente', 'senha456', true);

-- Exemplo 3: Criar admin com login personalizado
-- INSERT INTO users (nome, senha, is_admin) 
-- VALUES ('SEU_LOGIN_AQUI', 'SUA_SENHA_AQUI', true);

-- Para promover um usuário existente a admin:
-- UPDATE users SET is_admin = true WHERE nome = 'nome_do_usuario';

-- Para remover privilégios de admin:
-- UPDATE users SET is_admin = false WHERE nome = 'nome_do_usuario';

-- Para verificar todos os admins atuais:
SELECT nome, is_admin FROM users WHERE is_admin = true;

-- Para verificar todos os usuários:
SELECT id, nome, is_admin, 
       (SELECT COUNT(*) FROM registros WHERE user_id = users.id) as total_registros
FROM users 
ORDER BY is_admin DESC, nome;
