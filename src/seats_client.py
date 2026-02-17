"""
Seats.aero API Client

Client for interacting with Seats.aero Partner API.
"""

import requests
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, date
from collections import defaultdict
from src.config import Config
from src.models import FlightBatch


# Mapeamento de códigos de programas para nomes bonitos
PROGRAM_NAMES = {
    'sms': 'Smiles',
    'lifemiles': 'LifeMiles',
    'avianca': 'LifeMiles',
    'aeroplan': 'Aeroplan',
    'united': 'United MileagePlus',
    'aa': 'AAdvantage',
    'delta': 'Delta SkyMiles',
    'virgin': 'Virgin Atlantic',
    'ba': 'British Airways Executive Club',
    'qantas': 'Qantas Frequent Flyer',
    'emirates': 'Emirates Skywards',
    'etihad': 'Etihad Guest',
    'alaska': 'Alaska Mileage Plan',
    'tap': 'TAP Miles&Go',
    'latam': 'LATAM Pass',
    'azul': 'Azul TudoAzul',
    'gol': 'Gol Smiles',
}


class SeatsAeroClient:
    """
    Client for Seats.aero Partner API.
    
    Handles authentication, request formatting, and error handling.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Seats.aero client.
        
        Args:
            api_key: Optional API key. If not provided, uses Config.SEATS_API_KEY
        """
        self.api_key = api_key or Config.SEATS_API_KEY
        self.base_url = Config.SEATS_BASE_URL
        
        if not self.api_key:
            Config.validate()  # Raises helpful error message
        
        # Setup session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Partner-Authorization': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'MileageBot/1.0'
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Seats.aero API.
        
        Args:
            method: HTTP method (GET, POST, etc)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON body for POST/PUT
            timeout: Request timeout in seconds
        
        Returns:
            JSON response as dict
        
        Raises:
            ConnectionError: Network/connection issues
            ValueError: Invalid response or API error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=timeout
            )
            
            # Check for HTTP errors
            if response.status_code == 401:
                raise ValueError(
                    "❌ Autenticação falhou! Verifique sua SEATS_API_KEY no .env"
                )
            elif response.status_code == 403:
                raise ValueError(
                    "❌ Acesso negado. Verifique se sua chave tem permissões corretas."
                )
            elif response.status_code == 429:
                raise ValueError(
                    "❌ Rate limit excedido. Aguarde alguns minutos e tente novamente."
                )
            elif response.status_code >= 500:
                raise ConnectionError(
                    f"❌ Erro no servidor Seats.aero (status {response.status_code}). "
                    "Tente novamente mais tarde."
                )
            
            response.raise_for_status()
            
            # Parse JSON
            try:
                return response.json()
            except ValueError:
                raise ValueError(
                    f"❌ Resposta inválida da API (não é JSON): {response.text[:200]}"
                )
        
        except requests.exceptions.Timeout:
            raise ConnectionError(
                f"❌ Timeout após {timeout}s. Verifique sua conexão ou tente novamente."
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"❌ Erro de conexão: {str(e)}\n"
                "Verifique sua internet ou se a API está disponível."
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"❌ Erro na requisição: {str(e)}")
    
    def search_availability(
        self,
        origin: str,
        destination: str,
        date_start: str,
        date_end: Optional[str] = None,
        cabin_class: Optional[str] = None,
        direct_only: bool = False
    ) -> Dict[str, Any]:
        """
        Search for award seat availability.
        
        Args:
            origin: Origin airport code (e.g., "GRU")
            destination: Destination airport code (e.g., "MIA")
            date_start: Start date in ISO format "YYYY-MM-DD"
            date_end: End date in ISO format (optional, defaults to date_start)
            cabin_class: Cabin class filter ("economy", "business", "first")
            direct_only: Only show direct flights
        
        Returns:
            JSON response with availability data
        
        Example:
            >>> client = SeatsAeroClient()
            >>> results = client.search_availability(
            ...     origin="GRU",
            ...     destination="MIA",
            ...     date_start="2026-02-15",
            ...     cabin_class="business"
            ... )
        """
        params = {
            'origin': origin.upper(),
            'destination': destination.upper(),
            'date': date_start,
        }
        
        if date_end:
            params['date_end'] = date_end
        
        if cabin_class:
            params['cabin'] = cabin_class.lower()
        
        if direct_only:
            params['direct'] = 'true'
        
        # Try common endpoint patterns
        # Seats.aero API might use /search, /availability, or /flights
        # Adjust based on actual API documentation
        endpoint = '/search'
        
        try:
            return self._make_request('GET', endpoint, params=params)
        except Exception as e:
            # If endpoint fails, try alternative
            if '/search' in str(endpoint):
                try:
                    endpoint = '/availability'
                    return self._make_request('GET', endpoint, params=params)
                except:
                    pass
            raise e
    
    def get_routes(self, origin: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available routes from Seats.aero.
        
        Args:
            origin: Optional origin filter
        
        Returns:
            JSON with available routes
        """
        params = {}
        if origin:
            params['origin'] = origin.upper()
        
        return self._make_request('GET', '/routes', params=params)
    
    def get_programs(self) -> Dict[str, Any]:
        """
        Get list of supported loyalty programs.
        
        Returns:
            JSON with program data
        """
        return self._make_request('GET', '/programs')
    
    def close(self):
        """Close the session (cleanup)."""
        self.session.close()
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()
    
    @staticmethod
    def process_search_results(results: List[Dict[str, Any]]) -> List[FlightBatch]:
        """
        Processa resultados da API Seats.aero e agrupa em FlightBatch.
        
        Por que agrupar?
        - API retorna voos individuais (um por data/airline/program)
        - Queremos agrupar em "batches" para gerar um alerta por grupo
        - Grupo = mesma origem, destino, companhia, programa
        
        Args:
            results: Lista de voos da API (cada dict é um voo)
        
        Returns:
            Lista de FlightBatch agrupados e processados
        
        Exemplo de input da API:
        [
            {
                "Origin": "GRU",
                "Destination": "MIA",
                "Airline": "United",
                "Source": "united",
                "Date": "2026-03-01",
                "RemainingSeats": 4,
                "MilesCost": 77000,
                "CabinClass": "business",
                ...
            },
            ...
        ]
        """
        if not results:
            return []
        
        # Agrupar por (Origin, Destination, Airline, Source)
        groups = defaultdict(list)
        
        for flight in results:
            # Chave de agrupamento
            key = (
                flight.get('Origin', '').upper(),
                flight.get('Destination', '').upper(),
                flight.get('Airline', ''),
                flight.get('Source', '').lower()
            )
            groups[key].append(flight)
        
        # Criar FlightBatch para cada grupo
        batches = []
        
        for (origin_code, dest_code, airline, source), flights in groups.items():
            # Mapear source para nome bonito do programa
            program = PROGRAM_NAMES.get(source, source.title())
            
            # Coletar todas as datas com assentos
            dates = []
            costs = []
            cabin_class = None
            
            for flight in flights:
                # Data
                date_str = flight.get('Date', flight.get('DepartureDate', ''))
                if not date_str:
                    continue
                
                # Assentos
                seats = flight.get('RemainingSeats', flight.get('Seats', None))
                if seats is None:
                    seats = 4  # Default: 4+ assentos
                
                dates.append((date_str, seats))
                
                # Custo em milhas
                miles_cost = flight.get('MilesCost', flight.get('Miles', 0))
                if miles_cost:
                    costs.append(miles_cost)
                
                # Classe (pega do primeiro voo)
                if cabin_class is None:
                    cabin_class = flight.get('CabinClass', flight.get('Cabin', 'economy'))
            
            if not dates:
                continue  # Skip se não tem datas
            
            # Determinar custo (menor valor encontrado)
            if costs:
                min_cost = min(costs)
                # Formatar: 77000 -> "77k"
                if min_cost >= 1000:
                    cost_str = f"{min_cost // 1000}k"
                else:
                    cost_str = str(min_cost)
            else:
                cost_str = "Consultar"
            
            # Mapear cabin class
            cabin_map = {
                'economy': 'Econômica',
                'premium_economy': 'Econômica Premium',
                'business': 'Executiva',
                'first': 'Primeira Classe'
            }
            cabin_display = cabin_map.get(cabin_class, cabin_class.title())
            
            # Criar FlightBatch
            batch = FlightBatch(
                origin="",
                origin_code=origin_code,
                origin_flag="",
                destination="",
                dest_code=dest_code,
                dest_flag="",
                airline=airline,
                program=program,
                cost=cost_str,
                cabin=cabin_display,
                dates_outbound=dates,
                dates_inbound=[],  # API normalmente retorna só ida, volta é outra busca
                notes=f"Encontrado via API Seats.aero ({len(dates)} opção/opções disponível/disponíveis)"
            )
            
            # Enriquecer com dados de aeroportos
            try:
                batch.enrich_airport_data()
            except Exception:
                # Se falhar, deixa os campos vazios (já estão)
                pass
            
            batches.append(batch)
        
        return batches


def main():
    """
    Test the Seats.aero client.
    Execute: python -m src.seats_client
    """
    from rich.console import Console
    from rich.json import JSON
    
    console = Console()
    
    console.print("\n[bold cyan]🔌 Testando Seats.aero Client[/bold cyan]\n")
    
    try:
        # Initialize client
        console.print("[yellow]Inicializando cliente...[/yellow]")
        client = SeatsAeroClient()
        console.print("[green]✅ Cliente inicializado![/green]\n")
        
        # Test search
        console.print("[yellow]Testando busca GRU → MIA...[/yellow]")
        results = client.search_availability(
            origin="GRU",
            destination="MIA",
            date_start="2026-03-01",
            cabin_class="business"
        )
        
        console.print("[green]✅ Busca realizada![/green]\n")
        console.print("[bold]Resposta da API:[/bold]")
        console.print(JSON(str(results)))
        
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
    except ConnectionError as e:
        console.print(f"[red]{e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Erro inesperado: {e}[/red]")


if __name__ == "__main__":
    main()
