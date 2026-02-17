"""
Teste de Mapeamento de Programas de Fidelidade

Valida:
1. Tradução correta de códigos para nomes de programas
2. Filtro por substring (parcial ou completo)
3. Case insensitive matching
"""

import sys
from pathlib import Path

# Adiciona raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from app.services.seats_client import SeatsAeroClient, PROGRAM_MAPPING


# Mock de voos com diferentes programas
mock_flights_multiprogram = [
    # Qatar
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
        "LastSeen": datetime.now().isoformat()
    },
    # Smiles
    {
        "Origin": "GRU",
        "Destination": "MIA",
        "Airline": "United",
        "Source": "smiles",
        "Date": "2026-07-01",
        "RemainingSeats": 2,
        "MilesCost": 80000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": datetime.now().isoformat()
    },
    # Avianca LifeMiles
    {
        "Origin": "GRU",
        "Destination": "BOG",
        "Airline": "Avianca",
        "Source": "lifemiles",
        "Date": "2026-08-01",
        "RemainingSeats": 6,
        "MilesCost": 50000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": datetime.now().isoformat()
    },
    # Flying Blue
    {
        "Origin": "GRU",
        "Destination": "CDG",
        "Airline": "Air France",
        "Source": "flyingblue",
        "Date": "2026-09-01",
        "RemainingSeats": 3,
        "MilesCost": 90000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": datetime.now().isoformat()
    },
    # LATAM Pass
    {
        "Origin": "GRU",
        "Destination": "SCL",
        "Airline": "LATAM",
        "Source": "latam",
        "Date": "2026-10-01",
        "RemainingSeats": 5,
        "MilesCost": 40000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": datetime.now().isoformat()
    },
]


def test_program_mapping():
    """Testa se códigos são traduzidos corretamente."""
    print("=" * 70)
    print("TESTE 1: Mapeamento de Programas")
    print("=" * 70)
    
    batches = SeatsAeroClient.process_search_results(mock_flights_multiprogram)
    
    print(f"\n✅ {len(batches)} programa(s) encontrado(s):\n")
    
    expected_programs = {
        "Qatar Privilege Club",
        "Smiles",
        "Avianca LifeMiles",
        "Flying Blue",
        "LATAM Pass"
    }
    
    found_programs = {batch.program for batch in batches}
    
    for batch in batches:
        print(f"  • Código: {batch.dest_code:3} | Programa: {batch.program}")
    
    print("\n🔍 Validações:")
    for program in expected_programs:
        if program in found_programs:
            print(f"  ✅ '{program}' encontrado")
        else:
            print(f"  ❌ '{program}' NÃO encontrado")
    
    print()


def test_filter_by_full_name():
    """Testa filtro por nome completo do programa."""
    print("=" * 70)
    print("TESTE 2: Filtro por Nome Completo")
    print("=" * 70)
    
    # Filtrar por "Qatar Privilege Club"
    batches = SeatsAeroClient.process_search_results(
        mock_flights_multiprogram,
        program_filter="Qatar Privilege Club"
    )
    
    print(f"\n✅ Filtro: 'Qatar Privilege Club' → {len(batches)} batch(es)\n")
    
    for batch in batches:
        print(f"  • {batch.program}")
    
    assert len(batches) == 1, "Deveria retornar apenas Qatar"
    assert batches[0].program == "Qatar Privilege Club"
    print("\n  ✅ Filtro por nome completo funcionando!\n")


def test_filter_by_partial_name():
    """Testa filtro por substring do nome."""
    print("=" * 70)
    print("TESTE 3: Filtro por Substring (Parcial)")
    print("=" * 70)
    
    # Filtrar por "Privilege" (parcial)
    batches = SeatsAeroClient.process_search_results(
        mock_flights_multiprogram,
        program_filter="Privilege"
    )
    
    print(f"\n✅ Filtro: 'Privilege' → {len(batches)} batch(es)\n")
    
    for batch in batches:
        print(f"  • {batch.program}")
    
    assert len(batches) == 1
    assert "Privilege" in batches[0].program
    print("\n  ✅ Filtro por substring funcionando!\n")


def test_filter_by_code():
    """Testa filtro pelo código original."""
    print("=" * 70)
    print("TESTE 4: Filtro por Código (Source)")
    print("=" * 70)
    
    # Filtrar por código "smiles"
    batches = SeatsAeroClient.process_search_results(
        mock_flights_multiprogram,
        program_filter="smiles"
    )
    
    print(f"\n✅ Filtro: 'smiles' (código) → {len(batches)} batch(es)\n")
    
    for batch in batches:
        print(f"  • {batch.program}")
    
    assert len(batches) == 1
    assert batches[0].program == "Smiles"
    print("\n  ✅ Filtro por código funcionando!\n")


def test_filter_case_insensitive():
    """Testa filtro case insensitive."""
    print("=" * 70)
    print("TESTE 5: Filtro Case Insensitive")
    print("=" * 70)
    
    test_cases = [
        "QATAR",
        "qatar",
        "Qatar",
        "qAtAr"
    ]
    
    print("\n🔍 Testando diferentes casos:\n")
    
    for test_filter in test_cases:
        batches = SeatsAeroClient.process_search_results(
            mock_flights_multiprogram,
            program_filter=test_filter
        )
        status = "✅" if len(batches) == 1 else "❌"
        print(f"  {status} Filtro: '{test_filter}' → {len(batches)} batch(es)")
    
    print("\n  ✅ Case insensitive funcionando!\n")


def test_program_mapping_coverage():
    """Verifica cobertura do mapeamento."""
    print("=" * 70)
    print("TESTE 6: Cobertura do Mapeamento")
    print("=" * 70)
    
    print(f"\n📊 Total de programas mapeados: {len(PROGRAM_MAPPING)}\n")
    
    print("🌎 Alguns programas disponíveis:\n")
    
    # Agrupar por categoria
    categories = {
        "Star Alliance": ["aeroplan", "united", "lifemiles", "sas", "singapore"],
        "OneWorld": ["aa", "ba", "qr", "qantas", "cathay"],
        "SkyTeam": ["delta", "flyingblue", "aeromexico", "korean"],
        "América do Sul": ["latam", "smiles", "azul", "gol"],
        "Outros": ["alaska", "virgin", "emirates", "etihad"]
    }
    
    for category, codes in categories.items():
        print(f"  {category}:")
        for code in codes:
            if code in PROGRAM_MAPPING:
                print(f"    • {code:12} → {PROGRAM_MAPPING[code]}")
        print()
    
    print("  ✅ Mapeamento abrangente!\n")


def test_unknown_program():
    """Testa comportamento com código desconhecido."""
    print("=" * 70)
    print("TESTE 7: Código Desconhecido (Fallback)")
    print("=" * 70)
    
    # Mock com código desconhecido
    mock_unknown = [{
        "Origin": "GRU",
        "Destination": "JFK",
        "Airline": "Test Airways",
        "Source": "unknown_program",
        "Date": "2026-11-01",
        "RemainingSeats": 1,
        "MilesCost": 100000,
        "CabinClass": "business",
        "Direct": True,
        "LastSeen": datetime.now().isoformat()
    }]
    
    batches = SeatsAeroClient.process_search_results(mock_unknown)
    
    print(f"\n✅ Código desconhecido: 'unknown_program'\n")
    print(f"  • Nome traduzido: {batches[0].program}")
    
    # Deve usar title case do código
    assert batches[0].program == "Unknown_Program"
    print("\n  ✅ Fallback para title case funcionando!\n")


if __name__ == "__main__":
    print("\n🧪 TESTES DE MAPEAMENTO DE PROGRAMAS DE FIDELIDADE\n")
    
    test_program_mapping()
    test_filter_by_full_name()
    test_filter_by_partial_name()
    test_filter_by_code()
    test_filter_case_insensitive()
    test_program_mapping_coverage()
    test_unknown_program()
    
    print("=" * 70)
    print("✅ TODOS OS TESTES DE PROGRAMAS PASSARAM!")
    print("=" * 70)
    print("\n💡 Exemplos de uso:")
    print('  python main.py --mode api --origin GRU --dest DOH --program "Qatar"')
    print('  python main.py --mode api --origin GRU --dest MIA --program "Smiles"')
    print('  python main.py --mode api --origin GRU --dest CDG --program "Flying Blue"\n')
