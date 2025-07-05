import requests
import csv
import os
import json
from datetime import datetime, date 
import logging
import time
import random 

# --- CONFIGURAÇÃO INICIAL DO LOG ---
logging.basicConfig(
    filename='coleta_dados.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# --- FUNÇÃO PRINCIPAL ---
def baixar_e_salvar_estacao(id_estacao, pasta_saida, timestamp_arquivo, data_coleta):
    """
    Baixa, processa e salva os dados de uma única estação de monitoramento.
    """
    url = f"https://monitorar-backend.mma.gov.br/v1/estacao/por-ids?ids={id_estacao}"
    logging.info(f"Processando estação: {id_estacao} | URL: {url}")

    try:
        # <-- 2. BLOCO TRY...EXCEPT PARA ROBUSTEZ DA REQUISIÇÃO ---
        response = requests.get(url, timeout=30) # Adiciona um timeout de 30s
        response.raise_for_status() # Lança um erro para respostas ruins (4xx ou 5xx)
        dados = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de rede ao buscar dados para estação {id_estacao}: {e}")
        return
    except json.JSONDecodeError:
        logging.error(f"Falha ao decodificar JSON da resposta para estação {id_estacao}. Resposta: {response.text[:100]}")
        return

    if not isinstance(dados, list) or not dados:
        logging.warning(f"Resposta válida, mas vazia ou em formato inesperado para a estação ID: {id_estacao}.")
        return

    # O resto da lógica de processamento continua aqui...
    est = dados[0]
    nome_estacao = est.get("noEstacao", f"id_{id_estacao}").replace(" ", "_").lower()
    
    # ... (extração dos outros campos como você fez)
    id_uf = est.get("municipio", {}).get("uf", {}).get("idUf")
    sigla_uf = est.get("municipio", {}).get("uf", {}).get("sgUf")
    id_municipio = est.get("municipio", {}).get("idMunicipio")
    temperatura = est.get("temperatura")
    umidade = est.get("umidade")
    vento = est.get("vento")
    dt_medicao_geral = est.get("dtMedicao")

    registros = []
    for poluente in est.get("poluentes", []):
        for medicao in poluente.get("medicoes", []):
            registros.append({
                "dt_coleta": data_coleta,
                "dt_medicao_geral": dt_medicao_geral,
                "id_municipio": id_municipio,
                "id_uf": id_uf,
                "uf": sigla_uf,
                "estacao": nome_estacao,
                "temperatura": temperatura,
                "umidade": umidade,
                "vento": vento,
                "id_poluente": poluente.get("idPoluente"),
                "nome_poluente": poluente.get("noPoluente"),
                "descricao_poluente": poluente.get("dsPoluente"),
                "data_hora_medicao": medicao.get("dtMedicao"),
                "indice_qualidade_ar": medicao.get("indiceQualidadeAr"),
                "classificacao": medicao.get("classificacaoIqAr", {}).get("noClassificacao"),
                "dado_validado": medicao.get("stDadoValidado")
            })

    if registros:
        caminho_arquivo = f"{pasta_saida}/{nome_estacao}_{timestamp_arquivo}.csv"
        with open(caminho_arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=registros[0].keys())
            writer.writeheader()
            writer.writerows(registros)
        logging.info(f"Dados para '{nome_estacao}' salvos com {len(registros)} registros.")
    else:
        logging.warning(f"Nenhum registro de medição de poluentes encontrado para a estação '{nome_estacao}'.")


# --- BLOCO PRINCIPAL DE EXECUÇÃO ---
if __name__ == "__main__":
    logging.info("===== INICIANDO NOVA COLETA DE DADOS =====")
    
    try:
        with open("estacoes.json", "r", encoding="utf-8") as f:
            estacoes = json.load(f)
        ids_estacoes_bahia = [est["idEstacao"] for est in estacoes if est.get("idUf") == 29]
        logging.info(f"Encontradas {len(ids_estacoes_bahia)} estações para a Bahia.")
    except FileNotFoundError:
        logging.error("Arquivo 'estacoes.json' não encontrado. Abortando execução.")
        exit() # Sai do script se o arquivo principal não existe

    # --- 3. TIMESTAMP GERADO UMA VEZ ---
    data_hora_coleta = datetime.now()
    data_hoje_str = data_hora_coleta.strftime('%Y-%m-%d')
    timestamp_arquivo_str = data_hora_coleta.strftime('%Y-%m-%d_%H')
    # timestamp_arquivo_str = data_hora_coleta.strftime('%Y-%m-%d_%H-%M')
    
    pasta_saida = f"dados/{data_hoje_str}"
    os.makedirs(pasta_saida, exist_ok=True)
    logging.info(f"Pasta de saída definida como: {pasta_saida}")

    # Loop principal
    for id_est in ids_estacoes_bahia:
        baixar_e_salvar_estacao(id_est, pasta_saida, timestamp_arquivo_str, data_hoje_str)
        time.sleep(random.uniform(1.5, 3.5))

    logging.info("===== COLETA DE DADOS FINALIZADA =====")