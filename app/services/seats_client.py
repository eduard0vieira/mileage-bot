"""
Seats.aero API Client

Client for interacting with Seats.aero Partner API.
"""

import requests
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, date, timedelta
from collections import defaultdict
from app.core.config import Config
from app.core.models import FlightBatch


# Mapeamento completo de códigos Seats.aero para nomes de programas de fidelidade
PROGRAM_MAPPING = {
    # Star Alliance
    'aeroplan': 'Air Canada Aeroplan',
    'united': 'United MileagePlus',
    'avianca': 'Avianca LifeMiles',
    'lifemiles': 'Avianca LifeMiles',
    'ana': 'ANA Mileage Club',
    'asiana': 'Asiana Club',
    'lufthansa': 'Lufthansa Miles & More',
    'sas': 'SAS EuroBonus',
    'eurobonus': 'SAS EuroBonus',
    'singapore': 'Singapore Airlines KrisFlyer',
    'thai': 'Thai Royal Orchid Plus',
    'turkish': 'Turkish Miles&Smiles',
    
    # OneWorld
    'aa': 'American AAdvantage',
    'aadvantage': 'American AAdvantage',
    'ba': 'British Airways Executive Club',
    'club': 'British Airways Executive Club',
    'cathay': 'Cathay Pacific Asia Miles',
    'jal': 'JAL Mileage Bank',
    'qantas': 'Qantas Frequent Flyer',
    'qr': 'Qatar Privilege Club',
    'privilege': 'Qatar Privilege Club',
    
    # SkyTeam
    'delta': 'Delta SkyMiles',
    'flyingblue': 'Flying Blue',
    'aeromexico': 'Aeromexico Club Premier',
    'korean': 'Korean Air SKYPASS',
    
    # Outras companhias
    'alaska': 'Alaska Mileage Plan',
    'virgin': 'Virgin Atlantic Flying Club',
    'flyingclub': 'Virgin Atlantic Flying Club',
    'velocity': 'Virgin Australia Velocity',
    'etihad': 'Etihad Guest',
    'emirates': 'Emirates Skywards',
    'tap': 'TAP Miles&Go',
    
    # América do Sul
    'latam': 'LATAM Pass',
    'sms': 'Smiles',
    'smiles': 'Smiles',
    'gol': 'Gol Smiles',
    'azul': 'Azul Fidelidade',
    'blue': 'Azul Fidelidade',
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
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        days: int = 60,
        cabin_class: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for award seat availability in Seats.aero API.
        
        IMPORTANTE: Filtros de cliente (airline, direct, staleness, program)
        NÃO são enviados para a API. Eles devem ser aplicados localmente
        via process_search_results().
        
        Args:
            origin: Origin airport code (e.g., "GRU")
            destination: Destination airport code (e.g., "MIA")
            date_start: Start date ISO "YYYY-MM-DD" (defaults to today)
            date_end: End date ISO (defaults to date_start + days)
            days: Days forward to search (default 60, max 365)
            cabin_class: Cabin filter ("economy", "business", "first")
        
        Returns:
            JSON response with availability data (raw from API)
        
        Example:
            >>> client = SeatsAeroClient()
            >>> results = client.search_availability(
            ...     origin="GRU",
            ...     destination="MIA",
            ...     days=365,
            ...     cabin_class="business"
            ... )
            >>> # Aplicar filtros localmente:
            >>> batches = client.process_search_results(
            ...     results,
            ...     airline_filter="United",
            ...     direct_only=True,
            ...     max_staleness_hours=24
            ... )
        """
        # Calculate dates if not provided
        if not date_start:
            date_start = datetime.now().date().isoformat()
        
        if not date_end:
            start_date_obj = datetime.fromisoformat(date_start).date()
            end_date_obj = start_date_obj + timedelta(days=days)
            date_end = end_date_obj.isoformat()
        
        # IMPORTANTE: Apenas parâmetros aceitos pela API Seats.aero
        params = {
            'origin_airport': origin.upper(),
            'destination_airport': destination.upper(),
            'start_date': date_start,
            'end_date': date_end,
        }
        
        # Cabin é opcional
        if cabin_class:
            params['cabin'] = cabin_class.lower()
        
        # Try common endpoint patterns
        endpoint = '/search'
        
        try:
            return self._make_request('GET', endpoint, params=params)
        except Exception as e:
            # Fallback para endpoint alternativo
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
    def process_search_results(
        results: List[Dict[str, Any]],
        max_staleness_hours: int = 48,
        direct_only: bool = False,
        airline_filter: Optional[str] = None,
        program_filter: Optional[str] = None
    ) -> List[FlightBatch]:
        """
        Processa e agrupa resultados da API Seats.aero.
        
        Filtros aplicados:
        - max_staleness_hours: Descarta voos vistos há mais tempo
        - direct_only: Descarta voos com conexão
        - airline_filter: Filtra por companhia específica
        - program_filter: Filtra por programa de milhas
        
        Args:
            results: Lista de voos da API
            max_staleness_hours: Máximo de horas desde última atualização
            direct_only: Se True, só voos diretos
            airline_filter: Nome da companhia (ex: "United")
            program_filter: Nome do programa (ex: "Privilege Club")
        
        Returns:
            Lista de FlightBatch agrupados
        """
        if not results:
            return []
        
        # Filtrar resultados
        filtered_results = []
        now = datetime.now()
        
        for flight in results:
            # Filtro 1: Staleness (última vez visto)
            last_seen_str = flight.get('LastSeen', flight.get('UpdatedAt', ''))
            if last_seen_str:
                try:
                    last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                    hours_ago = (now - last_seen).total_seconds() / 3600
                    if hours_ago > max_staleness_hours:
                        continue  # Descarta (muito antigo)
                except:
                    pass  # Se não conseguir parsear, mantém
            
            # Filtro 2: Direct only
            if direct_only:
                is_direct = flight.get('Direct', flight.get('Nonstop', True))
                if not is_direct:
                    continue  # Descarta (tem conexão)
            
            # Filtro 3: Airline (case insensitive substring match)
            if airline_filter:
                airline = flight.get('Airline', '')
                # Aceita substring: 'latam' matches 'LATAM Airlines'
                if airline_filter.lower() not in airline.lower():
                    continue  # Descarta (companhia diferente)
            
            # Filtro 4: Program (case insensitive substring match)
            if program_filter:
                source = flight.get('Source', '').lower()
                # Traduzir código para nome do programa
                program_name = PROGRAM_MAPPING.get(source, source.title())
                
                # Verifica se program_filter está no nome traduzido OU no código
                # Ex: 'Qatar' matches 'Qatar Privilege Club'
                # Ex: 'privilege' matches 'privilege' (código)
                filter_lower = program_filter.lower()
                if (filter_lower not in program_name.lower() and 
                    filter_lower not in source):
                    continue  # Descarta (programa diferente)
            
            filtered_results.append(flight)
        
        if not filtered_results:
            return []
        
        # Agrupar por (Origin, Destination, Airline, Source)
        groups = defaultdict(list)
        
        for flight in filtered_results:
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
            # Traduzir código do programa para nome legível
            program = PROGRAM_MAPPING.get(source, source.title())
            
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
                    seats = 4
                
                dates.append((date_str, seats))
                
                # Custo
                miles_cost = flight.get('MilesCost', flight.get('Miles', 0))
                if miles_cost:
                    costs.append(miles_cost)
                
                # Classe
                if cabin_class is None:
                    cabin_class = flight.get('CabinClass', flight.get('Cabin', 'economy'))
            
            if not dates:
                continue
            
            # Calcular min e max cost
            min_cost = min(costs) if costs else None
            max_cost = max(costs) if costs else None
            
            # Formatar custo display
            if min_cost:
                if min_cost >= 1000:
                    cost_str = f"{min_cost // 1000}k"
                else:
                    cost_str = str(min_cost)
                
                # Se há variação de preço
                if max_cost and max_cost != min_cost:
                    max_str = f"{max_cost // 1000}k" if max_cost >= 1000 else str(max_cost)
                    cost_str = f"{cost_str}-{max_str}"
            else:
                cost_str = "Consultar"
            
            # Mapear cabin
            cabin_map = {
                'economy': 'Econômica',
                'premium_economy': 'Econômica Premium',
                'business': 'Executiva',
                'first': 'Primeira Classe'
            }
            cabin_display = cabin_map.get(cabin_class, cabin_class.title())
            
            # Nota com estatísticas
            notes_parts = [f"Encontrado via API Seats.aero"]
            notes_parts.append(f"{len(dates)} opções disponíveis")
            if min_cost and max_cost and max_cost != min_cost:
                notes_parts.append(f"Variação de preço: {min_cost//1000}k-{max_cost//1000}k")
            
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
                dates_inbound=[],
                notes=" | ".join(notes_parts),
                min_cost=min_cost,
                max_cost=max_cost
            )
            
            # Enriquecer
            try:
                batch.enrich_airport_data()
            except Exception:
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
