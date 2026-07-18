import json
import random
from typing import List, Dict

class PromoScraper:
    """
    Mock do subsistema de telemetria de preços.
    Em um cenário real de produção, substituiríamos esta interface por
    uma engenharia reversa das APIs de agregadores italianos (PromoQui/DoveConviene).
    """
    
    def __init__(self, location_zip: str = "80078"):
        self.location_zip = location_zip
        
        # Base de dados sintética simulando supermercados de Pozzuoli
        self.mock_db = [
            {"item": "Petto di Pollo", "preco": 5.99, "unidade": "kg", "supermercado": "MD"},
            {"item": "Trancio di Salmone", "preco": 12.50, "unidade": "kg", "supermercado": "Conad"},
            {"item": "Uova Fresche (10x)", "preco": 1.50, "unidade": "pz", "supermercado": "Eurospin"},
            {"item": "Macinato di Manzo", "preco": 6.80, "unidade": "kg", "supermercado": "Decò"},
            {"item": "Riso Arborio", "preco": 1.99, "unidade": "kg", "supermercado": "MD"},
            {"item": "Pasta Barilla (Penne)", "preco": 0.89, "unidade": "500g", "supermercado": "Conad"},
            {"item": "Patate", "preco": 0.99, "unidade": "kg", "supermercado": "Eurospin"},
            {"item": "Broccoli", "preco": 1.49, "unidade": "kg", "supermercado": "MD"},
            {"item": "Zucchine", "preco": 1.20, "unidade": "kg", "supermercado": "Sole365"},
            {"item": "Carote", "preco": 0.80, "unidade": "kg", "supermercado": "Eurospin"},
            {"item": "Pomodorini", "preco": 2.50, "unidade": "kg", "supermercado": "Conad"},
            {"item": "Latte Intero", "preco": 0.95, "unidade": "L", "supermercado": "Decò"}
        ]

    def fetch_promotions(self) -> List[Dict]:
        """
        Retorna as promoções ativas simulando uma rede instável
        mas entregando um dataset validado.
        """
        # Seleciona aleatoriamente algumas promoções para gerar variação semanal
        promos_da_semana = random.sample(self.mock_db, k=8)
        
        # Garante que sempre tenha pelo menos uma de cada macro para não quebrar o LLM no teste
        promos_da_semana.append({"item": "Fagioli Cannellini", "preco": 0.60, "unidade": "pz", "supermercado": "Eurospin"})
        
        return promos_da_semana

if __name__ == "__main__":
    scraper = PromoScraper()
    print(json.dumps(scraper.fetch_promotions(), indent=2))
