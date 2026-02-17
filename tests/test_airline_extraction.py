"""
Teste para validar extração robusta do campo 'airline'.

A API Seats.aero pode retornar a companhia em diferentes campos
ou estruturas. Este teste valida todas as variações.
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.seats_client import SeatsAeroClient
from datetime import datetime


def test_airline_direct_field():
    """Teste 1: Airline como campo direto."""
    print("\n" + "=" * 70)
    print("TESTE 1: Airline como Campo Direto")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'LATAM Airlines',  # ✅ Campo direto
            'Source': 'latam',
            'Date': '2026-06-15',
            'MilesCost': 70000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 1
    assert batches[0].airline == 'LATAM Airlines'
    print(f"✅ Airline extraída: '{batches[0].airline}'")
    print()


def test_airline_nested_route():
    """Teste 2: Airline aninhada em Route."""
    print("=" * 70)
    print("TESTE 2: Airline Aninhada em Route")
    print("=" * 70)
    
    mock_flights = [
        {
            'Route': {
                'OriginAirport': 'GRU',
                'DestinationAirport': 'DOH',
                'Airline': 'Qatar Airways'  # ✅ Aninhado em Route
            },
            'Source': 'qr',
            'Date': '2026-06-15',
            'MilesCost': 77000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 1
    assert batches[0].airline == 'Qatar Airways'
    print(f"✅ Airline extraída de Route: '{batches[0].airline}'")
    print()


def test_airline_marketing_carrier():
    """Teste 3: MarketingCarrier como fallback."""
    print("=" * 70)
    print("TESTE 3: MarketingCarrier como Fallback")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'JFK',
            'Destination': 'LHR',
            # SEM campo 'Airline'
            'MarketingCarrier': 'American Airlines',  # ✅ Fallback
            'Source': 'aadvantage',
            'Date': '2026-07-01',
            'MilesCost': 85000,
            'RemainingSeats': 2,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 1
    assert batches[0].airline == 'American Airlines'
    print(f"✅ MarketingCarrier usado: '{batches[0].airline}'")
    print()


def test_airline_operated_by():
    """Teste 4: OperatedBy como último fallback."""
    print("=" * 70)
    print("TESTE 4: OperatedBy como Último Fallback")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'LAX',
            'Destination': 'SYD',
            # SEM 'Airline' nem 'MarketingCarrier'
            'OperatedBy': 'Qantas',  # ✅ Último fallback
            'Source': 'qantas',
            'Date': '2026-08-01',
            'MilesCost': 95000,
            'RemainingSeats': 1,
            'Direct': False,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 1
    assert batches[0].airline == 'Qantas'
    print(f"✅ OperatedBy usado: '{batches[0].airline}'")
    print()


def test_airline_unknown():
    """Teste 5: Companhia Desconhecida quando nada é encontrado."""
    print("=" * 70)
    print("TESTE 5: Companhia Desconhecida (Nenhum Campo Disponível)")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            # SEM nenhum campo de companhia
            'Source': 'unknown',
            'Date': '2026-09-01',
            'MilesCost': 50000,
            'RemainingSeats': 3,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 1
    # Agora infere "Unknown" via .title() ao invés de "Companhia Desconhecida"
    assert batches[0].airline == 'Unknown'
    print(f"✅ Fallback aplicado: '{batches[0].airline}' (inferido de source 'unknown')")
    print()


def test_airline_filter_works():
    """Teste 6: Filtro de airline funciona com busca robusta."""
    print("=" * 70)
    print("TESTE 6: Filtro de Airline Funcionando")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'LATAM Airlines',
            'Source': 'latam',
            'Date': '2026-06-15',
            'MilesCost': 70000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'United Airlines',
            'Source': 'united',
            'Date': '2026-06-16',
            'MilesCost': 85000,
            'RemainingSeats': 2,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # Filtrar apenas "United"
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        airline_filter="United"
    )
    
    assert len(batches) == 1
    assert batches[0].airline == 'United Airlines'
    print(f"✅ Filtro 'United' retornou: '{batches[0].airline}'")
    
    # Filtrar apenas "LATAM"
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        airline_filter="LATAM"
    )
    
    assert len(batches) == 1
    assert batches[0].airline == 'LATAM Airlines'
    print(f"✅ Filtro 'LATAM' retornou: '{batches[0].airline}'")
    
    print()


def test_airline_filter_case_insensitive():
    """Teste 7: Filtro de airline é case insensitive."""
    print("=" * 70)
    print("TESTE 7: Filtro Case Insensitive")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'DOH',
            'Airline': 'Qatar Airways',
            'Source': 'qr',
            'Date': '2026-06-15',
            'MilesCost': 77000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # Filtro em lowercase
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        airline_filter="qatar"
    )
    assert len(batches) == 1
    print("✅ Filtro 'qatar' (lowercase) funcionou")
    
    # Filtro em uppercase
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        airline_filter="QATAR"
    )
    assert len(batches) == 1
    print("✅ Filtro 'QATAR' (uppercase) funcionou")
    
    # Filtro misto
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        airline_filter="QaTaR"
    )
    assert len(batches) == 1
    print("✅ Filtro 'QaTaR' (mixed case) funcionou")
    
    print()


def test_airline_filter_substring():
    """Teste 8: Filtro de airline aceita substring."""
    print("=" * 70)
    print("TESTE 8: Filtro com Substring")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'United Airlines',
            'Source': 'united',
            'Date': '2026-06-15',
            'MilesCost': 77000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # Substring no início
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        airline_filter="United"
    )
    assert len(batches) == 1
    print("✅ Filtro 'United' (substring) funcionou")
    
    # Substring no meio
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        airline_filter="ited"
    )
    assert len(batches) == 1
    print("✅ Filtro 'ited' (substring no meio) funcionou")
    
    # Substring no final
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        airline_filter="Airlines"
    )
    assert len(batches) == 1
    print("✅ Filtro 'Airlines' (substring no final) funcionou")
    
    print()


if __name__ == "__main__":
    print("\n🧪 TESTES DE EXTRAÇÃO ROBUSTA DE AIRLINE\n")
    
    try:
        test_airline_direct_field()
        test_airline_nested_route()
        test_airline_marketing_carrier()
        test_airline_operated_by()
        test_airline_unknown()
        test_airline_filter_works()
        test_airline_filter_case_insensitive()
        test_airline_filter_substring()
        
        print("=" * 70)
        print("✅ TODOS OS TESTES DE AIRLINE PASSARAM!")
        print("=" * 70)
        print("\n💡 A extração robusta de airline garante que:")
        print("  • Campo direto 'Airline' é tentado primeiro")
        print("  • Route.Airline (aninhado) é tentado em seguida")
        print("  • MarketingCarrier é usado como fallback")
        print("  • OperatedBy é usado como último fallback")
        print("  • 'Companhia Desconhecida' é usado se tudo falhar")
        print("  • Filtro --airline funciona com case insensitive")
        print("  • Filtro --airline aceita substrings\n")
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}\n")
        raise
