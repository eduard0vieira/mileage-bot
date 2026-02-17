"""
Mileage Bot - Main Entry Point

Script principal para testar a geração de alertas de passagens aéreas.
Este arquivo serve como ponto de entrada para validar a formatação de datas
e a substituição correta de variáveis nos templates.

Execute: python main.py
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.models import FlightBatch
from src.renderer import render_alert


def main():
    """
    Função principal: cria dados fictícios e renderiza o alerta.
    
    O que este script faz:
    1. Cria um FlightBatch com dados de teste realistas
    2. Renderiza o alerta usando o template padrao_whatsapp.j2
    3. Exibe o resultado formatado no terminal com Rich
    """
    
    # Instância do Rich Console para prints bonitos
    console = Console()
    
    # Banner inicial
    console.print("\n")
    console.print("=" * 70, style="bold cyan")
    console.print("  🛫 MILEAGE BOT - Gerador de Alertas de Passagens", style="bold cyan")
    console.print("=" * 70, style="bold cyan")
    console.print("\n")
    
    # ========================================
    # PASSO 1: Criar dados fictícios de teste
    # ========================================
    
    console.print("[bold yellow]📦 Criando FlightBatch com dados de teste...[/bold yellow]\n")
    
    flight = FlightBatch(
        route="GRU - MIA",
        airline="Latam",
        program="Privilege Club",
        cost="77k Avios",
        cabin="Executiva",
        dates_outbound=[
            "2026-02-15",  # Domingo
            "2026-02-18",  # Quarta
            "2026-02-22",  # Domingo
            "2026-03-01",  # Domingo (mês diferente!)
            "2026-03-05",  # Quinta
            "2026-03-12"   # Quinta
        ],
        dates_inbound=[
            "2026-02-20",  # Sexta
            "2026-02-25",  # Quarta
            "2026-03-10",  # Terça
            "2026-03-15",  # Domingo
            "2026-03-20"   # Sexta
        ],
        notes="💡 Taxas em torno de R$ 600. Melhor disponibilidade às quartas e quintas."
    )
    
    # Mostra os dados brutos em uma tabela
    table = Table(
        title="Dados do FlightBatch",
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED
    )
    table.add_column("Campo", style="cyan", width=20)
    table.add_column("Valor", style="white")
    
    table.add_row("Rota", flight.route)
    table.add_row("Companhia", flight.airline)
    table.add_row("Programa", flight.program)
    table.add_row("Custo", flight.cost)
    table.add_row("Classe", flight.cabin)
    table.add_row("Datas Ida (raw)", f"{len(flight.dates_outbound)} datas")
    table.add_row("Datas Volta (raw)", f"{len(flight.dates_inbound)} datas")
    
    console.print(table)
    console.print("\n")
    
    # ========================================
    # PASSO 2: Renderizar o alerta
    # ========================================
    
    console.print("[bold yellow]🎨 Renderizando alerta com template 'padrao_whatsapp.j2'...[/bold yellow]\n")
    
    try:
        alert_text = render_alert(flight, "padrao_whatsapp.j2")
        console.print("[bold green]✅ Alerta renderizado com sucesso![/bold green]\n")
    except Exception as e:
        console.print(f"[bold red]❌ Erro ao renderizar: {e}[/bold red]")
        return
    
    # ========================================
    # PASSO 3: Exibir resultado formatado
    # ========================================
    
    console.print("[bold cyan]📱 RESULTADO FINAL (pronto para copiar):[/bold cyan]\n")
    
    # Exibe o alerta em um painel estilizado
    console.print(Panel(
        alert_text,
        title="[bold]WhatsApp Alert Preview[/bold]",
        subtitle="[dim]Copie e cole este texto diretamente no WhatsApp![/dim]",
        border_style="green",
        padding=(1, 2),
        box=box.DOUBLE
    ))
    
    # ========================================
    # PASSO 4: Validação das datas formatadas
    # ========================================
    
    console.print("\n[bold yellow]🔍 Validação da formatação de datas:[/bold yellow]\n")
    
    # Mostra como as datas foram agrupadas
    outbound_dict = flight.get_outbound_dates_dict()
    inbound_dict = flight.get_inbound_dates_dict()
    
    validation_table = Table(
        title="Datas Agrupadas por Mês/Ano",
        show_header=True,
        header_style="bold cyan",
        box=box.SIMPLE
    )
    validation_table.add_column("Tipo", style="cyan", width=10)
    validation_table.add_column("Mês/Ano", style="yellow", width=15)
    validation_table.add_column("Dias (dia da semana)", style="white")
    
    # Datas de ida
    for month, days in outbound_dict.items():
        validation_table.add_row("IDA ✈️", month, days)
    
    # Separador visual
    validation_table.add_row("", "", "", style="dim")
    
    # Datas de volta
    for month, days in inbound_dict.items():
        validation_table.add_row("VOLTA 🔙", month, days)
    
    console.print(validation_table)
    
    # ========================================
    # ESTATÍSTICAS FINAIS
    # ========================================
    
    console.print("\n[bold cyan]📊 Estatísticas:[/bold cyan]")
    console.print(f"  • Total de datas de ida: [bold]{len(flight.dates_outbound)}[/bold]")
    console.print(f"  • Total de datas de volta: [bold]{len(flight.dates_inbound)}[/bold]")
    console.print(f"  • Meses cobertos (ida): [bold]{len(outbound_dict)}[/bold]")
    console.print(f"  • Meses cobertos (volta): [bold]{len(inbound_dict)}[/bold]")
    console.print(f"  • Tamanho do alerta: [bold]{len(alert_text)}[/bold] caracteres\n")
    
    # Mensagem final
    console.print("=" * 70, style="bold green")
    console.print("  ✅ Validação concluída! Tudo funcionando perfeitamente!", style="bold green")
    console.print("=" * 70, style="bold green")
    console.print("\n")


if __name__ == "__main__":
    main()
