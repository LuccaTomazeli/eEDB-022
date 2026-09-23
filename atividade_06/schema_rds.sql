CREATE TABLE IF NOT EXISTS ingestao_raw (
    id BIGSERIAL PRIMARY KEY,
    bucket_origem TEXT NOT NULL,
    chave_objeto TEXT NOT NULL,
    payload TEXT NOT NULL,
    recebido_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ingestao_raw_chave_objeto
    ON ingestao_raw (chave_objeto);
