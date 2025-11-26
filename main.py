import flet as ft
from database import DatabaseManager
##
from screens.login import LoginScreen
from screens.home import HomeScreen
from screens.relatorio import RelatorioScreen
from screens.cadastro import CadastroScreen
from screens.produtos import ProdutosScreen 
from screens.estoque import EstoqueScreen
from screens.despesas import DespesasScreen
from screens.caderno import CadernoScreen
from screens.clientes import ClientesScreen
from screens.config import ConfiguracoesScreen
from screens.cozinha import CozinhaScreen

def main(page: ft.Page):
    page.title = "Sistema CaixaCerto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_min_width = 800
    page.window_min_height = 600

    db = DatabaseManager()
    main_content = ft.Container(expand=True, padding=20)
    screens = {}

    def navigate(e):
        idx = e.control.selected_index
        screen_map = {0: 'home', 1: 'caderno',2:"cozinha", 3: 'relatorio', 4: 'produtos', 5: 'cadastro', 6: 'estoque', 7: 'despesas', 8: 'clientes', 9: 'configuracoes'}
        key = screen_map.get(idx)
        
     
        main_content.content = screens[key]     
        page.update()

    def init_app_layout():
      
        screens['home'] = HomeScreen(db, page) 
        screens['caderno'] = CadernoScreen(db)
        screens['cozinha'] = CozinhaScreen(db, page)
        screens['relatorio'] = RelatorioScreen(db, page)
        screens['produtos'] = ProdutosScreen(db, page) 
        screens['cadastro'] = CadastroScreen(db)
        screens['estoque'] = EstoqueScreen(db)
        screens['despesas'] = DespesasScreen(db) 
        screens['clientes'] = ClientesScreen(db)
        screens['configuracoes'] = ConfiguracoesScreen(db)

        main_content.content = screens['home']

        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.POINT_OF_SALE, 
                    selected_icon=ft.Icons.POINT_OF_SALE_OUTLINED, 
                    label="Caixa"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.BOOK, 
                    selected_icon=ft.Icons.BOOK_OUTLINED, 
                    label="Caderno"
                ),
                ft.NavigationRailDestination(
                    icon= ft.Icons.RECEIPT, 
                    selected_icon= ft.Icons.RECEIPT_OUTLINED, 
                    label="Cozinha"
                ),
                ft.NavigationRailDestination(
                    icon="bar_chart_outlined", 
                    selected_icon="bar_chart", 
                    label="Relatórios"
                ),
                 ft.NavigationRailDestination(
                    icon="shopping_bag_outlined", 
                    selected_icon="shopping_bag", 
                    label="Produtos"
                ),
                ft.NavigationRailDestination(
                    icon="add_box_outlined", 
                    selected_icon="add_box", 
                    label="Cadastro"
                ),
                ft.NavigationRailDestination(
                    icon="inventory_2_outlined", 
                    selected_icon="inventory_2", 
                    label="Estoque"
                ),
                ft.NavigationRailDestination(
                    icon="attach_money_outlined", 
                    selected_icon="money_off", 
                    label="Despesas"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE, 
                    selected_icon=ft.Icons.PEOPLE_OUTLINED, 
                    label="Clientes"
                ),
                ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS, 
                selected_icon=ft.Icons.SETTINGS_OUTLINED, 
                label="Configurações"
                ),
                
            ],
            on_change=navigate,
        )

        page.clean()
        page.add(
            ft.Row(
                [
                    rail,
                    ft.VerticalDivider(width=1),
                    main_content,
                ],
                expand=True,
            )
        )

    def on_login_success():
        init_app_layout()

    page.add(LoginScreen(page, db, on_login_success))

if __name__ == "__main__":
    ft.app(target=main)