import requests
import csv
import os

# Cria a pasta se não existir
os.makedirs("dados", exist_ok=True)

# URL da estação (exemplo Botelho)
url = "https://monitorar-backend.mma.gov.br/v1/estacao/por-ids?ids=136613"

response = requests.get(url)
dados = response.json()

# Verifica se dados é uma lista e tem pelo menos um item
if not isinstance(dados, list) or len(dados) == 0:
    print("❌ Nenhum dado retornado pela API ou estrutura inesperada!")
    print("Conteúdo retornado:", dados)
    exit()

# Pega a primeira estação
est = dados[0]

# Coleta os dados gerais da estação
nome_estacao = est.get("noEstacao", "")
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

# Salva em CSV se tiver registros
if registros:
    caminho_arquivo = f"dados/{nome_estacao.lower().replace(' ', '_')}.csv"
    with open(caminho_arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=registros[0].keys())
        writer.writeheader()
        writer.writerows(registros)

    print(f"✅ Arquivo salvo com sucesso em: {caminho_arquivo}")
else:
    print("⚠️ Nenhum registro encontrado para salvar.")
