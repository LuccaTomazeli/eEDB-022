
  
    

  create  table "eedb022_a5"."delivery"."delivery_final__dbt_tmp"
  
  
    as
  
  (
    

WITH reclamacoes_agg AS (
    SELECT
        cnpj,
        SUM(qtd_reclamacoes) AS total_reclamacoes
    FROM "eedb022_a5"."trusted"."trusted_reclamacoes"
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
FROM "eedb022_a5"."trusted"."trusted_bancos" b
LEFT JOIN reclamacoes_agg r ON b.cnpj = r.cnpj
LEFT JOIN "eedb022_a5"."trusted"."trusted_empregados" e ON b.nome_busca = e.nome
  );
  