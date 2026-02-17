"""
Renderizador de Templates

Este módulo é responsável por pegar os dados do FlightBatch
e gerar textos formatados usando templates Jinja2.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from src.models import FlightBatch


class TemplateRenderer:
    """
    Classe responsável por renderizar templates de alertas.
    
    Por que criar uma classe separada?
    - Separa a lógica de formatação de datas (models.py) da lógica de templates
    - Facilita trocar/adicionar novos templates no futuro
    - Segue o princípio de Responsabilidade Única (Single Responsibility)
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Inicializa o renderizador de templates.
        
        Args:
            templates_dir: Diretório onde estão os arquivos .j2
        """
        # Configura o Jinja2 para buscar templates na pasta especificada
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,        # Remove espaços em branco extras
            lstrip_blocks=True       # Remove indentação desnecessária
        )
    
    def render_alert(self, flight: FlightBatch, template_name: str = "alert_telegram.j2") -> str:
        """
        Renderiza um alerta de voo usando um template Jinja2.
        
        Args:
            flight: Objeto FlightBatch com os dados do voo
            template_name: Nome do arquivo .j2 a ser usado
        
        Returns:
            String com o alerta formatado pronto para envio
        """
        # Carrega o template
        template = self.env.get_template(template_name)
        
        # Prepara os dados para o template
        # Note que usamos os métodos helper da classe FlightBatch
        context = {
            "route": flight.route,
            "airline": flight.airline,
            "program": flight.program,
            "cost": flight.cost,
            "cabin": flight.cabin,
            "formatted_outbound": flight.get_formatted_outbound_dates(),
            "formatted_inbound": flight.get_formatted_inbound_dates(),
            "notes": flight.notes
        }
        
        # Renderiza e retorna o texto final
        return template.render(context)


def main():
    """Exemplo de uso do TemplateRenderer."""
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    
    # Cria um exemplo de voo
    flight = FlightBatch(
        route="GRU - MIA",
        airline="Latam",
        program="Privilege Club",
        cost="77k Avios",
        cabin="Executiva",
        dates_outbound=["2026-02-15", "2026-02-18", "2026-03-01"],
        dates_inbound=["2026-02-20", "2026-03-05"],
        notes="Taxas em torno de R$ 600. Melhor disponibilidade às quartas."
    )
    
    # Renderiza o alerta
    renderer = TemplateRenderer()
    alert_text = renderer.render_alert(flight)
    
    # Mostra o resultado
    console.print("\n[bold cyan]📱 Alerta Formatado (Telegram):[/bold cyan]\n")
    console.print(Panel(alert_text, border_style="cyan"))


if __name__ == "__main__":
    main()
