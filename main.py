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
        console.print(f"  • Cia: {batch.airline}\n")
        
        # Enriquecer dados
        try:
            batch.enrich_airport_data()
        except Exception as e:
            console.print(f"[bold red]❌ Erro ao enriquecer:[/bold red] {e}\n")
            continue
        
        # Renderizar
        try:
            alert_text = render_alert(batch, "padrao_whatsapp.j2")
        except Exception as e:
            console.print(f"[bold red]❌ Erro ao renderizar:[/bold red] {e}\n")
            continue
        
        # Separador antes do alerta
        print("." * 70)
        
        # Imprimir alerta (TEXTO PURO - sem bordas)
        print(alert_text)
        
        # Separador depois do alerta
        print("." * 70)
        print()
    
    # Resumo final
    console.print("=" * 70)
    console.print(f"✅ {len(batches)} alerta(s) gerado(s) com sucesso!")
    console.print("=" * 70)
    console.print("\n[bold cyan]💡 DICA:[/bold cyan]")
    console.print("Selecione cada alerta entre os separadores de pontos")
    console.print("Para adicionar mais voos, separe com '---' no input.txt\n")


if __name__ == "__main__":
    main()
