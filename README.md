# Mileage Bot - Flight Alert Formatter 🛫

CLI para formatação de alertas de passagens aéreas com milhas/pontos.

## 📁 Estrutura do Projeto

```
mileage-bot/
├── src/              # Código fonte principal
│   └── models.py     # Definição das estruturas de dados
├── templates/        # Templates Jinja2 (.j2) para alertas
├── data/             # Arquivos JSON com dados de voos
├── requirements.txt  # Dependências do projeto
└── README.md
```

## 🚀 Setup

1. **Criar ambiente virtual (boa prática!):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

2. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

## 📦 Dependências

- **jinja2**: Template engine para gerar os textos dos alertas
- **arrow**: Biblioteca moderna para manipulação de datas (melhor que datetime nativo)
- **rich**: Para prints coloridos e formatados no terminal

## 🔧 Como Funciona

A classe `FlightBatch` representa um lote de voos disponíveis com:
- Rota, companhia aérea, programa de fidelidade
- Custo em milhas e classe de voo
- Listas de datas de ida e volta
- Notas/dicas extras

O método `format_dates_by_month()` agrupa as datas automaticamente:
- **Entrada:** `['2026-02-15', '2026-02-18', '2026-03-01']`
- **Saída:** `"Fev 2026: 15 (Sex), 18 (Seg) | Mar 2026: 01 (Dom)"`

## 🎯 Próximos Passos

- [ ] Criar templates Jinja2 em `templates/`
- [ ] Criar CLI principal com argparse ou typer
- [ ] Adicionar exemplos de JSONs em `data/`
- [ ] Implementar formatação de alertas
