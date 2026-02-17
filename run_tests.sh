#!/usr/bin/env bash

# Script para rodar todos os testes do Mileage Bot
# Usage: ./run_tests.sh [options]

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Mileage Bot - Test Runner${NC}"
echo "=================================="
echo ""

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}📦 Ativando ambiente virtual...${NC}"
    source venv/bin/activate
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}⚠️  pytest não encontrado. Rodando testes diretamente com Python...${NC}"
    echo ""
    
    # Run tests directly with Python
    echo -e "${GREEN}🔍 Testando formatação visual...${NC}"
    python tests/test_visual_format.py
    echo ""
    
    echo -e "${GREEN}🔍 Testando funcionalidades avançadas...${NC}"
    python tests/test_advanced_features.py
    echo ""
    
    echo -e "${GREEN}🔍 Testando processamento Seats.aero...${NC}"
    python tests/test_seats_processing.py
    echo ""
    
    echo -e "${GREEN}✅ Todos os testes executados!${NC}"
    echo ""
    echo -e "${YELLOW}💡 Dica: Instale pytest para melhor experiência:${NC}"
    echo "   pip install -r requirements-dev.txt"
else
    # Run with pytest
    echo -e "${GREEN}🚀 Rodando testes com pytest...${NC}"
    echo ""
    
    # Parse arguments
    if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
        pytest tests/ -v --tb=short
    elif [ "$1" = "-c" ] || [ "$1" = "--coverage" ]; then
        pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
        echo ""
        echo -e "${GREEN}📊 Relatório de cobertura gerado em: htmlcov/index.html${NC}"
    elif [ "$1" = "-f" ] || [ "$1" = "--failed" ]; then
        pytest tests/ --lf -v
    else
        pytest tests/
    fi
    
    echo ""
    echo -e "${GREEN}✅ Testes concluídos!${NC}"
fi

echo ""
echo "=================================="
