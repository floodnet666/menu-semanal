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

class Refeicao(BaseModel):
    dia: str = Field(description="Dia da semana (ex: Segunda-feira)")
    tipo: str = Field(description="Almoço ou Jantar")
    prato: Prato

class MenuSemanal(BaseModel):
    refeicoes: List[Refeicao]

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
        Sua tarefa é gerar um menu para 7 dias (Almoço e Jantar) para 2 adultos e 1 criança de 3 anos.
        
        RESTRIÇÕES IMUTÁVEIS:
        1. Toda refeição DEVE conter: 1 Proteína, 1 Carboidrato, 1 Vegetal.
        2. RESTRIÇÃO VEGETAL: Um dos adultos possui restrição com vegetais misturados. 
           Portanto, o componente vegetal DEVE SER COMPLETAMENTE ISOLADO (ex: servido cru, a vapor em recipiente separado). 
           NUNCA sugira pratos onde o vegetal é inerente ao cozimento do prato principal (ex: Torta de espinafre, Risoto de abobrinha). 
           Arroz branco + Frango grelhado + Brócolis a vapor (separado) é o formato correto.
        3. Fator Criança: Os pratos principais devem ter baixa complexidade palatável (kid-friendly).
        4. O tempo de preparo de cada prato não pode exceder 30 minutos.
        5. Utilize preferencialmente os ingredientes da lista de promoções enviada. Complete com ingredientes básicos de despensa.
        
        Você retornará ESTRITAMENTE o JSON compatível com o schema solicitado, sem marcações ou alucinações verbais.
        """

        prompt_usuario = f"""
        Lista de promoções ativas em Pozzuoli nesta semana:
        {json.dumps(promos, indent=2)}
        
        Gere as 14 refeições.
        """

        # O modelo padrão para raciocínio complexo estruturado (Gemini 2.5 Pro ou Flash)
        # Vamos usar o gemini-2.5-flash pela velocidade e competência estrutural.
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
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
