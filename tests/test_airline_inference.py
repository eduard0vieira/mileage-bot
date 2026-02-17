"""
Teste para validar inferência de airline via Source.

Quando a API não retorna 'Airline', inferimos a companhia
baseado no programa de milhas (Source).
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.seats_client import SeatsAeroClient, SOURCE_TO_AIRLINE
from datetime import datetime


def test_airline_inference_from_source():
    """Teste 1: Inferir airline via Source quando Airline é None."""
    print("\n" + "=" * 70)
    print("TESTE 1: Inferir Airline via Source")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'DOH',
            # SEM campo 'Airline' ❌
            'Source': 'qr',  # ✅ Qatar Privilege Club
            'Date': '2026-06-15',
            'MilesCost': 70000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 1
    assert batches[0].airline == 'Qatar Airways'  # Inferido de 'qr'
    print(f"✅ Airline inferida: Source 'qr' -> '{batches[0].airline}'")
    print()


def test_airline_inference_multiple_sources():
    """Teste 2: Inferir múltiplas companhias via Source."""
    print("=" * 70)
    print("TESTE 2: Múltiplas Companhias Inferidas")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Source': 'united',  # United Airlines
            'Date': '2026-06-15',
            'MilesCost': 77000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'LIS',
            'Source': 'tap',  # TAP Air Portugal
            'Date': '2026-06-16',
            'MilesCost': 60000,
            'RemainingSeats': 2,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'MAD',
            'Source': 'iberia',  # Iberia
            'Date': '2026-06-17',
            'MilesCost': 55000,
            'RemainingSeats': 3,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 3
    
    # Verificar cada inferência
    airlines = {batch.airline for batch in batches}
    assert 'United Airlines' in airlines
    assert 'TAP Air Portugal' in airlines
    assert 'Iberia' in airlines
    
    print("✅ Inferências corretas:")
    print("  • 'united' -> United Airlines")
    print("  • 'tap' -> TAP Air Portugal")
    print("  • 'iberia' -> Iberia")
    print()


def test_airline_direct_over_inference():
    """Teste 3: Campo direto tem prioridade sobre inferência."""
    print("=" * 70)
    print("TESTE 3: Campo Direto tem Prioridade")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'LATAM Airlines',  # ✅ Campo direto presente
            'Source': 'united',            # Source diferente
            'Date': '2026-06-15',
            'MilesCost': 70000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 1
    # Deve usar 'LATAM Airlines' (campo direto), não 'United' (inferido de source)
    assert batches[0].airline == 'LATAM Airlines'
    print("✅ Campo direto 'Airline' usado ao invés de inferência via Source")
    print(f"   Airline: {batches[0].airline} (Source era 'united')")
    print()


def test_airline_inference_smiles():
    """Teste 4: Smiles inferido corretamente (multi-companhia)."""
    print("=" * 70)
    print("TESTE 4: Inferência Smiles (Multi-Companhia)")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'FOR',
            'Source': 'smiles',  # Smiles é multi-companhia
            'Date': '2026-06-15',
            'MilesCost': 12000,
            'RemainingSeats': 9,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 1
    assert batches[0].airline == 'Gol / Parceiros Smiles'
    print(f"✅ Smiles inferido: '{batches[0].airline}'")
    print("   (Correto, pois Smiles é multi-companhia)")
    print()


def test_airline_inference_unknown_source():
    """Teste 5: Source desconhecido usa .title()."""
    print("=" * 70)
    print("TESTE 5: Source Desconhecido (Fallback .title())")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Source': 'newairline',  # Não mapeado
            'Date': '2026-06-15',
            'MilesCost': 70000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 1
    assert batches[0].airline == 'Newairline'  # .title()
    print(f"✅ Source desconhecido capitalizado: 'newairline' -> '{batches[0].airline}'")
    print()


def test_airline_filter_with_inference():
    """Teste 6: Filtro funciona com airline inferida."""
    print("=" * 70)
    print("TESTE 6: Filtro com Airline Inferida")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'DOH',
            'Source': 'qr',  # Qatar Airways
            'Date': '2026-06-15',
            'MilesCost': 77000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Source': 'united',  # United Airlines
            'Date': '2026-06-16',
            'MilesCost': 85000,
            'RemainingSeats': 2,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # Filtrar apenas Qatar
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        airline_filter="Qatar"
    )
    
    assert len(batches) == 1
    assert batches[0].airline == 'Qatar Airways'
    print(f"✅ Filtro 'Qatar' retornou: '{batches[0].airline}' (inferida de 'qr')")
    
    # Filtrar apenas United
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        airline_filter="United"
    )
    
    assert len(batches) == 1
    assert batches[0].airline == 'United Airlines'
    print(f"✅ Filtro 'United' retornou: '{batches[0].airline}' (inferida de 'united')")
    print()


def test_source_to_airline_mapping_coverage():
    """Teste 7: Verificar cobertura do mapeamento."""
    print("=" * 70)
    print("TESTE 7: Cobertura do SOURCE_TO_AIRLINE")
    print("=" * 70)
    
    # Programas importantes que devem estar mapeados
    expected_sources = [
        'american', 'aa', 'aadvantage',
        'alaska',
        'qatar', 'qr', 'privilege',
        'united',
        'delta',
        'aeromexico',
        'british', 'ba',
        'iberia',
        'tap',
        'azul', 'blue',
        'latam',
        'gol',
        'smiles',
        'lufthansa',
        'turkish',
        'virgin',
        'qantas',
        'flyingblue',
    ]
    
    missing = []
    for source in expected_sources:
        if source not in SOURCE_TO_AIRLINE:
            missing.append(source)
    
    assert len(missing) == 0, f"Mapeamentos faltando: {missing}"
    print(f"✅ {len(SOURCE_TO_AIRLINE)} programas mapeados")
    print(f"✅ Todos os programas importantes estão cobertos")
    
    # Mostrar alguns exemplos
    print("\n📋 Exemplos de mapeamento:")
    examples = ['qr', 'united', 'latam', 'smiles', 'tap']
    for source in examples:
        airline = SOURCE_TO_AIRLINE.get(source, 'N/A')
        print(f"  • '{source}' → {airline}")
    
    print()


def test_airline_inference_brazilian_airlines():
    """Teste 8: Companhias brasileiras inferidas corretamente."""
    print("=" * 70)
    print("TESTE 8: Companhias Brasileiras")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'GIG',
            'Source': 'latam',
            'Date': '2026-06-15',
            'MilesCost': 12000,
            'RemainingSeats': 9,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'SSA',
            'Source': 'azul',
            'Date': '2026-06-16',
            'MilesCost': 15000,
            'RemainingSeats': 7,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'BSB',
            'Source': 'gol',
            'Date': '2026-06-17',
            'MilesCost': 10000,
            'RemainingSeats': 5,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    batches = SeatsAeroClient.process_search_results(mock_flights)
    
    assert len(batches) == 3
    
    airlines = {batch.airline for batch in batches}
    assert 'LATAM Airlines' in airlines
    assert 'Azul' in airlines
    assert 'Gol' in airlines
    
    print("✅ Companhias brasileiras inferidas:")
    print("  • 'latam' -> LATAM Airlines")
    print("  • 'azul' -> Azul")
    print("  • 'gol' -> Gol")
    print()


if __name__ == "__main__":
    print("\n🧪 TESTES DE INFERÊNCIA DE AIRLINE VIA SOURCE\n")
    
    try:
        test_airline_inference_from_source()
        test_airline_inference_multiple_sources()
        test_airline_direct_over_inference()
        test_airline_inference_smiles()
        test_airline_inference_unknown_source()
        test_airline_filter_with_inference()
        test_source_to_airline_mapping_coverage()
        test_airline_inference_brazilian_airlines()
        
        print("=" * 70)
        print("✅ TODOS OS TESTES DE INFERÊNCIA PASSARAM!")
        print("=" * 70)
        print("\n💡 A inferência via Source garante que:")
        print("  • Airline é inferida quando API não retorna o campo")
        print("  • SOURCE_TO_AIRLINE mapeia 30+ programas de fidelidade")
        print("  • Campo direto 'Airline' tem prioridade sobre inferência")
        print("  • Source desconhecido usa .title() como fallback")
        print("  • Filtro --airline funciona com airlines inferidas")
        print("  • Companhias brasileiras (LATAM, Azul, Gol) cobertas")
        print("  • Multi-companhias (Smiles) tratadas corretamente\n")
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}\n")
        raise
