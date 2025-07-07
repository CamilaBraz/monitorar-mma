# 🌬️ Monitoramento da Qualidade do Ar

Este projeto automatiza a coleta diária de dados de qualidade do ar a partir da API pública do Ministério do Meio Ambiente (MMA).

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
scripts/baixar_dados.py
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

## Estrutura dos Arquivos e Dados

Os dados coletados são armazenados em formato `.csv` e organizados em uma estrutura de pastas hierárquica para facilitar o acesso e a navegação. A lógica da organização é a seguinte:

`dados/UF/DATA_DA_COLETA/ARQUIVO.csv`

Onde:
* **`UF`**: A sigla da Unidade da Federação
* **`DATA_DA_COLETA`**: A data em que o script de coleta foi executado, no formato `AAAA-MM-DD`.
* **`ARQUIVO.csv`**: O arquivo de dados final, nomeado com o nome da estação e o timestamp (data e hora) da coleta.

Abaixo está um exemplo da aparência da estrutura de pastas:

```text
dados/
├── BA/
│   └── 2025-07-07/
│       ├── salvador_campus_ondina_2025-07-07_17.csv
│       └── vitoria_da_conquista_centro_2025-07-07_17.csv
│
├── RJ/
│   └── 2025-07-07/
│       ├── duque_de_caxias_2025-07-07_17.csv
│       └── sao_goncalo_2025-07-07_17.csv
│
└── SP/
    └── 2025-07-07/
        ├── campinas_centro_2025-07-07_17.csv
        └── sao_paulo_parque_d_pedro_ii_2025-07-07_17.csv
```

## 🗺️ Unidades Federativas

O projeto está configurado para coletar dados das estações localizadas nas seguintes UFs que estão disponíveis na plataforma do ministério do meio ambiente:

* Bahia (BA)
* Distrito Federal (DF)
* Espírito Santo (ES)
* Maranhão (MA)
* Minas Gerais (MG)
* Mato Grosso do Sul (MS)
* Pará (PA)
* Pernambuco (PE)
* Paraná (PR)
* Rio de Janeiro (RJ)
* Rio Grande do Sul (RS)
* Santa Catarina (SC)
* São Paulo (SP)

## 📌 Próximos Passos

O objetivo contínuo deste projeto é não apenas coletar os dados, mas também avaliar sua qualidade e integridade. Os próximos passos planejados incluem:

- **Relatório de Disponibilidade de Dados:**
  - Criar um painel ou relatório que mostre, para cada UF, quantas estações estão ativas e quantas estão inativas ou sem dados recentes.

- **Melhoria Contínua:**
  - Otimizar o processo de coleta e adicionar mais UFs ao escopo do projeto.
 
- **Consolidação dos Dados**

  - Os dados serão agregados mensalmente, por UF e disponibilizados em uma plataforma de dados como o Kaggle.
