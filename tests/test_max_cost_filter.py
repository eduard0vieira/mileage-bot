"""
Teste para validar filtro de custo máximo.

O filtro --max-cost descarta voos com custo acima do limite especificado.
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.seats_client import SeatsAeroClient
from datetime import datetime


def test_max_cost_filter_basic():
    """Teste 1: Filtro de custo máximo básico."""
    print("\n" + "=" * 70)
    print("TESTE 1: Filtro de Custo Máximo Básico")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'United',
            'Source': 'united',
            'Date': '2026-06-15',
            'MilesCost': 50000,  # Abaixo do limite
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'United',
            'Source': 'united',
            'Date': '2026-06-16',
            'MilesCost': 150000,  # Acima do limite
            'RemainingSeats': 2,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # Filtrar com limite de 100k
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        max_cost_filter=100000
    )
    
    assert len(batches) == 1
    assert batches[0].min_cost == 50000
    assert len(batches[0].dates_outbound) == 1  # Apenas 1 data válida
    print(f"✅ Filtro max_cost=100000 aplicado")
    print(f"   Voos aceitos: 50000 milhas")
    print(f"   Voos rejeitados: 150000 milhas")
    print()


def test_max_cost_filter_removes_entire_batch():
    """Teste 2: Batch inteiro removido se todos voos ultrapassam limite."""
    print("=" * 70)
    print("TESTE 2: Batch Removido Completamente")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'DOH',
            'Airline': 'Qatar Airways',
            'Source': 'qr',
            'Date': '2026-06-15',
            'MilesCost': 150000,  # Acima do limite
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'DOH',
            'Airline': 'Qatar Airways',
            'Source': 'qr',
            'Date': '2026-06-16',
            'MilesCost': 200000,  # Muito acima do limite
            'RemainingSeats': 2,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # Filtrar com limite de 100k
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        max_cost_filter=100000
    )
    
    assert len(batches) == 0  # Nenhum batch criado
    print(f"✅ Batch completamente removido (todos voos > 100k)")
    print(f"   Voos rejeitados: 150000, 200000 milhas")
    print()


def test_max_cost_filter_keeps_all_if_below():
    """Teste 3: Mantém todos se estiverem abaixo do limite."""
    print("=" * 70)
    print("TESTE 3: Todos Voos Mantidos (Abaixo do Limite)")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'GIG',
            'Airline': 'LATAM',
            'Source': 'latam',
            'Date': '2026-06-15',
            'MilesCost': 12000,
            'RemainingSeats': 9,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'GIG',
            'Airline': 'LATAM',
            'Source': 'latam',
            'Date': '2026-06-16',
            'MilesCost': 15000,
            'RemainingSeats': 7,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'GIG',
            'Airline': 'LATAM',
            'Source': 'latam',
            'Date': '2026-06-17',
            'MilesCost': 18000,
            'RemainingSeats': 5,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # Filtrar com limite alto (50k)
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        max_cost_filter=50000
    )
    
    assert len(batches) == 1
    assert len(batches[0].dates_outbound) == 3  # Todas as 3 datas mantidas
    assert batches[0].min_cost == 12000
    assert batches[0].max_cost == 18000
    print(f"✅ Todos voos mantidos (12k, 15k, 18k < 50k)")
    print()


def test_max_cost_filter_none_means_no_filter():
    """Teste 4: None desabilita o filtro."""
    print("=" * 70)
    print("TESTE 4: max_cost_filter=None Desabilita Filtro")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'SYD',
            'Airline': 'Qantas',
            'Source': 'qantas',
            'Date': '2026-06-15',
            'MilesCost': 500000,  # Valor muito alto
            'RemainingSeats': 1,
            'Direct': False,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # SEM filtro (None)
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        max_cost_filter=None
    )
    
    assert len(batches) == 1
    assert batches[0].min_cost == 500000
    print(f"✅ Voo de 500k mantido (filtro desabilitado)")
    print()


def test_max_cost_filter_multiple_batches():
    """Teste 5: Filtro aplicado em múltiplos batches."""
    print("=" * 70)
    print("TESTE 5: Filtro em Múltiplos Batches")
    print("=" * 70)
    
    mock_flights = [
        # Batch 1: GRU-MIA (United) - 1 voo barato, 1 caro
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'United',
            'Source': 'united',
            'Date': '2026-06-15',
            'MilesCost': 60000,  # OK
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'United',
            'Source': 'united',
            'Date': '2026-06-16',
            'MilesCost': 120000,  # Muito caro
            'RemainingSeats': 2,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        # Batch 2: GRU-DOH (Qatar) - Todos caros
        {
            'Origin': 'GRU',
            'Destination': 'DOH',
            'Airline': 'Qatar Airways',
            'Source': 'qr',
            'Date': '2026-06-15',
            'MilesCost': 150000,  # Muito caro
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        # Batch 3: GRU-GIG (LATAM) - Todos baratos
        {
            'Origin': 'GRU',
            'Destination': 'GIG',
            'Airline': 'LATAM',
            'Source': 'latam',
            'Date': '2026-06-15',
            'MilesCost': 12000,  # Barato
            'RemainingSeats': 9,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'GIG',
            'Airline': 'LATAM',
            'Source': 'latam',
            'Date': '2026-06-16',
            'MilesCost': 15000,  # Barato
            'RemainingSeats': 7,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # Filtrar com limite de 80k
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        max_cost_filter=80000
    )
    
    # Deve ter 2 batches (United parcial, LATAM completo)
    # Qatar removido completamente
    assert len(batches) == 2
    
    # Verificar United (apenas 1 data)
    united_batch = [b for b in batches if 'United' in b.airline][0]
    assert len(united_batch.dates_outbound) == 1
    assert united_batch.min_cost == 60000
    
    # Verificar LATAM (2 datas)
    latam_batch = [b for b in batches if 'LATAM' in b.airline][0]
    assert len(latam_batch.dates_outbound) == 2
    assert latam_batch.min_cost == 12000
    assert latam_batch.max_cost == 15000
    
    print(f"✅ Filtro aplicado corretamente:")
    print(f"   United: 1/2 datas mantidas (60k OK, 120k rejeitado)")
    print(f"   Qatar: batch removido (150k rejeitado)")
    print(f"   LATAM: 2/2 datas mantidas (12k e 15k OK)")
    print()


def test_max_cost_filter_with_other_filters():
    """Teste 6: max_cost combinado com outros filtros."""
    print("=" * 70)
    print("TESTE 6: max_cost Combinado com Outros Filtros")
    print("=" * 70)
    
    mock_flights = [
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'United',
            'Source': 'united',
            'Date': '2026-06-15',
            'MilesCost': 60000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        },
        {
            'Origin': 'GRU',
            'Destination': 'MIA',
            'Airline': 'LATAM',
            'Source': 'latam',
            'Date': '2026-06-15',
            'MilesCost': 70000,
            'RemainingSeats': 4,
            'Direct': True,
            'LastSeen': datetime.now().isoformat()
        }
    ]
    
    # Filtrar: max_cost=100k E airline="United"
    batches = SeatsAeroClient.process_search_results(
        mock_flights,
        max_cost_filter=100000,
        airline_filter="United"
    )
    
    assert len(batches) == 1
    assert 'United' in batches[0].airline
    assert batches[0].min_cost == 60000
    print(f"✅ Filtros combinados funcionam:")
    print(f"   max_cost=100k: ambos passam")
    print(f"   airline='United': apenas United mantido")
    print()


if __name__ == "__main__":
    print("\n🧪 TESTES DE FILTRO DE CUSTO MÁXIMO\n")
    
    try:
        test_max_cost_filter_basic()
        test_max_cost_filter_removes_entire_batch()
        test_max_cost_filter_keeps_all_if_below()
        test_max_cost_filter_none_means_no_filter()
        test_max_cost_filter_multiple_batches()
        test_max_cost_filter_with_other_filters()
        
        print("=" * 70)
        print("✅ TODOS OS TESTES DE max_cost PASSARAM!")
        print("=" * 70)
        print("\n💡 O filtro --max-cost garante que:")
        print("  • Voos acima do limite são descartados")
        print("  • Batches sem nenhuma data válida são removidos")
        print("  • max_cost=None desabilita o filtro")
        print("  • Funciona combinado com outros filtros")
        print("  • Calcula min_cost e max_cost corretamente após filtro\n")
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}\n")
        raise
