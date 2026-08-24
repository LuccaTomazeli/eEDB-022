SELECT
    UPPER(TRIM("Nome")) AS nome,
    AVG("Geral") AS nota_geral,
    AVG("Remuneração e benefícios") AS nota_remuneracao,
    AVG("Recomendam para outras pessoas(%)") AS pct_recomendam
FROM raw.empregados
WHERE "Nome" IS NOT NULL AND TRIM("Nome") != ''
GROUP BY UPPER(TRIM("Nome"))