import os
import json
from typing import List, Dict
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class Oferta(BaseModel):
    item: str
    preco: float
    unidade: str = Field(description="Ex: kg, pz, 500g")
    supermercado: str = Field(description="Onde está em oferta")

class ListaOfertas(BaseModel):
    ofertas: List[Oferta]

class PromoScraper:
    """
    Substituição do Mock. Este módulo utiliza a funcionalidade de Google Search Grounding 
    do Gemini para realizar buscas em tempo real por ofertas em Pozzuoli.
    """
    
    def __init__(self, location_zip: str = "80078", location_name: str = "Pozzuoli (Napoli)"):
        self.location_name = location_name
        self.client = genai.Client()

    def fetch_promotions(self) -> List[Dict]:
        """
        Inicia uma operação autônoma de pesquisa na web via Gemini.
        """
        print(f"[Log] Procurando ofertas reais ativas via Web Search para {self.location_name}...")
        
        prompt = f"""
        Faça uma pesquisa detalhada na web pelas ofertas ativas desta semana (volantini, ofertas de supermercados) 
        para a cidade de {self.location_name}.
        Foque nos supermercados: MD, Conad, Decò, Eurospin, Sole365.
        Retorne pelo menos 15 itens em promoção, focando em proteínas, vegetais e carboidratos úteis para refeições.
        """

        try:
            # Gemini 2.5 Pro ou Flash. Usando pro para melhor capacidade de pesquisa.
            response = self.client.models.generate_content(
                model='gemini-2.5-pro',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                    response_mime_type="application/json",
                    response_schema=ListaOfertas,
                    temperature=0.1
                ),
            )
            data = ListaOfertas.model_validate_json(response.text)
            print(f"[Log] Obtidas {len(data.ofertas)} ofertas do mundo real.")
            return [oferta.model_dump() for oferta in data.ofertas]
        except Exception as e:
            print(f"[Aviso] Falha na telemetria de web search. Utilizando base de fallback. Erro: {e}")
            # Fallback robusto caso o search grounding falhe ou atinja cota limit
            return [
                {"item": "Petto di Pollo", "preco": 5.99, "unidade": "kg", "supermercado": "MD (Fallback)"},
                {"item": "Broccoli", "preco": 1.49, "unidade": "kg", "supermercado": "MD (Fallback)"},
                {"item": "Riso Arborio", "preco": 1.99, "unidade": "kg", "supermercado": "Conad (Fallback)"}
            ]

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    scraper = PromoScraper()
    print(json.dumps(scraper.fetch_promotions(), indent=2))
