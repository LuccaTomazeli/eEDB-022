import os

import pandas as pd
import great_expectations as gx


BASE_DIR = "/opt/atividade_05/data/trusted"


print("========================================")
print("ATIVIDADE 5 - QUALIDADE DOS DADOS")
print("========================================")


context = gx.get_context()


datasets = {
    "trusted_bancos": {
        "arquivo": "trusted_bancos.parquet",
        "colunas": [
            "cnpj",
            "nome_completo",
            "nome_busca",
            "segmento",
        ],
    },
    "trusted_reclamacoes": {
        "arquivo": "trusted_reclamacoes.parquet",
        "colunas": [
            "ano",
            "trimestre",
            "cnpj",
            "instituicao",
            "qtd_reclamacoes",
        ],
    },
    "trusted_empregados": {
        "arquivo": "trusted_empregados.parquet",
        "colunas": [
            "nome",
            "nota_geral",
            "nota_remuneracao",
            "pct_recomendam",
        ],
    },
}


total_passou = 0
total_falhou = 0


def executar_expectation(nome, resultado):
    global total_passou
    global total_falhou

    sucesso = resultado["success"]

    if sucesso:
        print(f"  ✓ {nome}")
        total_passou += 1
    else:
        print(f"  ✗ {nome}")
        total_falhou += 1

        if "result" in resultado:
            print(f"    Resultado: {resultado['result']}")


for nome, config in datasets.items():

    print()
    print("----------------------------------------")
    print(nome.upper())
    print("----------------------------------------")

    caminho = os.path.join(
        BASE_DIR,
        config["arquivo"]
    )

    if not os.path.exists(caminho):
        print(f"ERRO: arquivo não encontrado: {caminho}")
        raise FileNotFoundError(caminho)

    print(f"Arquivo: {caminho}")

    # Leitura auxiliar para informações de volume
    df = pd.read_parquet(caminho)

    print(f"Linhas: {len(df)}")

    # Data Source
    datasource = context.data_sources.add_pandas(
        name=f"{nome}_datasource"
    )

    # Data Asset
    asset = datasource.add_parquet_asset(
        name=f"{nome}_asset",
        path=caminho
    )

    # Batch
    batch_request = asset.build_batch_request()

    validator = context.get_validator(
        batch_request=batch_request
    )

    # =====================================================
    # VALIDAÇÕES COMUNS
    # =====================================================

    executar_expectation(
        "Tabela possui pelo menos 1 registro",
        validator.expect_table_row_count_to_be_between(
            min_value=1
        )
    )

    executar_expectation(
        "Estrutura de colunas está correta",
        validator.expect_table_columns_to_match_set(
            column_set=config["colunas"],
            exact_match=True
        )
    )

    # =====================================================
    # TRUSTED BANCOS
    # =====================================================

    if nome == "trusted_bancos":

        executar_expectation(
            "CNPJ não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="cnpj"
            )
        )

        executar_expectation(
            "Nome completo não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="nome_completo"
            )
        )

        executar_expectation(
            "Nome de busca não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="nome_busca"
            )
        )

        executar_expectation(
            "Segmento não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="segmento"
            )
        )

        executar_expectation(
            "CNPJ possui 8 dígitos",
            validator.expect_column_values_to_match_regex(
                column="cnpj",
                regex=r"^\d{8}$"
            )
        )

        executar_expectation(
            "Segmento pertence ao padrão S1-S5",
            validator.expect_column_values_to_match_regex(
                column="segmento",
                regex=r"^S[1-5]$"
            )
        )

    # =====================================================
    # TRUSTED RECLAMACOES
    # =====================================================

    elif nome == "trusted_reclamacoes":

        executar_expectation(
            "Ano não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="ano"
            )
        )

        executar_expectation(
            "Trimestre não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="trimestre"
            )
        )

        executar_expectation(
            "CNPJ não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="cnpj"
            )
        )

        executar_expectation(
            "Instituição não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="instituicao"
            )
        )

        executar_expectation(
            "Quantidade de reclamações não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="qtd_reclamacoes"
            )
        )

        executar_expectation(
            "Ano está entre 2021 e 2022",
            validator.expect_column_values_to_be_between(
                column="ano",
                min_value=2021,
                max_value=2022
            )
        )

        executar_expectation(
            "Trimestre possui valores válidos",
            validator.expect_column_values_to_be_in_set(
                column="trimestre",
                value_set=[
                    "1º",
                    "2º",
                    "3º",
                    "4º",
                ]
            )
        )

        executar_expectation(
            "CNPJ possui 8 dígitos",
            validator.expect_column_values_to_match_regex(
                column="cnpj",
                regex=r"^\d{8}$"
            )
        )

        executar_expectation(
            "Quantidade de reclamações é positiva",
            validator.expect_column_values_to_be_between(
                column="qtd_reclamacoes",
                min_value=1
            )
        )

    # =====================================================
    # TRUSTED EMPREGADOS
    # =====================================================

    elif nome == "trusted_empregados":

        executar_expectation(
            "Nome não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="nome"
            )
        )

        executar_expectation(
            "Nota geral não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="nota_geral"
            )
        )

        executar_expectation(
            "Nota de remuneração não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="nota_remuneracao"
            )
        )

        executar_expectation(
            "Percentual de recomendação não possui valores nulos",
            validator.expect_column_values_to_not_be_null(
                column="pct_recomendam"
            )
        )

        executar_expectation(
            "Nota geral está entre 0 e 5",
            validator.expect_column_values_to_be_between(
                column="nota_geral",
                min_value=0,
                max_value=5
            )
        )

        executar_expectation(
            "Nota de remuneração está entre 0 e 5",
            validator.expect_column_values_to_be_between(
                column="nota_remuneracao",
                min_value=0,
                max_value=5
            )
        )

        executar_expectation(
            "Percentual de recomendação está entre 0 e 100",
            validator.expect_column_values_to_be_between(
                column="pct_recomendam",
                min_value=0,
                max_value=100
            )
        )


print()
print("========================================")
print("RESULTADO FINAL DA QUALIDADE")
print("========================================")

print(f"PASSOU: {total_passou}")
print(f"FALHOU: {total_falhou}")

print()

if total_falhou > 0:

    print("QUALIDADE DOS DADOS REPROVADA!")
    print("O pipeline deve ser interrompido.")

    raise RuntimeError(
        f"Validação de qualidade falhou: "
        f"{total_falhou} expectation(s) não atendida(s)."
    )

else:

    print("QUALIDADE DOS DADOS APROVADA!")
    print("Todas as validações foram executadas com sucesso.")

print("========================================")