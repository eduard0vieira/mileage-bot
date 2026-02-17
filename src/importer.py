"""
Importer for Flight Alert CLI

Módulo responsável por ler arquivos de input e converter em objetos FlightBatch.
"""

from pathlib import Path
from typing import List, Tuple
from src.models import FlightBatch


def parse_file(filepath: str) -> FlightBatch:
    """
    Lê um arquivo de texto e converte em objeto FlightBatch.
    
    Por que este parser existe?
    - Evita ter que editar código Python toda vez
    - Formato simples: CHAVE: valor
    - Fácil de criar múltiplos alertas (um arquivo por alerta)
    - Não programadores podem criar alertas!
    
    Formato esperado do arquivo:
    ```
    ROUTE: GRU MIA
    AIRLINE: Latam
    PROGRAM: Privilege Club
    COST: 77k Avios
    CABIN: Executiva
    NOTE: Taxas em torno de R$ 600.
    DATES_OUT: 2026-02-15=9, 2026-02-18=4
    DATES_IN: 2026-02-20=6
    ```
    
    Como funciona o parse:
    1. Lê o arquivo linha por linha
    2. Identifica a chave (ROUTE:, AIRLINE:, etc)
    3. Extrai o valor (tudo depois dos dois pontos)
    4. Para ROUTE: separa em origin_code e dest_code
    5. Para DATES_OUT/DATES_IN: parseia formato "data=assentos"
    6. Monta o objeto FlightBatch com campos vazios (origin, origin_flag, etc)
    7. Retorna o objeto (você deve chamar .enrich_airport_data() depois!)
    
    Args:
        filepath: Caminho para o arquivo de input (ex: "input.txt")
    
    Returns:
        Objeto FlightBatch preenchido (mas ainda precisa do enrich!)
    
    Exemplo:
        >>> batch = parse_file("input.txt")
        >>> batch.enrich_airport_data()  # Preenche cidades e bandeiras
        >>> alert = render_alert(batch, "padrao_whatsapp.j2")
    """
    # Dicionário para armazenar os valores parseados
    data = {}
    
    # Lê o arquivo
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parseia cada linha
    for line in lines:
        line = line.strip()  # Remove espaços/quebras de linha
        
        # Ignora linhas vazias ou comentários
        if not line or line.startswith('#'):
            continue
        
        # Separa chave e valor por ":"
        if ':' not in line:
            continue  # Linha mal formatada, ignora
        
        key, value = line.split(':', 1)  # Split com maxsplit=1 (só no primeiro :)
        key = key.strip().upper()        # Normaliza: "route" → "ROUTE"
        value = value.strip()            # Remove espaços extras
        
        data[key] = value
    
    # Valida que temos os campos obrigatórios
    required_fields = ['ROUTE', 'AIRLINE', 'PROGRAM', 'COST', 'CABIN', 'NOTE', 'DATES_OUT', 'DATES_IN']
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(f"Campos obrigatórios faltando no arquivo: {', '.join(missing)}")
    
    # Parse ROUTE: "GRU MIA" → origin_code="GRU", dest_code="MIA"
    route_parts = data['ROUTE'].split()
    if len(route_parts) != 2:
        raise ValueError(f"ROUTE deve ter exatamente 2 códigos IATA (ex: GRU MIA), encontrado: {data['ROUTE']}")
    origin_code, dest_code = route_parts
    
    # Parse DATES_OUT: "2026-02-15=9, 2026-02-18=4" → [("2026-02-15", 9), ("2026-02-18", 4)]
    dates_outbound = parse_dates_string(data['DATES_OUT'])
    
    # Parse DATES_IN: "2026-02-20=6, 2026-02-25=9" → [("2026-02-20", 6), ("2026-02-25", 9)]
    dates_inbound = parse_dates_string(data['DATES_IN'])
    
    # Cria o FlightBatch
    # IMPORTANTE: Deixa origin, origin_flag, destination, dest_flag vazios
    # Eles serão preenchidos pelo enrich_airport_data()!
    batch = FlightBatch(
        origin="",                    # Vazio - será preenchido pelo enrich
        origin_code=origin_code,      # Ex: "GRU"
        origin_flag="",               # Vazio - será preenchido pelo enrich
        destination="",               # Vazio - será preenchido pelo enrich
        dest_code=dest_code,          # Ex: "MIA"
        dest_flag="",                 # Vazio - será preenchido pelo enrich
        airline=data['AIRLINE'],      # Ex: "Latam"
        program=data['PROGRAM'],      # Ex: "Privilege Club"
        cost=data['COST'],            # Ex: "77k Avios"
        cabin=data['CABIN'],          # Ex: "Executiva"
        dates_outbound=dates_outbound,
        dates_inbound=dates_inbound,
        notes=data['NOTE']
    )
    
    return batch


def parse_dates_string(dates_str: str) -> List[Tuple[str, int]]:
    """
    Parseia string de datas no formato "data=assentos, data=assentos".
    
    Formato esperado:
    - "2026-02-15=9, 2026-02-18=4, 2026-02-22=2"
    - Separador entre datas: vírgula
    - Separador data/assentos: sinal de igual (=)
    
    Args:
        dates_str: String com datas no formato acima
    
    Returns:
        Lista de tuplas (data_iso, assentos)
        Exemplo: [("2026-02-15", 9), ("2026-02-18", 4)]
    
    Raises:
        ValueError: Se o formato estiver incorreto
    
    Exemplo:
        >>> parse_dates_string("2026-02-15=9, 2026-02-18=4")
        [("2026-02-15", 9), ("2026-02-18", 4)]
    """
    dates = []
    
    # Separa por vírgula
    parts = dates_str.split(',')
    
    for part in parts:
        part = part.strip()  # Remove espaços
        
        if not part:
            continue  # Ignora partes vazias
        
        # Separa data e assentos pelo "="
        if '=' not in part:
            raise ValueError(f"Formato inválido para data: '{part}'. Esperado: 'YYYY-MM-DD=N'")
        
        date_str, seats_str = part.split('=', 1)
        date_str = date_str.strip()
        seats_str = seats_str.strip()
        
        # Valida formato da data (básico)
        if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
            raise ValueError(f"Data inválida: '{date_str}'. Esperado formato: YYYY-MM-DD")
        
        # Converte assentos para inteiro
        try:
            seats = int(seats_str)
        except ValueError:
            raise ValueError(f"Número de assentos inválido: '{seats_str}'. Deve ser um número inteiro.")
        
        if seats < 0:
            raise ValueError(f"Número de assentos não pode ser negativo: {seats}")
        
        dates.append((date_str, seats))
    
    if not dates:
        raise ValueError("Nenhuma data válida encontrada")
    
    return dates


def main():
    """
    Exemplo de uso do importer.
    Execute: python -m src.importer
    """
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    console.print("\n[bold cyan]📄 Testando parse_file()[/bold cyan]\n")
    
    # Testa o parser com input.txt
    try:
        batch = parse_file("input.txt")
        
        console.print("[bold green]✅ Arquivo parseado com sucesso![/bold green]\n")
        
        # Mostra os dados parseados
        table = Table(title="Dados Parseados", show_header=True, header_style="bold magenta")
        table.add_column("Campo", style="cyan", width=20)
        table.add_column("Valor", style="white")
        
        table.add_row("Origin Code", batch.origin_code)
        table.add_row("Dest Code", batch.dest_code)
        table.add_row("Airline", batch.airline)
        table.add_row("Program", batch.program)
        table.add_row("Cost", batch.cost)
        table.add_row("Cabin", batch.cabin)
        table.add_row("Dates Out", f"{len(batch.dates_outbound)} datas")
        table.add_row("Dates In", f"{len(batch.dates_inbound)} datas")
        
        console.print(table)
        
        console.print("\n[bold yellow]⚠️  Nota:[/bold yellow]")
        console.print("Os campos origin, origin_flag, destination, dest_flag estão vazios.")
        console.print("Chame [bold]batch.enrich_airport_data()[/bold] para preenchê-los!\n")
        
        # Testa o enrich
        console.print("[bold cyan]🪄 Executando enrich_airport_data()...[/bold cyan]\n")
        batch.enrich_airport_data()
        
        console.print(f"✅ Origem: {batch.origin} ({batch.origin_code}) {batch.origin_flag}")
        console.print(f"✅ Destino: {batch.destination} ({batch.dest_code}) {batch.dest_flag}\n")
        
    except FileNotFoundError:
        console.print("[bold red]❌ Erro: Arquivo 'input.txt' não encontrado![/bold red]")
        console.print("Crie um arquivo input.txt na raiz do projeto.\n")
    except ValueError as e:
        console.print(f"[bold red]❌ Erro ao parsear: {e}[/bold red]\n")


if __name__ == "__main__":
    main()
