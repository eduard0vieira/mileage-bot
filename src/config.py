"""
Configuration module for Mileage Bot

Loads environment variables and provides centralized config.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Load .env file from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Centralized configuration class."""
    
    # Seats.aero API
    SEATS_API_KEY = os.getenv('SEATS_API_KEY')
    SEATS_BASE_URL = 'https://seats.aero/partnerapi'
    
    @classmethod
    def validate(cls):
        """
        Validates required environment variables.
        Raises ValueError with helpful message if missing.
        """
        if not cls.SEATS_API_KEY:
            raise ValueError(
                "❌ SEATS_API_KEY não encontrada!\n\n"
                "Para usar a integração com Seats.aero:\n"
                "1. Crie um arquivo .env na raiz do projeto\n"
                "2. Adicione: SEATS_API_KEY=sua_chave_aqui\n"
                "3. Rode o script novamente\n\n"
                "Exemplo de .env:\n"
                "SEATS_API_KEY=sk_live_abc123xyz789\n"
            )
    
    @classmethod
    def is_seats_enabled(cls) -> bool:
        """Check if Seats.aero integration is configured."""
        return bool(cls.SEATS_API_KEY)


# Auto-validate on import (can be disabled if needed)
if __name__ != "__main__":
    # Only validate if someone tries to use the API
    pass
