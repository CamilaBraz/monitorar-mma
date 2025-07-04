# 🌬️ Monitoramento da Qualidade do Ar - Bahia

Este projeto automatiza a coleta diária de dados de qualidade do ar a partir da API pública do Ministério do Meio Ambiente (MMA), com foco inicial nas estações localizadas no estado da Bahia (UF = BA).

---

## 📌 Objetivo

- Rastrear os níveis de poluentes atmosféricos monitorados em tempo real.
- Armazenar os dados em formato `.csv` organizados por data e estação.
- Gerar uma versão consolidada diária com todos os dados coletados no estado.
- Automatizar o processo com GitHub Actions para facilitar atualizações frequentes.


---

## ⚙️ Como Executar Localmente

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Execute o script principal

```python
scripts/baixar_dados_ba_por_data.py
```

Os dados serão salvos na pasta `dados/` com subpastas por data e um arquivo consolidado.


## 🤖 Automação com GitHub Actions

O projeto conta com uma automação agendada via GitHub Actions (`.github/workflows/baixar_dados.yml`) que roda diariamente para:

 - Executar o script de coleta;

 - Armazenar os dados atualizados no repositório;

## 📈 Dados Coletados

Cada registro inclui:

 - Data e hora da medição

 - Estação e município

 - Tipo e descrição do poluente

 - Índice de qualidade do ar

 - Classificação ("Boa", "Moderada", etc.)

 - Indicadores climáticos (quando disponíveis): temperatura, umidade, vento

## 🗺️ Foco Inicial: Estado da Bahia

O projeto atualmente coleta dados das seguintes estações:

 - BOTELHO

 - MALEMBA

 - AREIAS

 - AREIAS II

 - CABOTO

 - CÂMARA

 - COBRE

 - CONCORDIA

 - ESCOLA

 - FUTURAMA I

 - GAMBOA

 - GRAVATÁ

 - LAMARÃO

 - LEANDRINHO

 - MACHADINHO

## 📌 Próximos Passos

 - Implementar verificação de falhas e envio de logs
