import requests
import csv
import os
import json
from datetime import datetime
import logging

# --- CONFIGURAÇÃO INICIAL DO LOG ---
logging.basicConfig(
    filename='coleta_dados.log', # Nome do arquivo que guardará os logs
    level=logging.INFO,          # Nível mínimo de mensagem a ser registrada
    format='%(asctime)s - %(levelname)s - %(message)s', # Formato da mensagem
    encoding='utf-8'             # Garante a compatibilidade com acentos
)
# --- FIM DA CONFIGURAÇÃO ---

# Carrega os ids das estações da Bahia
with open("estacoes.json", "r", encoding="utf-8") as f:
    estacoes = json.load(f)

# Filtra os IDs da Bahia
ids_estacoes_bahia = [est["idEstacao"] for est in estacoes if est.get("idUf") == 29]

# === Defina a data da coleta (hoje) ===
data_hora_coleta = datetime.now()

# 1. Apenas a data no formato 'AAAA-MM-DD'
data_hoje = data_hora_coleta.strftime('%Y-%m-%d')

# 2. O timestamp completo para o nome do arquivo
timestamp_arquivo = data_hora_coleta.strftime('%Y-%m-%d_%H-%M')
print(timestamp_arquivo)

# === Crie a pasta do dia ===
pasta_saida = f"dados/{data_hoje}"
os.makedirs(pasta_saida, exist_ok=True)

# === Função para baixar e salvar dados de uma estação ===
def baixar_e_salvar_estacao(id_estacao):
    url = f"https://monitorar-backend.mma.gov.br/v1/estacao/por-ids?ids={id_estacao}"
    response = requests.get(url)
    dados = response.json()

    logging.info(f"Processando estação: {id_estacao}")

    if not isinstance(dados, list) or len(dados) == 0:
        logging.error(f"Falha ao obter dados (resposta inválida ou vazia) para a estação ID: {id_estacao}.")
        return

    est = dados[0]

    nome_estacao = est.get("noEstacao", f"id_{id_estacao}").replace(" ", "_").lower()
    id_uf = est.get("municipio", {}).get("uf", {}).get("idUf")
    sigla_uf = est.get("municipio", {}).get("uf", {}).get("sgUf")
    id_municipio = est.get("municipio", {}).get("idMunicipio")
    temperatura = est.get("temperatura")
    umidade = est.get("umidade")
    vento = est.get("vento")
    dt_medicao = est.get("dtMedicao")

    registros = []

    

    for poluente in est.get("poluentes", []):
        id_poluente = poluente.get("idPoluente")
        nome_poluente = poluente.get("noPoluente")
        descricao_poluente = poluente.get("dsPoluente")

        for medicao in poluente.get("medicoes", []):
            registros.append({
                "dt_coleta": data_hoje,
                "dt_medicao": dt_medicao,
                "id_municipio": id_municipio,
                "id_uf": id_uf,
                "uf": sigla_uf,
                "estacao": nome_estacao,
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



    if registros:
        # caminho_arquivo = f"{pasta_saida}/{nome_estacao}.csv"
        caminho_arquivo = f"{pasta_saida}/{nome_estacao}_{timestamp_arquivo}.csv"
        with open(caminho_arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=registros[0].keys())
            writer.writeheader()
            writer.writerows(registros)
        logging.info(f"Dados para '{nome_estacao}' salvos em: {caminho_arquivo}")
    else:
        logging.warning(f"Nenhum registro encontrado para a estação '{nome_estacao}'")

# === Loop nas estações da Bahia ===
for id_est in ids_estacoes_bahia:
    baixar_e_salvar_estacao(id_est)