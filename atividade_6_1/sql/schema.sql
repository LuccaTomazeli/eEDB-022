CREATE TABLE IF NOT EXISTS clientes (
    id INT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telefone VARCHAR(30) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    segmento VARCHAR(100) NOT NULL,
    plano VARCHAR(50) NOT NULL,
    limite_credito DECIMAL(12, 2) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    data_cadastro DATE NOT NULL,
    ultima_compra DATE,
    total_compras INT NOT NULL DEFAULT 0,
    valor_total_compras DECIMAL(12, 2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bancos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    arquivo_origem VARCHAR(255) NOT NULL,
    linha_origem INT NOT NULL,
    dados JSON NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_bancos_origem (arquivo_origem, linha_origem)
);

CREATE TABLE IF NOT EXISTS empregados (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    arquivo_origem VARCHAR(255) NOT NULL,
    linha_origem INT NOT NULL,
    dados JSON NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_empregados_origem (arquivo_origem, linha_origem)
);

CREATE TABLE IF NOT EXISTS reclamacoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    arquivo_origem VARCHAR(255) NOT NULL,
    linha_origem INT NOT NULL,
    dados JSON NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_reclamacoes_origem (arquivo_origem, linha_origem)
);

CREATE TABLE IF NOT EXISTS dados_enriquecidos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    banco_id BIGINT NOT NULL,
    cnpj VARCHAR(30),
    nome_original VARCHAR(255),
    nome_normalizado VARCHAR(255) NOT NULL,
    segmento VARCHAR(50),
    empregado_match JSON NOT NULL,
    reclamacoes_resumo JSON NOT NULL,
    total_reclamacoes INT NOT NULL DEFAULT 0,
    indice_medio DECIMAL(12, 2),
    nota_media_empregados DECIMAL(5, 2),
    dados_tratados JSON NOT NULL,
    enriquecido_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_dados_enriquecidos_banco (banco_id)
);

INSERT INTO clientes (
    id, nome, email, telefone, cidade, estado, segmento, plano,
    limite_credito, ativo, data_cadastro, ultima_compra, total_compras,
    valor_total_compras
) VALUES
    (1, 'Joao Silva', 'joao.silva@email.com', '+55 11 98888-1001', 'Sao Paulo', 'SP', 'varejo', 'premium', 15000.00, TRUE, '2024-01-15', '2026-08-22', 18, 8420.50),
    (2, 'Maria Oliveira', 'maria.oliveira@email.com', '+55 21 97777-2002', 'Rio de Janeiro', 'RJ', 'servicos', 'essencial', 8000.00, TRUE, '2024-03-08', '2026-08-30', 11, 3975.90),
    (3, 'Guilherme Santos', 'guilherme.santos@email.com', '+55 31 96666-3003', 'Belo Horizonte', 'MG', 'tecnologia', 'premium', 25000.00, TRUE, '2023-11-21', '2026-09-02', 27, 18450.75),
    (4, 'Ana Costa', 'ana.costa@email.com', '+55 41 95555-4004', 'Curitiba', 'PR', 'varejo', 'basico', 4500.00, TRUE, '2025-02-10', '2026-07-18', 6, 1240.00),
    (5, 'Rafael Almeida', 'rafael.almeida@email.com', '+55 51 94444-5005', 'Porto Alegre', 'RS', 'industria', 'empresarial', 50000.00, FALSE, '2022-09-03', '2026-01-12', 42, 52890.30)
ON DUPLICATE KEY UPDATE
    nome = VALUES(nome),
    email = VALUES(email), telefone = VALUES(telefone), cidade = VALUES(cidade),
    estado = VALUES(estado), segmento = VALUES(segmento), plano = VALUES(plano),
    limite_credito = VALUES(limite_credito), ativo = VALUES(ativo),
    data_cadastro = VALUES(data_cadastro), ultima_compra = VALUES(ultima_compra),
    total_compras = VALUES(total_compras), valor_total_compras = VALUES(valor_total_compras);
