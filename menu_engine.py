import os
import json
from typing import List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

class Ingrediente(BaseModel):
    nome: str
    quantidade: str
    supermercado: str = Field(description="Supermercado onde está em promoção, se aplicável, senão 'Qualquer'")

class Prato(BaseModel):
    nome: str
    proteina: str
    carboidrato: str
    vegetal_isolado: str = Field(description="Vegetal que DEVE ser preparado separadamente (sem misturar no carb/proteína).")
    tempo_preparo_minutos: int
    ingredientes: List[Ingrediente]

class ItemCompra(BaseModel):
    item: str
    quantidade: str
    supermercado: str = Field(description="Supermercado com a melhor oferta para este item, ou 'Qualquer' se não houver oferta.")

class Refeicao(BaseModel):
    dia: str = Field(description="Dia da semana (ex: Segunda-feira)")
    tipo: str = Field(description="Almoço ou Jantar")
    prato: Prato

class MenuSemanal(BaseModel):
    refeicoes: List[Refeicao]
    lista_compras: List[ItemCompra]

class MenuEngine:
    def __init__(self):
        # Inicializa o cliente Gemini nativo. A API KEY deve estar no ambiente.
        self.client = genai.Client()

    def generate_menu(self, promos: List[dict]) -> MenuSemanal:
        """
        Orquestra a geração do menu utilizando os dados sintéticos de promoção.
        """
        prompt_sistema = """
        Você é um arquiteto nutricional de precisão. 
        Sua tarefa é gerar um menu para 7 dias (Almoço e Jantar) para 2 adultos e 1 criança de 3 anos, além da LISTA DE COMPRAS completa.
        
        RESTRIÇÕES IMUTÁVEIS:
        1. Toda refeição DEVE conter: 1 Proteína, 1 Carboidrato, 1 Vegetal.
        2. RESTRIÇÃO VEGETAL: Um dos adultos possui restrição com vegetais misturados. 
           O componente vegetal DEVE SER COMPLETAMENTE ISOLADO (ex: servido cru, a vapor em recipiente separado). 
           NUNCA sugira pratos onde o vegetal é inerente ao cozimento do prato principal (ex: Torta de espinafre, Risoto de abobrinha). 
           Exemplo correto: Arroz branco + Frango grelhado + Brócolis a vapor (separado).
        3. Fator Criança: Os pratos principais devem ter baixa complexidade palatável (kid-friendly).
        4. O tempo de preparo de cada prato não pode exceder 30 minutos.
        5. Utilize as ofertas enviadas para basear as refeições. Complete com itens de despensa básicos.
        6. Após gerar as refeições, agregue TODOS os ingredientes na 'lista_compras'. 
           Para cada item na lista de compras, indique o supermercado que possui a melhor oferta (baseado nos dados fornecidos), 
           ou 'Qualquer' se não houver oferta específica.
        
        Retorne ESTRITAMENTE o JSON.
        """

        prompt_usuario = f"""
        Lista de ofertas reais ativas nesta semana em Pozzuoli:
        {json.dumps(promos, indent=2)}
        
        Gere as 14 refeições e a lista de compras agregada.
        """

        # O modelo padrão para raciocínio complexo estruturado (Gemini 2.5 Pro ou Flash)
        # Vamos usar o gemini-2.5-flash pela velocidade e competência estrutural.
        
        response = self.client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt_usuario,
            config=types.GenerateContentConfig(
                system_instruction=prompt_sistema,
                response_mime_type="application/json",
                response_schema=MenuSemanal,
                temperature=0.2, # Baixa entropia
            ),
        )
        
        # Pydantic cuidará da validação do JSON retornado pelo modelo.
        # No SDK do google-genai, o response.text contém o JSON serializado garantido pelo modelo.
        return MenuSemanal.model_validate_json(response.text)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Teste isolado
    from data_ingestion import PromoScraper
    promos = PromoScraper().fetch_promotions()
    engine = MenuEngine()
    menu = engine.generate_menu(promos)
    print(menu.model_dump_json(indent=2))
