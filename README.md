# Mileage Bot - Flight Alert Formatter 🛫

CLI para formatação de alertas de passagens aéreas com milhas/pontos.

## 📁 Estrutura do Projeto

```
mileage-bot/
├── main.py           # 🎯 Script principal - COMECE AQUI!
├── requirements.txt  # Dependências do projeto
├── README.md
├── src/              # Código fonte principal
│   ├── __init__.py
│   ├── models.py     # Classe FlightBatch e lógica de datas
│   ├── renderer.py   # Função render_alert com Jinja2
│   └── example.py    # Exemplos de uso
├── templates/        # Templates Jinja2 (.j2) para alertas
│   ├── padrao_whatsapp.j2   # Template principal
│   └── alert_telegram.j2    # Template alternativo
└── data/             # Arquivos JSON com dados de voos
    └── example.json  # Exemplo de estrutura
```

## 🚀 Setup e Execução

1. **Criar ambiente virtual (boa prática!):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

2. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Rodar o script principal:**
   ```bash
   python main.py
   ```
   
   Isso vai:
   - Criar um FlightBatch com dados de teste
   - Renderizar o alerta usando o template WhatsApp
   - Exibir o resultado formatado no terminal

## 📦 Dependências

- **jinja2**: Template engine para gerar os textos dos alertas
- **arrow**: Biblioteca moderna para manipulação de datas (melhor que datetime nativo)
- **rich**: Para prints coloridos e formatados no terminal

## 🔧 Como Funciona

A classe `FlightBatch` representa um lote de voos disponíveis com:
- Origem e destino separados (ex: "São Paulo" → "Miami")
- Companhia aérea, programa de fidelidade
- Custo em milhas e classe de voo
- Listas de datas com **assentos disponíveis** (ex: `("2026-02-15", 9)`)
- Notas/dicas extras

O método `format_dates_by_month()` agrupa as datas automaticamente:
- **Entrada:** `[("2026-02-15", 9), ("2026-02-18", 4), ("2026-03-01", 2)]`
- **Saída:** `"Fev 2026: 15 (9), 18 (4) | Mar 2026: 01 (2)"`
- **Número entre parênteses:** quantidade de assentos disponíveis

## 🎯 Próximos Passos

- [ ] Criar templates Jinja2 em `templates/`
- [ ] Criar CLI principal com argparse ou typer
- [ ] Adicionar exemplos de JSONs em `data/`
- [ ] Implementar formatação de alertas
