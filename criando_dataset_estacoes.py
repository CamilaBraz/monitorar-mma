import json

with open("estacoes_raw.json", "r", encoding="utf-8") as f:
    dados = json.load(f)

filtrado = []

for estacao in dados:
    municipio = estacao.get("municipio")

    if municipio:
        id_municipio = municipio.get("idMunicipio")
        uf_data = municipio.get("uf") or {}
        id_uf = uf_data.get("idUf")
    else:
        id_municipio = None
        id_uf = None

    nova_entrada = {
        "idEstacao": estacao.get("idEstacao"),
        "coEstacao": estacao.get("coEstacao"),
        "noEstacao": estacao.get("noEstacao"),
        "idUf": id_uf,
        "idMunicipio": id_municipio,
    }
    filtrado.append(nova_entrada)

with open("estacoes.json", "w", encoding="utf-8") as f_out:
    json.dump(filtrado, f_out, ensure_ascii=False, indent=2)
