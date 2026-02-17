"""
Models for Flight Alert CLI

Este módulo define as estruturas de dados principais do projeto.
"""

from dataclasses import dataclass
from typing import List
import arrow
from collections import defaultdict


@dataclass
class FlightBatch:
    """
    Representa um lote de alertas de voos com datas disponíveis.
    
    Attributes:
        route: Rota do voo no formato 'ORIGEM - DESTINO' (ex: 'GRU - MIA')
        airline: Nome da companhia aérea (ex: 'Latam')
        program: Programa de fidelidade usado (ex: 'Privilege Club')
        cost: Custo em milhas/pontos (ex: '77k Avios')
        cabin: Classe de voo (ex: 'Executiva', 'Econômica')
        dates_outbound: Lista de datas de ida no formato ISO 'YYYY-MM-DD'
        dates_inbound: Lista de datas de volta no formato ISO 'YYYY-MM-DD'
        notes: Observações e dicas extras sobre o voo
    """
    route: str
    airline: str
    program: str
    cost: str
    cabin: str
    dates_outbound: List[str]
    dates_inbound: List[str]
    notes: str
    
    def format_dates_by_month(self, dates: List[str], lang: str = 'pt_BR') -> str:
        """
        Agrupa e formata datas por mês/ano com dia da semana em português.
        
        Por que esse método existe?
        - Ao invés de mostrar "2026-02-15, 2026-02-18, 2026-03-01", 
          queremos algo mais legível: "Fev 2026: 15 (Sex), 18 (Seg)"
        - Isso facilita a leitura e torna o alerta mais profissional
        
        Args:
            dates: Lista de datas no formato ISO 'YYYY-MM-DD'
            lang: Locale para formatação (padrão: pt_BR)
        
        Returns:
            String formatada agrupada por mês/ano
            Exemplo: "Fev 2026: 15 (Sex), 18 (Seg) | Mar 2026: 01 (Dom)"
        """
        if not dates:
            return "Nenhuma data disponível"
        
        # Dicionário para agrupar datas por mês/ano
        # defaultdict cria automaticamente uma lista vazia se a chave não existir
        grouped = defaultdict(list)
        
        for date_str in dates:
            # Converte string ISO para objeto Arrow (mais poderoso que datetime)
            date_obj = arrow.get(date_str)
            
            # Chave: "Fev 2026" (mês abreviado + ano)
            month_year_key = date_obj.format('MMM YYYY', locale=lang)
            
            # Valor: "15 (Sex)" (dia + dia da semana abreviado)
            day_weekday = date_obj.format('DD (ddd)', locale=lang)
            
            grouped[month_year_key].append(day_weekday)
        
        # Monta string final: "Fev 2026: 15 (Sex), 18 (Seg) | Mar 2026: ..."
        result_parts = []
        for month_year, days in grouped.items():
            days_str = ", ".join(days)
            result_parts.append(f"{month_year}: {days_str}")
        
        return " | ".join(result_parts)
    
    def get_formatted_outbound_dates(self) -> str:
        """Retorna datas de ida formatadas e agrupadas por mês."""
        return self.format_dates_by_month(self.dates_outbound)
    
    def get_formatted_inbound_dates(self) -> str:
        """Retorna datas de volta formatadas e agrupadas por mês."""
        return self.format_dates_by_month(self.dates_inbound)
