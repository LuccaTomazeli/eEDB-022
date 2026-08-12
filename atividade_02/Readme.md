resumo da atividade 1

## Docker

Para executar a atividade 02 em Docker e manter o banco disponível depois da carga, rode a partir desta pasta:

```bash
docker compose up -d postgres
docker compose run --rm pipeline
```

O serviço `pipeline` executa os scripts de tratamento, gera os parquets em `data/trusted`, salva o delivery em `data/delivery/delivery_bancos.parquet` e carrega a tabela `delivery_bancos` no Postgres. O container do banco continua ativo para consultas depois.