"""
Teste das funcionalidades avançadas do Seats.aero Client

Este arquivo demonstra:
1. Busca com 365 dias
2. Filtros de staleness (freshness dos dados)
3. Filtros de voo direto
4. Filtros de companhia
5. Filtros de programa
6. Cálculo de min/max cost
"""

from datetime import datetime, timedelta
from src.seats_client import SeatsAeroClient

# Mock de dados da API Seats.aero
mock_api_response = [
    # Voo 1: Qatar Airways - Privilege Club - Direto - Recente
    {
        "Origin": "GRU",
        "Destination": "DOH",
        "Airline": "Qatar Airways",
        "Source": "qr",
        "Date": "2026-06-15",
        "RemainingSeats": 4,
        "MilesCost": 70000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": datetime.now().isoformat()  # Agora mesmo
    },
    # Voo 2: Qatar - Mais caro (para testar min/max)
    {
        "Origin": "GRU",
        "Destination": "DOH",
        "Airline": "Qatar Airways",
        "Source": "qr",
        "Date": "2026-06-20",
        "RemainingSeats": 2,
        "MilesCost": 90000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": datetime.now().isoformat()
    },
    # Voo 3: Qatar - Mais barato (para testar min/max)
    {
        "Origin": "GRU",
        "Destination": "DOH",
        "Airline": "Qatar Airways",
        "Source": "qr",
        "Date": "2026-07-01",
        "RemainingSeats": 6,
        "MilesCost": 65000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": datetime.now().isoformat()
    },
    # Voo 4: United - Velho demais (será filtrado)
    {
        "Origin": "GRU",
        "Destination": "MIA",
        "Airline": "United",
        "Source": "united",
        "Date": "2026-08-15",
        "RemainingSeats": 4,
        "MilesCost": 77000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": (datetime.now() - timedelta(hours=72)).isoformat()  # 72h atrás
    },
    # Voo 5: United - Com conexão (será filtrado se direct_only=True)
    {
        "Origin": "GRU",
        "Destination": "MIA",
        "Airline": "United",
        "Source": "united",
        "Date": "2026-08-20",
        "RemainingSeats": 9,
        "MilesCost": 50000,
        "CabinClass": "business",
        "Direct": False,  # Com conexão
        "LastSeen": datetime.now().isoformat()
    },
    # Voo 6: United - Direto e recente (passa nos filtros)
    {
        "Origin": "GRU",
        "Destination": "MIA",
        "Airline": "United",
        "Source": "united",
        "Date": "2026-09-01",
        "RemainingSeats": 4,
        "MilesCost": 80000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": datetime.now().isoformat()
    },
    # Voo 7: LATAM (companhia diferente, será filtrado se airline_filter="Qatar Airways")
    {
        "Origin": "GRU",
        "Destination": "MIA",
        "Airline": "LATAM",
        "Source": "latam",
        "Date": "2026-10-01",
        "RemainingSeats": 8,
        "MilesCost": 60000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": datetime.now().isoformat()
    },
]


def test_no_filters():
    """Teste sem filtros - deve retornar todos os voos válidos agrupados."""
    print("=" * 70)
    print("TESTE 1: Sem filtros")
    print("=" * 70)
    
    batches = SeatsAeroClient.process_search_results(mock_api_response)
    
    print(f"\n✅ {len(batches)} batch(es) criado(s):\n")
    for batch in batches:
        print(f"  • {batch.route} - {batch.airline} ({batch.program})")
        print(f"    Custo: {batch.cost} (min: {batch.min_cost}, max: {batch.max_cost})")
        print(f"    Datas: {len(batch.dates_outbound)} opções")
        print()


def test_staleness_filter():
    """Teste com filtro de staleness - deve descartar voos antigos."""
    print("=" * 70)
    print("TESTE 2: Filtro de Staleness (max 48h)")
    print("=" * 70)
    
    batches = SeatsAeroClient.process_search_results(
        mock_api_response,
        max_staleness_hours=48
    )
    
    print(f"\n✅ {len(batches)} batch(es) após filtro de staleness:\n")
    for batch in batches:
        print(f"  • {batch.route} - {batch.airline}")
        print(f"    Datas: {len(batch.dates_outbound)} opções")
        print()


def test_direct_only_filter():
    """Teste com filtro de voos diretos."""
    print("=" * 70)
    print("TESTE 3: Apenas Voos Diretos")
    print("=" * 70)
    
    batches = SeatsAeroClient.process_search_results(
        mock_api_response,
        max_staleness_hours=48,
        direct_only=True
    )
    
    print(f"\n✅ {len(batches)} batch(es) após filtro de voos diretos:\n")
    for batch in batches:
        print(f"  • {batch.route} - {batch.airline}")
        print()


def test_program_filter():
    """Teste com filtro de programa (Privilege Club)."""
    print("=" * 70)
    print("TESTE 4: Filtro de Programa (Privilege Club)")
    print("=" * 70)
    
    batches = SeatsAeroClient.process_search_results(
        mock_api_response,
        max_staleness_hours=48,
        direct_only=True,
        program_filter="Privilege Club"
    )
    
    print(f"\n✅ {len(batches)} batch(es) após filtro de programa:\n")
    for batch in batches:
        print(f"  • {batch.route} - {batch.airline} ({batch.program})")
        print(f"    Custo: {batch.cost} (min: {batch.min_cost}, max: {batch.max_cost})")
        print(f"    Datas: {len(batch.dates_outbound)} opções")
        print()


def test_airline_filter():
    """Teste com filtro de companhia (United)."""
    print("=" * 70)
    print("TESTE 5: Filtro de Companhia (United)")
    print("=" * 70)
    
    batches = SeatsAeroClient.process_search_results(
        mock_api_response,
        max_staleness_hours=48,
        direct_only=True,
        airline_filter="United"
    )
    
    print(f"\n✅ {len(batches)} batch(es) após filtro de companhia:\n")
    for batch in batches:
        print(f"  • {batch.route} - {batch.airline}")
        print()


def test_min_max_cost():
    """Teste específico para verificar cálculo de min/max cost."""
    print("=" * 70)
    print("TESTE 6: Cálculo de Min/Max Cost (Qatar - Privilege Club)")
    print("=" * 70)
    
    batches = SeatsAeroClient.process_search_results(
        mock_api_response,
        program_filter="Privilege Club"
    )
    
    for batch in batches:
        if batch.program == "Privilege Club":
            print(f"\n✅ Batch encontrado: {batch.route}")
            print(f"  • Display: {batch.cost}")
            print(f"  • Menor custo (min_cost): {batch.min_cost} milhas")
            print(f"  • Maior custo (max_cost): {batch.max_cost} milhas")
            print(f"  • Variação: {batch.max_cost - batch.min_cost} milhas")
            print(f"  • Datas disponíveis: {len(batch.dates_outbound)}")
            print()


if __name__ == "__main__":
    print("\n🧪 TESTES DE FUNCIONALIDADES AVANÇADAS\n")
    
    test_no_filters()
    test_staleness_filter()
    test_direct_only_filter()
    test_program_filter()
    test_airline_filter()
    test_min_max_cost()
    
    print("=" * 70)
    print("✅ Todos os testes concluídos!")
    print("=" * 70 + "\n")
