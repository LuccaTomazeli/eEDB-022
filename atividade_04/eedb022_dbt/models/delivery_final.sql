{{ config(schema='delivery') }}

WITH reclamacoes_agg AS (
    SELECT
        cnpj,
        SUM(qtd_reclamacoes) AS total_reclamacoes
    FROM {{ ref('trusted_reclamacoes') }}
    GROUP BY cnpj
)

SELECT
    b.cnpj,
    b.nome_completo AS nome,
    b.segmento,
    COALESCE(r.total_reclamacoes, 0) AS total_reclamacoes,
    e.nota_geral,
    e.nota_remuneracao,
    e.pct_recomendam
FROM {{ ref('trusted_bancos') }} b
LEFT JOIN reclamacoes_agg r ON b.cnpj = r.cnpj
LEFT JOIN {{ ref('trusted_empregados') }} e ON b.nome_busca = e.nome