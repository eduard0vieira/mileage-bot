"""
Mileage Bot - Main Entry Point

CLI para gerar alertas de passagens.
Modos: 'file' (lê input.txt) ou 'api' (busca em Seats.aero)

Execute: 
  python main.py                           # Modo file (padrão)
  python main.py --mode api --origin GRU --dest MIA
"""

import argparse
from datetime import datetime, timedelta
from rich.console import Console
from src.importer import parse_file_batch
from src.renderer import render_alert
from src.seats_client import SeatsAeroClient


def mode_file(console: Console):
    """Modo FILE: Lê input.txt e gera alertas."""
    
    console.print("[bold yellow]📄 Modo FILE - Lendo input.txt...[/bold yellow]\n")
    
    try:
        batches = parse_file_batch("input.txt")
        console.print(f"[bold green]✅ {len(batches)} voo(s) encontrado(s)![/bold green]\n")
    except FileNotFoundError:
        console.print("[bold red]❌ Arquivo 'input.txt' não encontrado![/bold red]\n")
        return
    except ValueError as e:
        console.print(f"[bold red]❌ Erro ao parsear:[/bold red] {e}\n")
        return
    
    render_batches(console, batches)


def mode_api(console: Console, origin: str, dest: str, days: int, cabin: str):
    """Modo API: Busca em Seats.aero e gera alertas."""
    
    console.print(f"[bold yellow]🔌 Modo API - Buscando em Seats.aero...[/bold yellow]\n")
    console.print(f"  • Origem: {origin}")
    console.print(f"  • Destino: {dest}")
    console.print(f"  • Período: Próximos {days} dias")
    console.print(f"  • Classe: {cabin}\n")
    
    # Calcular range de datas
    date_start = datetime.now().date()
    date_end = date_start + timedelta(days=days)
    
    # Buscar na API
    try:
        console.print("[cyan]🔍 Conectando à API...[/cyan]\n")
        
        with SeatsAeroClient() as client:
            results = client.search_availability(
                origin=origin,
                destination=dest,
                date_start=date_start.isoformat(),
                date_end=date_end.isoformat(),
                cabin_class=cabin
            )
        
        console.print(f"[green]✅ Busca realizada![/green]\n")
        
        # Verificar se results é lista ou dict com chave 'data'/'results'
        if isinstance(results, dict):
            # API pode retornar {"data": [...], "meta": {...}}
            flights_list = results.get('data', results.get('results', results.get('flights', [])))
        else:
            flights_list = results
        
        if not flights_list:
            console.print("[bold yellow]⚠️  Nenhum voo encontrado com esses filtros.[/bold yellow]")
            console.print("\n💡 Dica: Tente:")
            console.print("  • Aumentar o período (--days 90)")
            console.print("  • Mudar a classe (--cabin economy)")
            console.print("  • Tentar outra rota\n")
            return
        
        console.print(f"[green]✅ {len(flights_list)} voo(s) encontrado(s) na API[/green]\n")
        
        # Processar e agrupar
        console.print("[cyan]🔄 Processando e agrupando...[/cyan]\n")
        batches = SeatsAeroClient.process_search_results(flights_list)
        
        if not batches:
            console.print("[bold yellow]⚠️  Nenhum batch criado após processamento.[/bold yellow]\n")
            return
        
        console.print(f"[green]✅ Agrupados em {len(batches)} batch(es)![/green]\n")
        
        render_batches(console, batches)
        
    except ValueError as e:
        console.print(f"[bold red]{e}[/bold red]\n")
        return
    except ConnectionError as e:
        console.print(f"[bold red]{e}[/bold red]\n")
        return
    except Exception as e:
        console.print(f"[bold red]❌ Erro inesperado: {e}[/bold red]\n")
        return


def render_batches(console: Console, batches: list):
    """Renderiza e imprime todos os batches."""
    
    for i, batch in enumerate(batches, 1):
        console.print(f"[bold cyan]🎯 Processando voo {i}/{len(batches)}...[/bold cyan]")
        console.print(f"  • Rota: {batch.origin_code} → {batch.dest_code}")
        console.print(f"  • Cia: {batch.airline}")
        
        # Se ainda não foi enriquecido, enriquecer agora
        if not batch.origin:
            try:
                batch.enrich_airport_data()
            except Exception as e:
                console.print(f"[red]⚠️  Erro ao enriquecer: {e}[/red]")
        
        console.print()
        
        # Renderizar
        try:
            alert_text = render_alert(batch, "padrao_whatsapp.j2")
        except Exception as e:
            console.print(f"[bold red]❌ Erro ao renderizar:[/bold red] {e}\n")
            continue
        
        # Separador e texto puro
        print("." * 70)
        print(alert_text)
        print("." * 70)
        print()
    
    # Resumo final
    console.print("=" * 70)
    console.print(f"✅ {len(batches)} alerta(s) gerado(s) com sucesso!")
    console.print("=" * 70 + "\n")


def main():
    # Configurar argparse
    parser = argparse.ArgumentParser(
        description='Mileage Bot - Gerador de Alertas de Passagens',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py                                    # Lê input.txt (padrão)
  python main.py --mode api --origin GRU --dest MIA
  python main.py --mode api --origin GIG --dest LIS --days 90 --cabin economy
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['file', 'api'],
        default='file',
        help='Modo de operação: file (lê input.txt) ou api (busca Seats.aero)'
    )
    
    parser.add_argument(
        '--origin',
        type=str,
        help='Código IATA origem (ex: GRU) - Obrigatório no modo API'
    )
    
    parser.add_argument(
        '--dest',
        type=str,
        help='Código IATA destino (ex: MIA) - Obrigatório no modo API'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=60,
        help='Quantos dias para frente buscar (padrão: 60)'
    )
    
    parser.add_argument(
        '--cabin',
        choices=['economy', 'business', 'first'],
        default='business',
        help='Classe de cabine (padrão: business)'
    )
    
    args = parser.parse_args()
    
    console = Console()
    
    # Banner
    console.print("\n" + "=" * 70)
    console.print("🛫 MILEAGE BOT - Gerador de Alertas de Passagens")
    console.print("=" * 70 + "\n")
    
    # Validar argumentos para modo API
    if args.mode == 'api':
        if not args.origin or not args.dest:
            console.print("[bold red]❌ Modo API requer --origin e --dest![/bold red]\n")
            parser.print_help()
            return
        
        mode_api(console, args.origin, args.dest, args.days, args.cabin)
    else:
        mode_file(console)


if __name__ == "__main__":
    main()
