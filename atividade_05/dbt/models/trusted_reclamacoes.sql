SELECT DISTINCT
    "Ano" AS ano,
    "Trimestre" AS trimestre,
    LPAD(TRIM("CNPJ IF"), 8, '0') AS cnpj,
    "Instituição financeira" AS instituicao,
    "Quantidade total de reclamações" AS qtd_reclamacoes
FROM raw.reclamacoes
WHERE "CNPJ IF" IS NOT NULL AND TRIM("CNPJ IF") != ''

