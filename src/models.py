"""
Models for Flight Alert CLI

Este módulo define as estruturas de dados principais do projeto.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
import arrow
from collections import defaultdict


@dataclass
class FlightBatch:
    """
    Representa um lote de alertas de voos com datas disponíveis.
    
    Attributes:
        origin: Cidade de origem (ex: 'São Paulo', 'Rio de Janeiro')
        origin_code: Código IATA do aeroporto de origem (ex: 'GRU', 'GIG')
        origin_flag: Emoji da bandeira do país de origem (ex: '🇧🇷')
        destination: Cidade de destino (ex: 'Miami', 'Lisboa')
        dest_code: Código IATA do aeroporto de destino (ex: 'MIA', 'LIS')
        dest_flag: Emoji da bandeira do país de destino (ex: '🇺🇸', '🇵🇹')
        airline: Nome da companhia aérea (ex: 'Latam')
        program: Programa de fidelidade usado (ex: 'Privilege Club')
        cost: Custo em milhas/pontos (ex: '77k Avios')
        cabin: Classe de voo (ex: 'Executiva', 'Econômica')
        dates_outbound: Lista de tuplas (data_iso, assentos_disponíveis)
                       Exemplo: [("2026-02-15", 9), ("2026-02-18", 4)]
        dates_inbound: Lista de tuplas (data_iso, assentos_disponíveis)
        notes: Observações e dicas extras sobre o voo
    """
    origin: str
    origin_code: str
    origin_flag: str
    destination: str
    dest_code: str
    dest_flag: str
    airline: str
    program: str
    cost: str
    cabin: str
    dates_outbound: List[Tuple[str, int]]
    dates_inbound: List[Tuple[str, int]]
    notes: str
    
    @property
    def route(self) -> str:
        """
        Propriedade de compatibilidade: retorna a rota no formato 'ORIGEM - DESTINO'.
        
        Por que criar esta propriedade?
        - Alguns templates antigos ainda podem usar {{ route }}
        - Facilita migração gradual do código
        """
        return f"{self.origin} - {self.destination}"
    
    def format_dates_by_month(self, dates: List[Tuple[str, int]], lang: str = 'pt_BR') -> str:
        """
        Agrupa e formata datas por mês/ano com dia da semana e assentos em português.
        
        NOVA VERSÃO: Agora aceita tuplas (data, assentos) e formata como "dd (assentos)"
        
        Por que mudou?
        - Antes: [("2026-02-15")] → "15 (Sex)"
        - Agora: [("2026-02-15", 9)] → "15 (9)"
        - O número entre parênteses agora é a QUANTIDADE DE ASSENTOS disponíveis
        
        Args:
            dates: Lista de tuplas (data_iso, assentos_disponíveis)
                   Exemplo: [("2026-02-15", 9), ("2026-02-18", 4)]
            lang: Locale para formatação (padrão: pt_BR)
        
        Returns:
            String formatada agrupada por mês/ano
            Exemplo: "Fev 2026: 15 (9), 18 (4) | Mar 2026: 01 (2)"
        """
        if not dates:
            return "Nenhuma data disponível"
        
        # Dicionário para agrupar datas por mês/ano
        grouped = defaultdict(list)
        
        for date_str, seats in dates:
            # Converte string ISO para objeto Arrow
            date_obj = arrow.get(date_str)
            
            # Chave: "Fev 2026" (mês abreviado + ano)
            month_year_key = date_obj.format('MMM YYYY', locale=lang)
            
            # Valor: "15 (9)" (dia + assentos disponíveis)
            day_seats = f"{date_obj.format('DD')} ({seats})"
            
            grouped[month_year_key].append(day_seats)
        
        # Monta string final: "Fev 2026: 15 (9), 18 (4) | Mar 2026: ..."
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
    
    def get_dates_grouped_dict(self, dates: List[Tuple[str, int]], lang: str = 'pt_BR') -> Dict[str, str]:
        """
        Agrupa datas por mês/ano e retorna um DICIONÁRIO (para usar em templates Jinja2).
        
        NOVA VERSÃO: Agora trabalha com tuplas (data, assentos)
        
        Por que criar este método separado?
        - O método `format_dates_by_month()` retorna uma STRING: "Fev 2026: 15 (9), 18 (4)"
        - Mas para usar no Jinja2 com `{% for month, days in ... %}`, precisamos de um DICT
        - Retorna: {"Fev 2026": "15 (9), 18 (4)", "Mar 2026": "01 (2)"}
        
        Args:
            dates: Lista de tuplas (data_iso, assentos_disponíveis)
            lang: Locale para formatação (padrão: pt_BR)
        
        Returns:
            Dicionário onde:
            - chave = mês/ano (ex: "Fev 2026")
            - valor = dias com assentos (ex: "15 (9), 18 (4)")
        """
        if not dates:
            return {}
        
        grouped = defaultdict(list)
        
        for date_str, seats in dates:
            date_obj = arrow.get(date_str)
            month_year_key = date_obj.format('MMM YYYY', locale=lang)
            day_seats = f"{date_obj.format('DD')} ({seats})"
            grouped[month_year_key].append(day_seats)
        
        # Converte defaultdict para dict normal e junta os dias com vírgula
        return {month: ", ".join(days) for month, days in grouped.items()}
    
    def get_outbound_dates_dict(self) -> Dict[str, str]:
        """Retorna datas de ida como dicionário (para usar em templates)."""
        return self.get_dates_grouped_dict(self.dates_outbound)
    
    def get_inbound_dates_dict(self) -> Dict[str, str]:
        """Retorna datas de volta como dicionário (para usar em templates)."""
        return self.get_dates_grouped_dict(self.dates_inbound)
