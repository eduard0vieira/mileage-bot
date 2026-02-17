"""
Test script for Seats.aero processing

Simulates API responses and tests the process_search_results method.
Execute: python test_seats_processing.py
"""

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from app.services.seats_client import SeatsAeroClient
from app.ui.renderer import render_alert


def main():
    console = Console()
    
    console.print("\n[bold cyan]🧪 Testando Processamento Seats.aero[/bold cyan]\n")
    
    # Simular resposta da API Seats.aero
    mock_api_response = [
        {
            "Origin": "GRU",
            "Destination": "MIA",
            "Airline": "United",
            "Source": "united",
            "Date": "2026-03-01",
            "RemainingSeats": 4,
            "MilesCost": 77000,
            "CabinClass": "business"
        },
        {
            "Origin": "GRU",
            "Destination": "MIA",
            "Airline": "United",
            "Source": "united",
            "Date": "2026-03-05",
            "RemainingSeats": 2,
            "MilesCost": 77000,
            "CabinClass": "business"
        },
        {
            "Origin": "GRU",
            "Destination": "MIA",
            "Airline": "United",
            "Source": "united",
            "Date": "2026-03-12",
            "RemainingSeats": 7,
            "MilesCost": 88000,
            "CabinClass": "business"
        },
        {
            "Origin": "GRU",
            "Destination": "MIA",
            "Airline": "Latam",
            "Source": "sms",
            "Date": "2026-03-15",
            "RemainingSeats": 9,
            "MilesCost": 65000,
            "CabinClass": "business"
        },
        {
            "Origin": "GIG",
            "Destination": "LIS",
            "Airline": "TAP",
            "Source": "tap",
            "Date": "2026-06-10",
            "RemainingSeats": 12,
            "MilesCost": 50000,
            "CabinClass": "economy"
        },
        {
            "Origin": "GIG",
            "Destination": "LIS",
            "Airline": "TAP",
            "Source": "tap",
            "Date": "2026-06-15",
            "RemainingSeats": 8,
            "MilesCost": 50000,
            "CabinClass": "economy"
        }
    ]
    
    console.print(f"[yellow]📊 Dados simulados: {len(mock_api_response)} voos da API[/yellow]\n")
    
    # Processar
    console.print("[cyan]🔄 Processando e agrupando...[/cyan]\n")
    batches = SeatsAeroClient.process_search_results(mock_api_response)
    
    console.print(f"[green]✅ Agrupados em {len(batches)} batch(es)![/green]\n")
    
    # Mostrar cada batch
    for i, batch in enumerate(batches, 1):
        console.print(f"[bold yellow]━━━ BATCH {i} ━━━[/bold yellow]")
        
        table = Table()
        table.add_column("Campo", style="cyan")
        table.add_column("Valor")
        
        table.add_row("Rota", f"{batch.origin} → {batch.destination}")
        table.add_row("Códigos", f"{batch.origin_code} → {batch.dest_code}")
        table.add_row("Companhia", batch.airline)
        table.add_row("Programa", batch.program)
        table.add_row("Custo", batch.cost)
        table.add_row("Classe", batch.cabin)
        table.add_row("Datas", f"{len(batch.dates_outbound)} opções")
        
        console.print(table)
        
        # Mostrar datas
        console.print("\n[dim]Datas disponíveis:[/dim]")
        for date_iso, seats in batch.dates_outbound:
            console.print(f"  • {date_iso} - {seats} assentos")
        
        console.print()
    
    # Renderizar alertas
    console.print("[bold cyan]📱 Gerando alertas...[/bold cyan]\n")
    
    for i, batch in enumerate(batches, 1):
        console.print("." * 70)
        alert = render_alert(batch, "padrao_whatsapp.j2")
        print(alert)
        console.print("." * 70)
        console.print()


if __name__ == "__main__":
    main()
