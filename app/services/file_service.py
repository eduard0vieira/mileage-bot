"""
File Service - Importador de arquivos input.txt

Este módulo é responsável por ler e parsear arquivos no formato input.txt
e transformá-los em objetos FlightBatch.
"""

from typing import List, Tuple
import re
from app.core.models import FlightBatch


# Mapeamento de meses PT->EN
MONTH_MAP = {
    'Jan': 'Jan', 'Fev': 'Feb', 'Mar': 'Mar', 'Abr': 'Apr',
    'Mai': 'May', 'Jun': 'Jun', 'Jul': 'Jul', 'Ago': 'Aug',
    'Set': 'Sep', 'Out': 'Oct', 'Nov': 'Nov', 'Dez': 'Dec'
}

MONTH_TO_NUM = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}


def parse_date_block(text_block: str) -> List[Tuple[str, int]]:
    """
    Parseia bloco de datas formato cliente:
    Mar 2026: 31 (1)
    Abr 2026: 05 (5), 24 (7)
    """
    dates = []
    lines = text_block.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Regex: "Mar 2026: 31 (1), 05 (2)"
        match = re.match(r'(\w+)\s+(\d{4}):\s*(.+)', line)
        if not match:
            continue
        
        month_pt, year, days_str = match.groups()
        
        # Converte mês PT->EN
        month_en = MONTH_MAP.get(month_pt, month_pt)
        month_num = MONTH_TO_NUM.get(month_en, 1)
        
        # Parseia dias: "31 (1), 05 (2)"
        day_matches = re.findall(r'(\d+)\s*\((\d+)\)', days_str)
        
        for day_str, seats_str in day_matches:
            day = int(day_str)
            seats = int(seats_str)
            date_iso = f"{year}-{month_num:02d}-{day:02d}"
            dates.append((date_iso, seats))
    
    return dates


def parse_dates_string(dates_str: str) -> List[Tuple[str, int]]:
    """
    Parseia datas. Detecta automaticamente o formato:
    - Formato antigo: "2026-02-15=9, 2026-02-18=4"
    - Formato novo: 
        Mar 2026: 31 (1)
        Abr 2026: 05 (5), 24 (7)
    """
    dates_str = dates_str.strip()
    
    # Detecta formato novo: tem quebra de linha OU padrão "Mês YYYY:"
    if '\n' in dates_str or re.search(r'\w+\s+\d{4}:', dates_str):
        return parse_date_block(dates_str)
    else:
        # Formato antigo
        return parse_dates_string_old(dates_str)


def parse_dates_string_old(dates_str: str) -> List[Tuple[str, int]]:
    """Formato antigo: "2026-02-15=9, 2026-02-18=4" """
    dates = []
    parts = dates_str.split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        if '=' not in part:
            raise ValueError(f"Formato inválido: '{part}'. Esperado: 'YYYY-MM-DD=N'")
        
        date_str, seats_str = part.split('=', 1)
        date_str = date_str.strip()
        seats_str = seats_str.strip()
        
        if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
            raise ValueError(f"Data inválida: '{date_str}'. Esperado: YYYY-MM-DD")
        
        seats = int(seats_str)
        if seats < 0:
            raise ValueError(f"Assentos negativo: {seats}")
        
        dates.append((date_str, seats))
    
    if not dates:
        raise ValueError("Nenhuma data válida")
    
    return dates


def parse_file(filepath: str) -> FlightBatch:
    """
    Lê arquivo input.txt e retorna UM FlightBatch.
    Para múltiplos voos, use parse_file_batch().
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return parse_flight_block(content)


def parse_file_batch(filepath: str) -> List[FlightBatch]:
    """
    Lê arquivo com MÚLTIPLOS voos separados por '---'.
    Retorna List[FlightBatch].
    
    Exemplo de input.txt:
    ```
    ROUTE: GRU MIA
    AIRLINE: Latam
    ...
    ---
    ROUTE: GIG LIS
    AIRLINE: TAP
    ...
    ```
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Divide por separador ---
    blocks = content.split('---')
    
    batches = []
    for i, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
        
        try:
            batch = parse_flight_block(block)
            batches.append(batch)
        except Exception as e:
            raise ValueError(f"Erro no bloco {i+1}: {e}")
    
    if not batches:
        raise ValueError("Nenhum voo encontrado no arquivo")
    
    return batches


def parse_flight_block(content: str) -> FlightBatch:
    """
    Parseia um bloco de texto representando UM voo.
    Usado por parse_file() e parse_file_batch().
    """
    data = {}
    
    # Regex: CHAVE: valor (multilinha até próxima CHAVE)
    pattern = r'([A-Z_]+):\s*((?:(?![A-Z_]+:).)*)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for key, value in matches:
        key = key.strip().upper()
        value = value.strip()
        if value:
            data[key] = value
    
    # Valida campos
    required = ['ROUTE', 'AIRLINE', 'PROGRAM', 'COST', 'CABIN', 'NOTE', 'DATES_OUT', 'DATES_IN']
    missing = [f for f in required if f not in data]
    if missing:
        raise ValueError(f"Campos faltando: {', '.join(missing)}")
    
    # Parse ROUTE
    route_parts = data['ROUTE'].split()
    if len(route_parts) != 2:
        raise ValueError(f"ROUTE deve ter 2 códigos IATA: {data['ROUTE']}")
    origin_code, dest_code = route_parts
    
    # Parse DATES (suporta ambos formatos)
    dates_outbound = parse_dates_string(data['DATES_OUT'])
    dates_inbound = parse_dates_string(data['DATES_IN'])
    
    # Cria FlightBatch
    return FlightBatch(
        origin="",
        origin_code=origin_code,
        origin_flag="",
        destination="",
        dest_code=dest_code,
        dest_flag="",
        airline=data['AIRLINE'],
        program=data['PROGRAM'],
        cost=data['COST'],
        cabin=data['CABIN'],
        dates_outbound=dates_outbound,
        dates_inbound=dates_inbound,
        notes=data['NOTE']
    )


def main():
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    console.print("\n[bold cyan]📄 Testando parse_file_batch()[/bold cyan]\n")
    
    try:
        batches = parse_file_batch("input.txt")
        console.print(f"[bold green]✅ {len(batches)} voo(s) parseado(s)![/bold green]\n")
        
        for i, batch in enumerate(batches, 1):
            console.print(f"[bold yellow]Voo {i}:[/bold yellow]")
            
            table = Table()
            table.add_column("Campo", style="cyan")
            table.add_column("Valor")
            
            table.add_row("Origin", batch.origin_code)
            table.add_row("Dest", batch.dest_code)
            table.add_row("Airline", batch.airline)
            table.add_row("Program", batch.program)
            table.add_row("Dates Out", f"{len(batch.dates_outbound)} datas")
            table.add_row("Dates In", f"{len(batch.dates_inbound)} datas")
            
            console.print(table)
            
            batch.enrich_airport_data()
            console.print(f"✅ {batch.origin} → {batch.destination}\n")
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]\n")


if __name__ == "__main__":
    main()
