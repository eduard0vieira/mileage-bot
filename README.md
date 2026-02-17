# Mileage Bot - Flight Alert Formatter 🛫

CLI para formatação de alertas de passagens aéreas com milhas/pontos.

## 📁 Estrutura do Projeto (v4.0 - Modular)

```
mileage-bot/
├── main.py                    # 🎯 Script principal - COMECE AQUI!
├── requirements.txt           # Dependências do projeto
├── .env                       # Chave API Seats.aero (não commitado)
├── input.txt                  # Arquivo de entrada para modo file
├── README.md
├── REFACTORING.md            # 📚 Documentação da refatoração
├── app/                      # 🏗️ Código fonte modular
│   ├── __init__.py
│   ├── core/                 # Núcleo: configurações e modelos
│   │   ├── __init__.py
│   │   ├── config.py         # Configurações (.env, API keys)
│   │   └── models.py         # FlightBatch e lógica de datas
│   ├── services/             # Serviços: integrações externas
│   │   ├── __init__.py
│   │   ├── file_service.py   # Parser de input.txt
│   │   └── seats_client.py   # Cliente API Seats.aero
│   ├── ui/                   # Interface: renderização
│   │   ├── __init__.py
│   │   └── renderer.py       # Render com Jinja2
│   └── utils/                # Utilitários: helpers
│       ├── __init__.py
│       └── helpers.py        # load_airport_data, etc
├── templates/                # Templates Jinja2 (.j2) para alertas
│   └── padrao_whatsapp.j2    # Template WhatsApp
├── data/                     # Dados estáticos
│   └── airports.json         # Códigos IATA → cidade + bandeira
└── tests/                    # Testes automatizados
    ├── test_visual_format.py
    └── test_advanced_features.py
```

## 🚀 Setup e Execução

### 1. Criar ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 2. Instalar dependências:
```bash
pip install -r requirements.txt
```

### 3. Configurar API Seats.aero (opcional):
```bash
# Criar arquivo .env na raiz
echo "SEATS_API_KEY=sua_chave_aqui" > .env
```

### 4. Executar:

**Modo FILE** (lê `input.txt`):
```bash
python main.py --mode file
```

**Modo API** (busca em Seats.aero):
```bash
python main.py --mode api --origin GRU --dest MIA --days 365
```

**Ver ajuda completa:**
```bash
python main.py --help
```

## 📦 Dependências

- **jinja2**: Template engine para gerar os textos dos alertas
- **arrow**: Manipulação de datas em português (melhor que datetime)
- **rich**: Prints coloridos e formatados no terminal
- **requests**: Cliente HTTP para API Seats.aero
- **python-dotenv**: Carrega variáveis de ambiente do `.env`

## 🔧 Como Funciona

### Modelo de Dados: `FlightBatch`

```python
from app.core.models import FlightBatch

flight = FlightBatch(
    origin="São Paulo",
    origin_code="GRU",
    origin_flag="🇧🇷",
    destination="Miami",
    dest_code="MIA",
    dest_flag="🇺🇸",
    airline="Latam",
    program="Privilege Club",
    cost="77k",
    cabin="Executiva",
    dates_outbound=[("2026-05-01", 9), ("2026-05-05", 4)],
    dates_inbound=[("2026-05-10", 7)],
    notes="Taxas ~R$ 600",
    min_cost=77000,
    max_cost=77000
)
```

### Formatação de Datas:

**Entrada:**
```python
[("2026-05-01", 9), ("2026-05-05", 4), ("2026-06-10", 2)]
```

**Saída:**
```
Mai 2026: 01 (9), 05 (4)
Jun 2026: 10 (2)
```

**Regras:**
- ✅ Ordenação cronológica rigorosa
- ✅ Meses com primeira letra MAIÚSCULA
- ✅ Dias com zero à esquerda

### Renderização de Alertas:

```python
from app.ui.renderer import render_alert

alert_text = render_alert(flight, "padrao_whatsapp.j2")
print(alert_text)  # Texto formatado para WhatsApp
```

## 🎯 Funcionalidades

### 1. Modo FILE
Lê arquivo `input.txt` e gera alertas:
```bash
python main.py --mode file
```

### 2. Modo API
Busca disponibilidade na API Seats.aero:
```bash
# Busca básica
python main.py --mode api --origin GRU --dest MIA

# Busca anual (365 dias)
python main.py --mode api --origin GRU --dest DOH --days 365

# Apenas voos diretos
python main.py --mode api --origin GRU --dest MIA --direct

# Filtrar por companhia
python main.py --mode api --origin GRU --dest MIA --airline Latam

# Filtrar por programa
python main.py --mode api --origin GRU --dest DOH --program "Privilege Club"

# Voos recentes (últimas 24h)
python main.py --mode api --origin GRU --dest MIA --stale 24

# Busca COMPLETA (todos os filtros)
python main.py --mode api --origin GRU --dest DOH --days 365 \
  --airline "Qatar Airways" --direct --stale 24 \
  --program "Privilege Club"
```

### 3. Argumentos CLI Disponíveis

| Argumento | Descrição | Padrão |
|-----------|-----------|--------|
| `--mode` | `file` ou `api` | `file` |
| `--origin` | Código IATA origem (GRU) | - |
| `--dest` | Código IATA destino (MIA) | - |
| `--days` | Dias à frente (1-365) | 60 |
| `--cabin` | Classe (economy/business/first) | business |
| `--direct` | Apenas voos diretos | False |
| `--stale` | Max horas desde última atualização | 48 |
| `--program` | Filtrar por programa de milhas | - |
| `--airline` | Filtrar por companhia | - |

## 🏗️ Arquitetura Modular

### `app/core/` - Núcleo
- **config.py**: Configurações (`.env`, API keys)
- **models.py**: Modelos de dados (`FlightBatch`)

### `app/services/` - Serviços
- **file_service.py**: Parser de `input.txt`
- **seats_client.py**: Cliente API Seats.aero

### `app/ui/` - Interface
- **renderer.py**: Renderização de templates Jinja2

### `app/utils/` - Utilitários
- **helpers.py**: Funções auxiliares (`load_airport_data`)

**Leia mais:** [REFACTORING.md](REFACTORING.md)

## 🧪 Testes

### Executar Testes:

**Opção 1: Script automático (recomendado)**
```bash
./run_tests.sh              # Bash
./run_tests.fish            # Fish Shell
```

**Opção 2: Python diretamente**
```bash
python tests/test_visual_format.py
python tests/test_advanced_features.py
python tests/test_seats_processing.py
```

**Opção 3: Com pytest (após instalar requirements-dev.txt)**
```bash
pip install -r requirements-dev.txt
pytest tests/                # Todos os testes
pytest tests/ -v             # Modo verbose
pytest tests/ --cov=app      # Com cobertura
```

### O que é testado:

- ✅ **Formatação visual**: Datas, templates, ordenação
- ✅ **Filtros avançados**: Staleness, direct, airline, program
- ✅ **Processamento API**: Agrupamento, min/max cost, enriquecimento

**Leia mais:** [TESTING.md](TESTING.md)

## 📚 Documentação

- **[REFACTORING.md](REFACTORING.md)**: Explicação da refatoração para estrutura modular
- **[TESTING.md](TESTING.md)**: Guia completo de testes (pytest, cobertura, boas práticas)
- **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)**: Funcionalidades avançadas de filtros
- **[VISUAL_FORMAT_UPDATE.md](VISUAL_FORMAT_UPDATE.md)**: Formatação visual estrita
- **[API_FILTERS_FIX.md](API_FILTERS_FIX.md)**: Separação de filtros API vs. locais
- **[API_MAPPING_FIX.md](API_MAPPING_FIX.md)**: Correção do mapeamento JSON → Objeto
- **[TYPE_SAFETY_FIX.md](TYPE_SAFETY_FIX.md)**: Correção de TypeError (strings → int)
- **[API_STRUCTURE_REFERENCE.md](API_STRUCTURE_REFERENCE.md)**: Referência rápida - estrutura da API Seats.aero
- **[LOYALTY_PROGRAMS.md](LOYALTY_PROGRAMS.md)**: Guia completo de programas de fidelidade
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**: Referência rápida de comandos

## 🎓 Para Estudar

1. **Estrutura modular**: Leia [REFACTORING.md](REFACTORING.md)
2. **Como testar**: Leia [TESTING.md](TESTING.md)
3. **Filtros de busca**: Leia [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)
4. **Formatação de datas**: Veja `app/core/models.py → get_dates_grouped_dict()`
5. **Templates Jinja2**: Veja `templates/padrao_whatsapp.j2`

---

**Versão:** 4.0 (Modular Architecture)  
**Python:** 3.8+
