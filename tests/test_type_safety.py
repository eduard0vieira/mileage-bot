"""
Teste para validar conversão segura de tipos (string → int).

A API Seats.aero pode retornar números como strings ("77000")
ou valores None. Este teste valida o método _safe_int.
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.seats_client import SeatsAeroClient
from datetime import datetime


def test_safe_int_basic():
    """Teste 1: Conversões básicas."""
    print("\n" + "=" * 70)
    print("TESTE 1: Conversões Básicas do _safe_int")
    print("=" * 70)
    
    # Integer direto
    assert SeatsAeroClient._safe_int(77000) == 77000
    print("✅ Integer direto: 77000 → 77000")
    
    # String numérica
    assert SeatsAeroClient._safe_int("77000") == 77000
    print("✅ String numérica: '77000' → 77000")
    
    # None (default 0)
    assert SeatsAeroClient._safe_int(None) == 0
    print("✅ None: None → 0")
    
    # None com default customizado
    assert SeatsAeroClient._safe_int(None, default=4) == 4
    print("✅ None com default: None (default=4) → 4")
    
    # String vazia
    assert SeatsAeroClient._safe_int("") == 0
    print("✅ String vazia: '' → 0")
    
    # String com espaços
    assert SeatsAeroClient._safe_int("  12345  ") == 12345
    print("✅ String com espaços: '  12345  ' → 12345")
    
    # Float
    assert SeatsAeroClient._safe_int(77.9) == 77
    print("✅ Float: 77.9 → 77")
    
    # Zero
    assert SeatsAeroClient._safe_int(0) == 0
    print("✅ Zero: 0 → 0")
    
    print()


def test_safe_int_edge_cases():
    """Teste 2: Casos extremos."""
    print("=" * 70)
    print("TESTE 2: Casos Extremos")
    print("=" * 70)
    
    # String inválida
    assert SeatsAeroClient._safe_int("invalid") == 0
    print("✅ String inválida: 'invalid' → 0")
    
    # String inválida com default
    assert SeatsAeroClient._safe_int("abc", default=10) == 10
    print("✅ String inválida com default: 'abc' (default=10) → 10")
    
    # Boolean True (em Python, bool é subclasse de int: True == 1)
    assert SeatsAeroClient._safe_int(True) == 1
    print("✅ Boolean True: True → 1 (Python: bool é subclasse de int)")
    
    # Boolean False
    assert SeatsAeroClient._safe_int(False) == 0
    print("✅ Boolean False: False → 0")
    
    # Lista (tipo inválido)
    assert SeatsAeroClient._safe_int([1, 2, 3]) == 0
    print("✅ Lista: [1,2,3] → 0 (default)")
    
    # Dict (tipo inválido)
    assert SeatsAeroClient._safe_int({"value": 123}) == 0
    print("✅ Dict: {'value': 123} → 0 (default)")
    
    print()


def test_safe_int_with_api_data():
    """Teste 3: Com dados reais da API (simulados)."""
    print("=" * 70)
    print("TESTE 3: Simulação com Dados da API")
    print("=" * 70)
    
    # Simular resposta da API onde números vêm como strings
    mock_flight = {
        'Origin': 'GRU',
        'Destination': 'MIA',
        'Airline': 'United Airlines',
        'Source': 'united',
        'Date': '2026-06-15',
        'JMileageCost': "77000",      # ⚠️ String ao invés de int
        'RemainingSeats': "4",        # ⚠️ String ao invés de int
        'Direct': True,
        'LastSeen': datetime.now().isoformat()
    }
    
    # Testar conversão de custo
    cost = SeatsAeroClient._safe_int(mock_flight['JMileageCost'])
    assert cost == 77000
    assert isinstance(cost, int)
    print(f"✅ Custo da API: '{mock_flight['JMileageCost']}' → {cost} (type: {type(cost).__name__})")
    
    # Testar conversão de assentos
    seats = SeatsAeroClient._safe_int(mock_flight['RemainingSeats'])
    assert seats == 4
    assert isinstance(seats, int)
    print(f"✅ Assentos da API: '{mock_flight['RemainingSeats']}' → {seats} (type: {type(seats).__name__})")
    
    # Testar que comparações funcionam
    assert cost > 0
    assert cost >= 1000
    assert seats > 0
    print("✅ Comparações numéricas funcionam após conversão")
    
    print()


def test_process_with_string_values():
    """Teste 4: process_search_results com valores string."""
    print("=" * 70)
    print("TESTE 4: Processamento com Valores String")
    print("=" * 70)
    
    # Mock com TODOS os valores numéricos como strings (API real)
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'DOH',
            'Airline': 'Qatar Airways',
            'Source': 'qr',
            'Date': '2026-06-15',
            'MilesCost': "70000",        # String
            'RemainingSeats': "4",       # String
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'DOH',
            'Airline': 'Qatar Airways',
            'Source': 'qr',
            'Date': '2026-06-20',
            'MilesCost': "85000",        # String
            'RemainingSeats': "2",       # String
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # Processar
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 1
    print(f"✅ {len(batches)} batch criado com sucesso")
    
    batch = batches[0]
    
    # Verificar que min/max foram calculados corretamente
    assert batch.min_cost == 70000
    assert batch.max_cost == 85000
    print(f"✅ Min cost: {batch.min_cost} (type: {type(batch.min_cost).__name__})")
    print(f"✅ Max cost: {batch.max_cost} (type: {type(batch.max_cost).__name__})")
    
    # Verificar datas
    assert len(batch.dates_outbound) == 2
    print(f"✅ {len(batch.dates_outbound)} datas processadas")
    
    # Verificar assentos (convertidos de string)
    date1, seats1 = batch.dates_outbound[0]
    date2, seats2 = batch.dates_outbound[1]
    assert seats1 == 4
    assert seats2 == 2
    print(f"✅ Assentos convertidos: {seats1}, {seats2}")
    
    # Verificar que enriquecimento funcionou
    assert batch.origin != ""
    assert batch.destination != ""
    print(f"✅ Enriquecimento: {batch.origin} → {batch.destination}")
    
    print()


def test_division_operations():
    """Teste 5: Operações matemáticas funcionam."""
    print("=" * 70)
    print("TESTE 5: Operações Matemáticas")
    print("=" * 70)
    
    # Valores como strings
    cost_str = "77000"
    seats_str = "4"
    
    # Converter
    cost = SeatsAeroClient._safe_int(cost_str)
    seats = SeatsAeroClient._safe_int(seats_str)
    
    # Operações matemáticas
    cost_display = cost // 1000  # Divisão inteira para "k"
    assert cost_display == 77
    print(f"✅ {cost} // 1000 = {cost_display}k")
    
    per_seat = cost // seats if seats > 0 else 0
    assert per_seat == 19250
    print(f"✅ {cost} // {seats} = {per_seat} por assento")
    
    # Comparações
    assert cost >= 1000
    assert seats > 0
    print("✅ Comparações (>=, >) funcionam corretamente")
    
    # Min/Max
    costs = [SeatsAeroClient._safe_int("70000"), 
             SeatsAeroClient._safe_int("85000")]
    assert min(costs) == 70000
    assert max(costs) == 85000
    print(f"✅ min/max: {min(costs)} - {max(costs)}")
    
    print()


if __name__ == "__main__":
    print("\n🧪 TESTES DE CONVERSÃO SEGURA DE TIPOS (TYPE SAFETY)\n")
    
    try:
        test_safe_int_basic()
        test_safe_int_edge_cases()
        test_safe_int_with_api_data()
        test_process_with_string_values()
        test_division_operations()
        
        print("=" * 70)
        print("✅ TODOS OS TESTES DE CONVERSÃO PASSARAM!")
        print("=" * 70)
        print("\n💡 O método _safe_int garante que:")
        print("  • Strings numéricas ('77000') são convertidas para int")
        print("  • None é tratado com valor default")
        print("  • Comparações numéricas funcionam (>, >=, ==)")
        print("  • Operações matemáticas funcionam (//, min, max)")
        print("  • Valores inválidos retornam default ao invés de causar erro\n")
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}\n")
        raise
