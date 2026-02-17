# 🎯 Guia Rápido - Como Usar o Mileage Bot

## Passo a Passo Completo

### 1️⃣ Setup Inicial (apenas uma vez)

```bash
# Clone ou navegue até o projeto
cd mileage-bot

# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 2️⃣ Rodando o Projeto

```bash
# Com o venv ativado, simplesmente rode:
python main.py
```

### 3️⃣ O que você vai ver

O script `main.py` vai:

1. **Criar dados de teste** (GRU-MIA, Latam, várias datas em 2026)
2. **Renderizar o alerta** usando o template WhatsApp
3. **Mostrar 4 seções no terminal:**
   - 📦 Tabela com os dados do FlightBatch
   - 📱 Painel com o alerta formatado (pronto para copiar!)
   - 🔍 Tabela validando como as datas foram agrupadas
   - 📊 Estatísticas do alerta gerado

### 4️⃣ Exemplo de Output

```
======================================================================
  🛫 MILEAGE BOT - Gerador de Alertas de Passagens
======================================================================

✈️ GRU - MIA
🚨 Classe Executiva - Latam

🌎 Programa: Privilege Club
💰 77k Avios + taxas

Ida:
📆 Fev 2026: 15 (Dom), 18 (Qua), 22 (Dom)
📆 Mar 2026: 01 (Dom), 05 (Qui), 12 (Qui)

Volta:
📆 Fev 2026: 20 (Sex), 25 (Qua)
📆 Mar 2026: 10 (Ter), 15 (Dom), 20 (Sex)

💡 Taxas em torno de R$ 600. Melhor disponibilidade às quartas e quintas.
```

### 5️⃣ Testando com seus próprios dados

Edite o arquivo `main.py` e modifique o objeto `FlightBatch`:

```python
flight = FlightBatch(
    route="GRU - LIS",           # Sua rota
    airline="TAP",               # Sua companhia
    program="TAP Miles&Go",      # Seu programa
    cost="50k Avios",            # Seu custo
    cabin="Econômica",           # Sua classe
    dates_outbound=["2026-04-10", "2026-04-12"],  # Suas datas
    dates_inbound=["2026-04-20", "2026-04-25"],
    notes="Suas observações aqui"
)
```

Depois rode novamente:
```bash
python main.py
```

---

## 🛠️ Arquivos Importantes

| Arquivo | O que faz |
|---------|-----------|
| `main.py` | Script principal - comece aqui! |
| `src/models.py` | Classe FlightBatch + lógica de formatação de datas |
| `src/renderer.py` | Função render_alert que usa Jinja2 |
| `templates/padrao_whatsapp.j2` | Layout do alerta WhatsApp |

---

## 🎓 Entendendo o Fluxo

```
1. main.py cria um FlightBatch
       ⬇️
2. Chama render_alert(flight, "padrao_whatsapp.j2")
       ⬇️
3. renderer.py carrega o template Jinja2
       ⬇️
4. FlightBatch formata as datas (get_outbound_dates_dict)
       ⬇️
5. Jinja2 substitui {{ variáveis }} e executa {% loops %}
       ⬇️
6. Retorna texto final formatado
       ⬇️
7. Rich exibe bonito no terminal
```

---

## ❓ Troubleshooting

**Erro: "ModuleNotFoundError: No module named 'arrow'"**
- Solução: Ative o venv e instale: `pip install -r requirements.txt`

**Erro: "jinja2.exceptions.TemplateNotFound"**
- Solução: Rode o script da raiz do projeto: `python main.py`

**Datas não estão em português**
- Verifique se a lib arrow está instalada corretamente
- O locale `pt_BR` deve funcionar automaticamente

---

## 📚 Próximos Passos

- [ ] Criar mais templates (Telegram, Email)
- [ ] Ler dados de arquivos JSON em `data/`
- [ ] Adicionar CLI com argparse
- [ ] Integrar com APIs de programas de milhas
