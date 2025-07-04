import requests
import pandas as pd

def baixar_dados_estacao(estacao_id):
    url = f"https://monitorar-backend.mma.gov.br/v1/estacao/por-ids?ids={estacao_id}"
    response = requests.get(url)
    response.raise_for_status()
    dados = response.json()[0]
    return dados

def processar_e_salvar_csv(dados, arquivo_saida):
    registros = []
    estacao = dados["noEstacao"]
    
    for poluente in dados["poluentes"]:
        nome_poluente = poluente["noPoluente"]
        for medicao in poluente["medicoes"]:
            registros.append({
                "estacao": estacao,
                "poluente": nome_poluente,
                "data_hora": medicao["dtMedicao"],
                "indice_qualidade_ar": medicao["indiceQualidadeAr"],
                "classificacao": medicao["classificacaoIqAr"]["noClassificacao"]
            })
    
    df = pd.DataFrame(registros)
    df.to_csv(arquivo_saida, index=False)
    print(f"Dados salvos em {arquivo_saida}")

if __name__ == "__main__":
    estacao_id = 136613  # Botelho
    dados = baixar_dados_estacao(estacao_id)
    processar_e_salvar_csv(dados, "dados_botelho.csv")
