import requests
import urllib3
import csv
import os
import json
from datetime import datetime, date 
import logging
import time
import random 
import unicodedata

# Desabilita o aviso de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def remover_acentos(texto: str) -> str:
    """Normaliza o texto, separando acentos dos caracteres e removendo-os."""
    forma_normalizada = unicodedata.normalize('NFD', texto)
    return ''.join(c for c in forma_normalizada if not unicodedata.combining(c))

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
        # Adiciona verify=False para ignorar verificação SSL
        response = requests.get(url, timeout=30, verify=False)
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

    # nome_estacao = est.get("noEstacao", f"id_{id_estacao}").replace(" ", "_").lower()
    # Primeiro, pegamos o nome original da estação
    nome_estacao_bruto = est.get("noEstacao", f"id_{id_estacao}")

    # Aplica nossa função para remover os acentos
    nome_sem_acentos = remover_acentos(nome_estacao_bruto)

    # Agora, fazemos as outras substituições que já tínhamos
    nome_estacao = nome_sem_acentos.replace("/", "_").replace(" ", "_").lower()
    
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
                "classificacao": (medicao.get("classificacaoIqAr") or {}).get("noClassificacao"),
                #"classificacao": medicao.get("classificacaoIqAr", {}).get("noClassificacao"),
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
    logging.info("===== INICIANDO NOVA COLETA DE DADOS GERAL =====")
    
    # 1. DICIONÁRIO COM AS UFs QUE QUEREMOS COLETAR
    # Chave: Sigla (para o nome da pasta), Valor: idUf (para o filtro)
    UFS_PARA_COLETAR = {
        "BA": 29,
        "PA": 15,
        "MA": 13,
        "PE": 26,
        "ES": 32,
        "DF": 53,
        "MG": 31,
        "SP": 35,
        "RJ": 33,
        "SC": 42,
        "RS": 43,
        "PR": 41,
        "MS": 50
    }
    logging.info(f"Coleta configurada para as UFs: {list(UFS_PARA_COLETAR.keys())}")

    try:
        with open("estacoes.json", "r", encoding="utf-8") as f:
            todas_as_estacoes = json.load(f)
    except FileNotFoundError:
        logging.error("Arquivo 'estacoes.json' não encontrado. Abortando execução.")
        exit()

    # Gera o timestamp UMA VEZ para toda a execução
    data_hora_coleta = datetime.now() # Idealmente com fuso horário, como fizemos antes
    data_hoje_str = data_hora_coleta.strftime('%Y-%m-%d')
    timestamp_arquivo_str = data_hora_coleta.strftime('%Y-%m-%d_%H')

    # --- 2. NOVO LOOP PRINCIPAL POR ESTADO ---
    for sigla_uf, id_uf_alvo in UFS_PARA_COLETAR.items():
        logging.info(f"--- Processando estado: {sigla_uf} (ID: {id_uf_alvo}) ---")

        # 3. FILTRA AS ESTAÇÕES PARA O ESTADO ATUAL
        ids_estacoes_do_estado = [
            est["idEstacao"] for est in todas_as_estacoes if est.get("idUf") == id_uf_alvo
        ]
        
        if not ids_estacoes_do_estado:
            logging.warning(f"Nenhuma estação encontrada para a UF '{sigla_uf}' no arquivo 'estacoes.json'. Pulando para o próximo estado.")
            continue # Pula para a próxima iteração do loop de UFs

        logging.info(f"Encontradas {len(ids_estacoes_do_estado)} estações para {sigla_uf}.")

        # 4. CRIA A PASTA DE SAÍDA PARA O ESTADO E O DIA
        pasta_saida_uf = f"dados/{sigla_uf}/{data_hoje_str}"
        os.makedirs(pasta_saida_uf, exist_ok=True)
        logging.info(f"Pasta de saída definida como: {pasta_saida_uf}")

        # Loop interno para baixar os dados de cada estação do estado
        for id_est in ids_estacoes_do_estado:
            baixar_e_salvar_estacao(id_est, pasta_saida_uf, timestamp_arquivo_str, data_hoje_str)
            
            # Delay para ser gentil com a API
            tempo_de_espera = random.uniform(2.5, 5.5)
            logging.info(f"Aguardando {tempo_de_espera:.2f} segundos...")
            time.sleep(tempo_de_espera)
            
    logging.info("===== COLETA DE DADOS GERAL FINALIZADA =====")