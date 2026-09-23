CREATE TABLE IF NOT EXISTS banco_enquadramento (
    cnpj VARCHAR(32) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    segmento VARCHAR(20),
    nome_normalizado VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_banco_nome_normalizado
    ON banco_enquadramento (nome_normalizado);