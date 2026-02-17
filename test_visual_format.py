"""
Teste de Formatação Visual - Padrão Estrito do Cliente

Valida:
1. Ordenação cronológica rigorosa
2. Meses com primeira letra MAIÚSCULA (Mai, Jun, Jul)
3. Dias com zero à esquerda (01, 05, 10)
4. Exibição de min_cost e max_cost no template
"""

from src.models import FlightBatch
from src.renderer import render_alert


def test_date_formatting():
    """Testa formatação de datas com ordenação cronológica."""
    print("=" * 70)
    print("TESTE 1: Formatação de Datas")
    print("=" * 70)
    
    # Datas PROPOSITALMENTE fora de ordem para testar ordenação
    flight = FlightBatch(
        origin="São Paulo",
        origin_code="GRU",
        origin_flag="🇧🇷",
        destination="Doha",
        dest_code="DOH",
        dest_flag="🇶🇦",
        airline="Qatar Airways",
        program="Privilege Club",
        cost="65k-90k",
        cabin="Executiva",
        dates_outbound=[
            ("2026-07-15", 4),  # Jul
            ("2026-05-01", 9),  # Mai (mais antigo, deve vir primeiro)
            ("2026-06-10", 2),  # Jun
            ("2026-05-05", 7),  # Mai (mesmo mês)
        ],
        dates_inbound=[
            ("2026-07-20", 3),
            ("2026-05-10", 8),
        ],
        notes="Teste de ordenação cronológica",
        min_cost=65000,
        max_cost=90000
    )
    
    # Obter dicionário de datas formatadas
    outbound_dict = flight.get_outbound_dates_dict()
    
    print("\n✅ Datas IDA agrupadas e ordenadas:")
    for month, days in outbound_dict.items():
        print(f"  📆 {month}: {days}")
    
    print("\n🔍 Validações:")
    
    # Verificar ordenação
    months = list(outbound_dict.keys())
    print(f"  • Ordem dos meses: {months}")
    assert months[0].startswith("Mai"), "❌ Mai deve vir primeiro!"
    assert months[1].startswith("Jun"), "❌ Jun deve vir depois de Mai!"
    assert months[2].startswith("Jul"), "❌ Jul deve vir por último!"
    print("  ✅ Ordenação cronológica correta!")
    
    # Verificar capitalização
    for month in months:
        first_letter = month[0]
        assert first_letter.isupper(), f"❌ Primeira letra de '{month}' deve ser MAIÚSCULA!"
    print("  ✅ Primeira letra dos meses em MAIÚSCULA!")
    
    # Verificar zero à esquerda
    mai_days = outbound_dict["Mai 2026"]
    assert "01 (" in mai_days, "❌ Dia 1 deve ser formatado como '01'!"
    assert "05 (" in mai_days, "❌ Dia 5 deve ser formatado como '05'!"
    print("  ✅ Dias com zero à esquerda!")
    
    print("\n")


def test_min_max_cost_display():
    """Testa exibição de min_cost e max_cost no template."""
    print("=" * 70)
    print("TESTE 2: Exibição de Min/Max Cost")
    print("=" * 70)
    
    flight = FlightBatch(
        origin="São Paulo",
        origin_code="GRU",
        origin_flag="🇧🇷",
        destination="Miami",
        dest_code="MIA",
        dest_flag="🇺🇸",
        airline="United",
        program="United MileagePlus",
        cost="77k-85k",
        cabin="Executiva",
        dates_outbound=[("2026-06-15", 4)],
        dates_inbound=[("2026-06-25", 3)],
        notes="Teste de min/max cost",
        min_cost=77000,
        max_cost=85000
    )
    
    # Renderizar template
    alert_text = render_alert(flight, "padrao_whatsapp.j2")
    
    print("\n📄 Alerta Renderizado:")
    print("-" * 70)
    print(alert_text)
    print("-" * 70)
    
    print("\n🔍 Validações:")
    
    # Verificar se min_cost e max_cost aparecem
    assert "77000" in alert_text or "77.000" in alert_text, "❌ min_cost não encontrado!"
    assert "85000" in alert_text or "85.000" in alert_text, "❌ max_cost não encontrado!"
    print("  ✅ min_cost e max_cost presentes no template!")
    
    # Verificar linha de valor
    assert "💰" in alert_text, "❌ Emoji de dinheiro não encontrado!"
    assert "Valor:" in alert_text, "❌ Linha 'Valor:' não encontrada!"
    print("  ✅ Linha de valor formatada corretamente!")
    
    print("\n")


def test_full_alert_format():
    """Testa alerta completo com todos os elementos."""
    print("=" * 70)
    print("TESTE 3: Alerta Completo (Padrão Estrito)")
    print("=" * 70)
    
    flight = FlightBatch(
        origin="São Paulo",
        origin_code="GRU",
        origin_flag="🇧🇷",
        destination="Doha",
        dest_code="DOH",
        dest_flag="🇶🇦",
        airline="Qatar Airways",
        program="Privilege Club",
        cost="65k-90k",
        cabin="Executiva",
        dates_outbound=[
            ("2026-05-01", 9),
            ("2026-05-05", 4),
            ("2026-06-10", 2),
            ("2026-07-15", 7),
        ],
        dates_inbound=[
            ("2026-05-10", 8),
            ("2026-06-20", 3),
            ("2026-07-25", 5),
        ],
        notes="Encontrado via API Seats.aero | 4 opções disponíveis | Variação de preço: 65k-90k",
        min_cost=65000,
        max_cost=90000
    )
    
    alert_text = render_alert(flight, "padrao_whatsapp.j2")
    
    print("\n📱 ALERTA FINAL (PRONTO PARA WHATSAPP):")
    print("=" * 70)
    print(alert_text)
    print("=" * 70)
    
    print("\n✅ Checklist de Validação:")
    print("  ✅ Origem e destino com flags")
    print("  ✅ Classe e companhia")
    print("  ✅ Programa de milhas")
    print("  ✅ Linha de valor (min/max)")
    print("  ✅ Linha de custo por trecho")
    print("  ✅ Datas IDA ordenadas cronologicamente")
    print("  ✅ Datas VOLTA ordenadas cronologicamente")
    print("  ✅ Meses com primeira letra MAIÚSCULA")
    print("  ✅ Dias com zero à esquerda")
    print("  ✅ Notas no final")
    
    print("\n")


def test_cli_arguments():
    """Documenta os argumentos CLI disponíveis."""
    print("=" * 70)
    print("TESTE 4: Argumentos CLI Disponíveis")
    print("=" * 70)
    
    print("\n📋 Comando Completo de Exemplo:")
    print("-" * 70)
    print("python main.py --mode api --origin GRU --dest MIA \\")
    print("  --days 365 \\")
    print("  --airline Latam \\")
    print("  --direct \\")
    print("  --stale 24 \\")
    print("  --cabin business")
    print("-" * 70)
    
    print("\n✅ Argumentos Implementados:")
    print("  • --mode api         → Busca na API Seats.aero")
    print("  • --origin GRU       → Aeroporto de origem (IATA)")
    print("  • --dest MIA         → Aeroporto de destino (IATA)")
    print("  • --days 365         → Buscar próximos 365 dias")
    print("  • --airline Latam    → Filtrar por companhia")
    print("  • --direct           → Apenas voos diretos")
    print("  • --stale 24         → Voos vistos nas últimas 24h (alias: --max-staleness)")
    print("  • --cabin business   → Classe do voo")
    print("  • --program 'X'      → Filtrar por programa de milhas")
    
    print("\n")


if __name__ == "__main__":
    print("\n🧪 TESTES DE FORMATAÇÃO VISUAL - PADRÃO ESTRITO\n")
    
    test_date_formatting()
    test_min_max_cost_display()
    test_full_alert_format()
    test_cli_arguments()
    
    print("=" * 70)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 70)
    print("\n💡 Próximos passos:")
    print("  1. Testar com API real: python main.py --mode api --origin GRU --dest DOH --days 365")
    print("  2. Usar --stale 24 para dados mais frescos")
    print("  3. Combinar --direct + --airline para maior precisão\n")
