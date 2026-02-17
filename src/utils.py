"""
Utility functions for Flight Alert CLI

Funções auxiliares para carregar dados e fazer operações comuns.
"""

import json
from pathlib import Path
from typing import Dict, Optional


def load_airport_data(iata_code: str) -> Dict[str, str]:
    """
    Carrega dados de um aeroporto a partir do código IATA.
    
    Por que esta função existe?
    - Evita repetir manualmente cidade e bandeira para cada aeroporto
    - Centraliza os dados em um único JSON (data/airports.json)
    - Permite adicionar novos aeroportos sem alterar código
    
    Como funciona:
    1. Lê o arquivo data/airports.json
    2. Busca o código IATA (case insensitive: "gru" vira "GRU")
    3. Retorna {"city": "São Paulo", "flag": "🇧🇷"}
    4. Se não encontrar, retorna dados genéricos
    
    Args:
        iata_code: Código IATA do aeroporto (ex: "GRU", "MIA", "LIS")
                   Aceita maiúsculas ou minúsculas
    
    Returns:
        Dicionário com duas chaves:
        - "city": Nome da cidade (ex: "São Paulo")
        - "flag": Emoji da bandeira (ex: "🇧🇷")
        
        Se o código não for encontrado:
        - "city": O próprio código IATA em maiúsculas
        - "flag": "✈️" (emoji genérico de avião)
    
    Exemplo:
        >>> load_airport_data("GRU")
        {"city": "São Paulo", "flag": "🇧🇷"}
        
        >>> load_airport_data("gru")  # Case insensitive
        {"city": "São Paulo", "flag": "🇧🇷"}
        
        >>> load_airport_data("XYZ")  # Código desconhecido
        {"city": "XYZ", "flag": "✈️"}
    """
    # Caminho para o arquivo JSON de aeroportos
    # Path(__file__).parent = pasta 'src/'
    # .parent = volta para a raiz do projeto
    # / "data" / "airports.json" = caminho completo
    airports_file = Path(__file__).parent.parent / "data" / "airports.json"
    
    # Normaliza o código para maiúsculas (GRU, gru, Gru → GRU)
    iata_code_upper = iata_code.upper().strip()
    
    try:
        # Tenta abrir e ler o arquivo JSON
        with open(airports_file, "r", encoding="utf-8") as f:
            airports_data = json.load(f)
        
        # Busca o código no dicionário
        if iata_code_upper in airports_data:
            return airports_data[iata_code_upper]
        else:
            # Código não encontrado - retorna dados genéricos
            return {
                "city": iata_code_upper,
                "flag": "✈️"
            }
    
    except FileNotFoundError:
        # Arquivo airports.json não existe
        # Retorna dados genéricos para não quebrar o código
        return {
            "city": iata_code_upper,
            "flag": "✈️"
        }
    
    except json.JSONDecodeError:
        # JSON mal formatado
        # Retorna dados genéricos
        return {
            "city": iata_code_upper,
            "flag": "✈️"
        }


def get_airport_info(iata_code: str) -> tuple[str, str]:
    """
    Versão simplificada que retorna tupla (cidade, bandeira).
    
    Atalho para quando você só quer desempacotar os valores:
    
    Exemplo:
        >>> city, flag = get_airport_info("GRU")
        >>> print(city)  # "São Paulo"
        >>> print(flag)  # "🇧🇷"
    
    Args:
        iata_code: Código IATA do aeroporto
    
    Returns:
        Tupla (cidade, bandeira)
    """
    data = load_airport_data(iata_code)
    return data["city"], data["flag"]


def main():
    """
    Exemplo de uso das funções de utils.
    Execute: python -m src.utils
    """
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    console.print("\n[bold cyan]🛫 Testando load_airport_data()[/bold cyan]\n")
    
    # Lista de códigos para testar
    test_codes = ["GRU", "mia", "LIS", "jfk", "XYZ"]  # XYZ não existe
    
    # Cria tabela de resultados
    table = Table(title="Resultados do Lookup", show_header=True, header_style="bold magenta")
    table.add_column("Código IATA", style="cyan")
    table.add_column("Cidade", style="green")
    table.add_column("Bandeira", style="yellow")
    
    for code in test_codes:
        data = load_airport_data(code)
        table.add_row(code, data["city"], data["flag"])
    
    console.print(table)
    
    console.print("\n[bold green]✅ Todos os códigos foram processados![/bold green]\n")


if __name__ == "__main__":
    main()
