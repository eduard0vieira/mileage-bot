"""
Mileage Bot - Main Entry Point

Script principal para gerar alertas de passagens aéreas a partir de arquivo.
Execute: python main.py
"""

from rich.console import Console
from src.importer import parse_file
from src.renderer import render_alert


def main():
    """
    Função principal: lê input.txt e gera o alerta formatado.
    
    Fluxo simplificado:
    1. Lê input.txt com parse_file()
    2. Preenche dados automaticamente com enrich_airport_data()
    3. Renderiza usando template padrao_whatsapp.j2
    4. Imprime texto puro (fácil de copiar!)
    """
    
    console = Console()
    
    # ========================================
    # BANNER
    # ========================================
    
    console.print("\n" + "=" * 70)
    console.print("🛫 MILEAGE BOT - Gerador de Alertas de Passagens")
    console.print("=" * 70 + "\n")
    
    # ========================================
    # PASSO 1: LER ARQUIVO INPUT.TXT
    # ========================================
    
    console.print("[bold yellow]📄 Lendo arquivo input.txt...[/bold yellow]\n")
    
    try:
        batch = parse_file("input.txt")
        console.print("[bold green]✅ Arquivo parseado com sucesso![/bold green]")
    except FileNotFoundError:
        console.print("[bold red]❌ Erro: Arquivo 'input.txt' não encontrado![/bold red]")
        console.print("\n💡 Dica: Crie um arquivo input.txt na raiz do projeto com o formato:")
        console.print("""
ROUTE: GRU MIA
AIRLINE: Latam
PROGRAM: Privilege Club
COST: 77k Avios
CABIN: Executiva
NOTE: Taxas em torno de R$ 600.
DATES_OUT: 2026-02-15=9, 2026-02-18=4
DATES_IN: 2026-02-20=6, 2026-02-25=9
        """)
        return
    except ValueError as e:
        console.print(f"[bold red]❌ Erro ao parsear arquivo:[/bold red] {e}")
        return
    
    console.print(f"  • Códigos IATA: {batch.origin_code} → {batch.dest_code}")
    console.print(f"  • Datas de ida: {len(batch.dates_outbound)} opções")
    console.print(f"  • Datas de volta: {len(batch.dates_inbound)} opções\n")
    
    # ========================================
    # PASSO 2: ENRIQUECER DADOS (MÁGICA!)
    # ========================================
    
    console.print("[bold cyan]🪄 Preenchendo cidades e bandeiras automaticamente...[/bold cyan]\n")
    
    try:
        batch.enrich_airport_data()
        console.print("[bold green]✅ Dados enriquecidos com sucesso![/bold green]")
        console.print(f"  • Origem: {batch.origin} ({batch.origin_code}) {batch.origin_flag}")
        console.print(f"  • Destino: {batch.destination} ({batch.dest_code}) {batch.dest_flag}")
        console.print(f"  • Rota completa: {batch.route}\n")
    except Exception as e:
        console.print(f"[bold red]❌ Erro ao enriquecer dados:[/bold red] {e}\n")
        return
    
    # ========================================
    # PASSO 3: RENDERIZAR ALERTA
    # ========================================
    
    console.print("[bold yellow]🎨 Renderizando alerta com template...[/bold yellow]\n")
    
    try:
        alert_text = render_alert(batch, "padrao_whatsapp.j2")
        console.print("[bold green]✅ Alerta renderizado com sucesso![/bold green]\n")
    except Exception as e:
        console.print(f"[bold red]❌ Erro ao renderizar:[/bold red] {e}\n")
        return
    
    # ========================================
    # PASSO 4: IMPRIMIR RESULTADO (SEM BORDAS)
    # ========================================
    
    console.print("=" * 70)
    console.print("📱 RESULTADO FINAL (copie o texto abaixo):")
    console.print("=" * 70 + "\n")
    
    # Texto puro, sem Panel ou bordas decorativas
    print(alert_text)
    
    console.print("\n" + "=" * 70)
    console.print("✅ Pronto! Selecione o texto acima e copie (Cmd+C / Ctrl+C)")
    console.print("=" * 70)
    
    # ========================================
    # DICA FINAL
    # ========================================
    
    console.print("\n[bold cyan]💡 DICA:[/bold cyan]")
    console.print("Para criar outro alerta, edite o [bold]input.txt[/bold] e rode novamente!")
    console.print("Você só precisa mudar os códigos IATA e as datas.\n")


if __name__ == "__main__":
    main()
