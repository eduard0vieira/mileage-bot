"""
Renderizador de Templates de Alertas

Este módulo é responsável por transformar objetos FlightBatch
em textos formatados usando templates Jinja2.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.models import FlightBatch


def render_alert(batch: FlightBatch, template_name: str) -> str:
    """
    Renderiza um alerta de voo usando um template Jinja2.
    
    Como funciona:
    1. Carrega o template especificado da pasta templates/
    2. Extrai os dados do objeto FlightBatch
    3. Formata as datas usando os métodos helpers
    4. Injeta tudo no template Jinja2
    5. Retorna o texto final pronto para envio
    
    Args:
        batch: Objeto FlightBatch com os dados do voo
        template_name: Nome do arquivo .j2 na pasta templates/
                      (ex: "padrao_whatsapp.j2", "telegram.j2")
    
    Returns:
        String com o alerta formatado, pronto para copiar/enviar
    
    Exemplo de uso:
        >>> flight = FlightBatch(...)
        >>> alert_text = render_alert(flight, "padrao_whatsapp.j2")
        >>> print(alert_text)  # ou enviar via API
    """
    # Configura o Jinja2 para buscar templates na pasta "templates/"
    # trim_blocks e lstrip_blocks removem espaços em branco desnecessários
    env = Environment(
        loader=FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # Carrega o template especificado
    template = env.get_template(template_name)
    
    # Prepara os dados para injetar no template
    # Note que usamos os métodos "_dict" para templates que precisam iterar
    context = {
        "origin": batch.origin,
        "origin_code": batch.origin_code,
        "origin_flag": batch.origin_flag,
        "destination": batch.destination,
        "dest_code": batch.dest_code,
        "dest_flag": batch.dest_flag,
        "route": batch.route,  # Propriedade computed para compatibilidade
        "airline": batch.airline,
        "program": batch.program,
        "cost": batch.cost,
        "cabin": batch.cabin,
        # Valores numéricos para mostrar variação de preço
        "min_cost": batch.min_cost,
        "max_cost": batch.max_cost,
        # Para templates que usam {% for month, days in ... %}
        "formatted_outbound": batch.get_outbound_dates_dict(),
        "formatted_inbound": batch.get_inbound_dates_dict(),
        "notes": batch.notes
    }
    
    # Renderiza e retorna o texto final
    return template.render(context)


def main():
    """
    Exemplo de uso do render_alert com dados reais.
    Execute: python -m src.renderer
    """
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    
    # Cria um exemplo de voo
    flight = FlightBatch(
        origin="São Paulo",
        origin_code="GRU",
        origin_flag="🇧🇷",
        destination="Miami",
        dest_code="MIA",
        dest_flag="🇺🇸",
        airline="Latam",
        program="Privilege Club",
        cost="77k Avios",
        cabin="Executiva",
        dates_outbound=[
            ("2026-02-15", 9),
            ("2026-02-18", 4),
            ("2026-03-01", 2)
        ],
        dates_inbound=[
            ("2026-02-20", 7),
            ("2026-03-05", 3)
        ],
        notes="💡 Taxas em torno de R$ 600. Melhor disponibilidade às quartas."
    )
    
    # Renderiza o alerta usando o template do WhatsApp
    alert_text = render_alert(flight, "padrao_whatsapp.j2")
    
    # Mostra o resultado formatado no terminal
    console.print("\n[bold green]✅ Alerta Renderizado com Sucesso![/bold green]\n")
    console.print(Panel(
        alert_text,
        title="📱 Padrão WhatsApp",
        border_style="green",
        padding=(1, 2)
    ))
    
    console.print("\n[dim]💾 Você pode copiar este texto e colar direto no WhatsApp/Telegram![/dim]\n")


if __name__ == "__main__":
    main()
