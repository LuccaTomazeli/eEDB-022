CREATE TABLE clientes (
    id INT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);

INSERT INTO clientes (id, nome, email) VALUES
    (1, 'Joao', 'joao@email.com'),
    (2, 'Maria', 'maria@email.com'),
    (3, 'Guilherme', 'guilherme@email.com')
ON DUPLICATE KEY UPDATE
    nome = VALUES(nome),
    email = VALUES(email);
