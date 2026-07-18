import os
from dotenv import load_dotenv
from data_ingestion import PromoScraper
from menu_engine import MenuEngine
from google_sync import GoogleSync

def main():
    print("[Log] Iniciando o Sistema de Otimização de Menu e Compras.")
    
    # 1. Carrega variáveis de ambiente
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY ausente.")
    if not os.environ.get("SPREADSHEET_ID"):
        raise ValueError("SPREADSHEET_ID ausente.")
        
    # 2. Ingestão de Dados
    print("[Log] Buscando promoções locais (Pozzuoli)...")
    scraper = PromoScraper()
    promos = scraper.fetch_promotions()
    
    # 3. Processamento Lógico via LLM
    print("[Log] Sintetizando menu otimizado via LLM...")
    engine = MenuEngine()
    menu_gerado = engine.generate_menu(promos)
    
    # 4. Sincronização de Estado (Frontend Mobile)
    print("[Log] Autenticando com o Google Sheets...")
    sync = GoogleSync(credentials_path="credentials.json")
    
    print("[Log] Escrevendo dados...")
    sync.sync_menu(menu_gerado)
    sync.sync_shopping_list(menu_gerado)
    
    print("[Log] Execução concluída. Sistema sincronizado com os smartphones.")

if __name__ == "__main__":
    main()
