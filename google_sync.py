import os
import gspread
from google.oauth2.service_account import Credentials
from menu_engine import MenuSemanal

class GoogleSync:
    def __init__(self, credentials_path: str = "credentials.json"):
        self.spreadsheet_id = os.environ.get("SPREADSHEET_ID")
        if not self.spreadsheet_id:
            raise ValueError("A variável de ambiente SPREADSHEET_ID não está definida.")
            
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado em {credentials_path}")
            
        from google.oauth2.service_account import Credentials
        credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open_by_key(self.spreadsheet_id)

    def _get_or_create_worksheet(self, title: str):
        try:
            return self.sheet.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            return self.sheet.add_worksheet(title=title, rows=100, cols=10)

    def sync_menu(self, menu: MenuSemanal):
        """Sincroniza o menu gerado na aba 'Menu Semanal'."""
        ws = self._get_or_create_worksheet("Menu Semanal")
        ws.clear()
        
        # Cabeçalhos
        ws.update('A1:E1', [["Dia", "Tipo", "Prato", "Tempo (min)", "Vegetal Isolado"]])
        
        # Formatando header
        ws.format('A1:E1', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}})
        
        linhas = []
        for ref in menu.refeicoes:
            linhas.append([
                ref.dia,
                ref.tipo,
                ref.prato.nome,
                ref.prato.tempo_preparo_minutos,
                ref.prato.vegetal_isolado
            ])
            
        ws.update(f'A2:E{len(linhas)+1}', linhas)
        print("[Log] Menu sincronizado no Google Sheets.")

    def sync_shopping_list(self, menu: MenuSemanal):
        """Sincroniza a lista de compras na aba 'Lista de Compras' com checkboxes."""
        ws = self._get_or_create_worksheet("Lista de Compras")
        ws.clear()
        
        linhas = [["Comprado", "Supermercado", "Quantidade", "Item"]]
        
        for compra in menu.lista_compras:
            linhas.append(["FALSE", compra.supermercado, compra.quantidade, compra.item])
                
        # Atualizando os dados
        ws.update(f'A1:D{len(linhas)}', linhas)
        
        # Formatando Header
        ws.format('A1:D1', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}})
        
        # Inserindo checkboxes (Validação de dados nativa do Google Sheets) na coluna A (de A2 em diante)
        # Requer um request de batch update via a API
        if len(linhas) > 1:
            worksheet_id = ws.id
            body = {
                "requests": [
                    {
                        "setDataValidation": {
                            "range": {
                                "sheetId": worksheet_id,
                                "startRowIndex": 1,
                                "endRowIndex": len(linhas),
                                "startColumnIndex": 0,
                                "endColumnIndex": 1
                            },
                            "rule": {
                                "condition": {
                                    "type": "BOOLEAN"
                                },
                                "showCustomUi": True
                            }
                        }
                    }
                ]
            }
            self.sheet.batch_update(body)
            
        print("[Log] Lista de compras sincronizada no Google Sheets.")
