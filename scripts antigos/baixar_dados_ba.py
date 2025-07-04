import requests
import csv
import os
import json

# Carrega os ids das estações da Bahia
with open("estacoes.json", "r", encoding="utf-8") as f:
    estacoes = json.load(f)

# Filtra os IDs da Bahia
ids_bahia = [est["idEstacao"] for est in estacoes if est.get("idUf") == 29]

# Percorre cada estação da Bahia
for id_estacao in ids_bahia:
    url = f"https://monitorar-backend.mma.gov.br/v1/estacao/por-ids?ids={id_estacao}"
    response = requests.get(url)

    try:
        dados = response.json()
    except Exception as e:
        print(f" Erro ao converter JSON da estação {id_estacao}: {e}")
        continue

    if not isinstance(dados, list) or len(dados) == 0:
        print(f"⚠️ Nenhum dado para estação {id_estacao}")
        continue

    est = dados[0]
    nome_estacao = est.get("noEstacao", f"estacao_{id_estacao}")
    id_uf = est.get("municipio", {}).get("uf", {}).get("idUf")
    sigla_uf = est.get("municipio", {}).get("uf", {}).get("sgUf")
    id_municipio = est.get("municipio", {}).get("idMunicipio")
    temperatura = est.get("temperatura")
    umidade = est.get("umidade")
    vento = est.get("vento")

    registros = []

    for poluente in est.get("poluentes", []):
        id_poluente = poluente.get("idPoluente")
        nome_poluente = poluente.get("noPoluente")
        descricao_poluente = poluente.get("dsPoluente")

        for medicao in poluente.get("medicoes", []):
            registros.append({
                "id_municipio": id_municipio,
                "estacao": nome_estacao,
                "id_uf": id_uf,
                "uf": sigla_uf,
                "temperatura": temperatura,
                "umidade": umidade,
                "vento": vento,
                "id_poluente": id_poluente,
                "nome_poluente": nome_poluente,
                "descricao_poluente": descricao_poluente,
                "data_hora": medicao.get("dtMedicao"),
                "indice_qualidade_ar": medicao.get("indiceQualidadeAr"),
                "classificacao": medicao.get("classificacaoIqAr", {}).get("noClassificacao"),
                "dado_validado": medicao.get("stDadoValidado")
            })

    # Salva em CSV se houver dados
    if registros:
        nome_arquivo = nome_estacao.lower().replace(" ", "_").replace("/", "-")
        caminho_arquivo = f"dados/{nome_arquivo}.csv"
        with open(caminho_arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=registros[0].keys())
            writer.writeheader()
            writer.writerows(registros)

        print(f"✅ Estação '{nome_estacao}' salva com sucesso em: {caminho_arquivo}")
    else:
        print(f"⚠️ Nenhum registro para a estação '{nome_estacao}' ({id_estacao})")
