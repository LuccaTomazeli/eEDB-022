SELECT DISTINCT
    LPAD(CAST(b."CNPJ" AS TEXT), 8, '0') AS cnpj,
    COALESCE(d.nome, b."Nome") AS nome_completo,
    UPPER(TRIM(SPLIT_PART(b."Nome", '-', 1))) AS nome_busca,
    b."Segmento" AS segmento
FROM raw.bancos b
LEFT JOIN raw.depara_bcb d ON LPAD(CAST(b."CNPJ" AS TEXT), 8, '0') = d.cnpj
WHERE b."CNPJ" IS NOT NULL AND b."CNPJ" != 0