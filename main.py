"""
Mileage Bot - Main Entry Point

Script principal para testar a geração de alertas de passagens aéreas.
Execute: python main.py
"""

from rich.console import Console
from src.models import FlightBatch
from src.renderer import render_alert


def main():
    """
    Função principal: cria dados fictícios e renderiza o alerta.
    
    O que este script faz:
    1. Cria um FlightBatch com dados de teste realistas
    2. Renderiza o alerta usando o template padrao_whatsapp.j2
    3. Imprime o texto puro no console (fácil de copiar!)
    """
    
    console = Console()
    
    # Banner inicial simples
    console.print("\n" + "=" * 70)
    console.print("🛫 MILEAGE BOT - Gerador de Alertas de Passagens")
    console.print("=" * 70 + "\n")
    
    # ========================================
    # CRIAR DADOS DE TESTE
    # ========================================
    
    console.print("📦 Criando FlightBatch com dados de teste...\n")
    
    # Dados de teste com formato NOVO:
    # - origin e destination separados
    # - origin_code, origin_flag, dest_code, dest_flag
    # - dates como lista de tuplas (data, assentos)
    flight = FlightBatch(
        origin="São Paulo",
        origin_code="GRU",
        origin_flag="🇧🇷",
        destination="Miami",
        dest_code="MIA",
        dest_flag="🇺🇸",
        airline="Latam",
        program="Privilege Club",
        cost="77k Avios",
        cabin="Executiva",
        dates_outbound=[
            ("2026-02-15", 9),   # 9 assentos disponíveis
            ("2026-02-18", 4),   # 4 assentos disponíveis
            ("2026-02-22", 2),   # 2 assentos disponíveis
            ("2026-03-01", 7),   # Mês diferente
            ("2026-03-05", 3),
            ("2026-03-12", 5)
        ],
        dates_inbound=[
            ("2026-02-20", 6),
            ("2026-02-25", 9),
            ("2026-03-10", 4),
            ("2026-03-15", 2),
            ("2026-03-20", 8)
        ],
        notes="Taxas em torno de R$ 600. Melhor disponibilidade às quartas."
    )
    
    console.print(f"✅ Rota: {flight.route}")
    console.print(f"✅ Programa: {flight.program}")
    console.print(f"✅ Datas de ida: {len(flight.dates_outbound)} opções")
    console.print(f"✅ Datas de volta: {len(flight.dates_inbound)} opções\n")
    
    # ========================================
    # RENDERIZAR O ALERTA
    # ========================================
    
    console.print("🎨 Renderizando alerta com template 'padrao_whatsapp.j2'...\n")
    
    try:
        alert_text = render_alert(flight, "padrao_whatsapp.j2")
        console.print("✅ Alerta renderizado com sucesso!\n")
    except Exception as e:
        console.print(f"❌ Erro ao renderizar: {e}")
        return
    
    # ========================================
    # IMPRIMIR TEXTO PURO (SEM BORDAS)
    # ========================================
    
    console.print("=" * 70)
    console.print("📱 RESULTADO FINAL (copie o texto abaixo):")
    console.print("=" * 70 + "\n")
    
    # Imprime o texto puro, sem Panel ou bordas decorativas
    # Você pode selecionar e copiar diretamente!
    print(alert_text)
    
    console.print("\n" + "=" * 70)
    console.print("✅ Pronto! Copie o texto acima e cole no WhatsApp")
    console.print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
