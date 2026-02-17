"""
Exemplo de uso da classe FlightBatch

Este arquivo demonstra como criar e usar um alerta de voo.
Execute: python -m src.example
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.models import FlightBatch

# Instância do Rich Console para prints bonitos
console = Console()


def main():
    """Demonstração do FlightBatch com dados reais."""
    
    # Criando um exemplo de alerta de voo
    flight = FlightBatch(
        route="GRU - MIA",
        airline="Latam",
        program="Privilege Club",
        cost="77k Avios",
        cabin="Executiva",
        dates_outbound=[
            "2026-02-15",
            "2026-02-18",
            "2026-02-22",
            "2026-03-01",
            "2026-03-05"
        ],
        dates_inbound=[
            "2026-02-20",
            "2026-02-25",
            "2026-03-10",
            "2026-03-15"
        ],
        notes="Taxas em torno de R$ 600. Melhor disponibilidade às quartas."
    )
    
    # Mostrando informações básicas com Rich
    console.print("\n[bold cyan]🛫 Alerta de Passagens com Milhas[/bold cyan]\n")
    
    # Criando tabela de informações
    table = Table(title="Detalhes do Voo", show_header=True, header_style="bold magenta")
    table.add_column("Campo", style="cyan", width=20)
    table.add_column("Valor", style="white")
    
    table.add_row("Rota", flight.route)
    table.add_row("Companhia", flight.airline)
    table.add_row("Programa", flight.program)
    table.add_row("Custo", flight.cost)
    table.add_row("Classe", flight.cabin)
    
    console.print(table)
    
    # Mostrando datas formatadas
    console.print("\n[bold green]📅 Datas Disponíveis:[/bold green]\n")
    
    outbound_formatted = flight.get_formatted_outbound_dates()
    inbound_formatted = flight.get_formatted_inbound_dates()
    
    console.print(Panel(
        f"[bold]IDA:[/bold]\n{outbound_formatted}\n\n"
        f"[bold]VOLTA:[/bold]\n{inbound_formatted}",
        title="Datas Agrupadas por Mês",
        border_style="green"
    ))
    
    # Mostrando notas
    console.print(f"\n[bold yellow]💡 Dica:[/bold yellow] {flight.notes}\n")


if __name__ == "__main__":
    main()
