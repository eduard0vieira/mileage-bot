"""
Mileage Bot - Main Entry Point

Script para gerar alertas de passagens a partir de input.txt.
Suporta múltiplos voos separados por '---'.
Execute: python main.py
"""

from rich.console import Console
from src.importer import parse_file_batch
from src.renderer import render_alert


def main():
    console = Console()
    
    # Banner
    console.print("\n" + "=" * 70)
    console.print("🛫 MILEAGE BOT - Gerador de Alertas de Passagens")
    console.print("=" * 70 + "\n")
    
    # Ler arquivo
    console.print("[bold yellow]📄 Lendo input.txt...[/bold yellow]\n")
    
    try:
        batches = parse_file_batch("input.txt")
        console.print(f"[bold green]✅ {len(batches)} voo(s) encontrado(s)![/bold green]\n")
    except FileNotFoundError:
        console.print("[bold red]❌ Arquivo 'input.txt' não encontrado![/bold red]\n")
        return
    except ValueError as e:
        console.print(f"[bold red]❌ Erro ao parsear:[/bold red] {e}\n")
        return
    
    # Processar cada voo
    for i, batch in enumerate(batches, 1):
        console.print(f"[bold cyan]🎯 Processando voo {i}/{len(batches)}...[/bold cyan]")
        console.print(f"  • Rota: {batch.origin_code} → {batch.dest_code}")
        console.print(f"  • Cia: {batch.airline}")
        
        # Enriquecer dados
        try:
            batch.enrich_airport_data()
            console.print(f"  • Origem: {batch.origin} {batch.origin_flag}")
            console.print(f"  • Destino: {batch.destination} {batch.dest_flag}\n")
        except Exception as e:
            console.print(f"[bold red]❌ Erro ao enriquecer:[/bold red] {e}\n")
            continue
        
        # Renderizar
        try:
            alert_text = render_alert(batch, "padrao_whatsapp.j2")
        except Exception as e:
            console.print(f"[bold red]❌ Erro ao renderizar:[/bold red] {e}\n")
            continue
        
        # Mostrar resultado
        console.print("╔" + "═" * 68 + "╗")
        console.print(f"║  [bold]VOO {i}[/bold] - {batch.route} {' ' * (52 - len(batch.route))}║")
        console.print("╠" + "═" * 68 + "╣")
        console.print("║" + " " * 68 + "║")
        
        # Imprimir o alerta (texto puro)
        for line in alert_text.split('\n'):
            # Limita a 66 chars para caber na caixa
            console.print(f"║ {line[:66]:<66} ║")
        
        console.print("║" + " " * 68 + "║")
        console.print("╚" + "═" * 68 + "╝")
        console.print()
        
        # Separador entre voos (exceto no último)
        if i < len(batches):
            console.print("[dim]" + "·" * 70 + "[/dim]")
            console.print()
    
    # Resumo final
    console.print("=" * 70)
    console.print(f"✅ {len(batches)} alerta(s) gerado(s) com sucesso!")
    console.print("=" * 70)
    console.print("\n[bold cyan]💡 DICA:[/bold cyan]")
    console.print("Copie cada alerta individualmente (dentro das caixas)")
    console.print("Para adicionar mais voos, separe com '---' no input.txt\n")


if __name__ == "__main__":
    main()
