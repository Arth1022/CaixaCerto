import flet as ft
from datetime import datetime
from IA import AIManager 

class ClientesScreen(ft.Column):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.ai = AIManager() 
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20
        
        # Botão de recarregar
        self.btn_refresh = ft.IconButton(
            icon=ft.Icons.REFRESH, 
            tooltip="Atualizar Lista", 
            on_click=lambda e: self.carregar_clientes()
        )
        
        # Botão IA
        self.btn_ia = ft.ElevatedButton(
            "Consultor CRM", 
            icon=ft.Icons.AUTO_AWESOME, 
            bgcolor="purple", 
            color="white", 
            on_click=self.abrir_analise_crm
        )

        self.tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Telefone")),
                ft.DataColumn(ft.Text("Pedidos"), numeric=True),
                ft.DataColumn(ft.Text("Última Compra")),
                ft.DataColumn(ft.Text("Status")),
            ],
            rows=[]
        )

        self.controls = [
            ft.Row([
                ft.Text("Gestão de Clientes (CRM)", size=30, weight="bold"),
                ft.Row([self.btn_refresh, self.btn_ia]) # Botões alinhados
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Text("Histórico de compras e frequência.", color="grey"),
            ft.Divider(),
            
            ft.Container(
                content=self.tabela,
                border=ft.border.all(1, "grey300"),
                border_radius=10,
                padding=10
            )
        ]

    def did_mount(self):
        self.carregar_clientes()

    # --- LÓGICA DA IA ---
    def abrir_analise_crm(self, e):
        bs_loading = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Divider(height=10, color="transparent"),
                    ft.Text("Analisando comportamento dos clientes...", weight="bold"),
                    ft.Text("Identificando Correntes e Sumidos.", size=12, color="grey")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30, height=180, alignment=ft.alignment.center
            ),
            dismissible=False
        )
        self.page.open(bs_loading)
        self.page.update()

        try:
            clientes = self.db.get_clientes()
            hoje = datetime.now()
            
            if not clientes:
                dados_texto = "Nenhum cliente cadastrado ainda."
            else:
                dados_texto = "Lista de Clientes:\n"
                for c in clientes:
                    nome = c.get('nome', 'Anonimo')
                    total = c.get('total_pedidos', 0)
                    ultima = c.get('ultima_compra')
                    
                    dias_sem_comprar = "Nunca"
                    if ultima:
                        dias_sem_comprar = (hoje - ultima).days
                    
                    dados_texto += f"- {nome}: {total} pedidos totais. Última compra há {dias_sem_comprar} dias.\n"

            resp = self.ai.analisar_dados(dados_texto, contexto="clientes")

            self.page.close(bs_loading)

            res_bs = ft.BottomSheet(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                [
                                    ft.Text("Controle Financeiro", weight="bold", size=20, color="black"),
                                    ft.IconButton(
                                        icon=ft.Icons.CLOSE, 
                                        icon_color="red", 
                                        tooltip="Fechar",
                                        on_click=lambda _: self.page_ref.close(res_bs)
                                    )
                                ], 
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(),
                            
                            ft.Markdown(
                                resp, 
                                selectable=True, 
                                extension_set="gitHubWeb",
                                on_tap_link=lambda e: self.page_ref.launch_url(e.data)
                            )
                        ],
            
                        scroll=ft.ScrollMode.HIDDEN, 
                    ),
                    padding=25,
                    height=600, 
                    bgcolor="white",
                    border_radius=ft.border_radius.only(top_left=25, top_right=25) 
                ),
                dismissible=True
            )
            self.page.open(res_bs)
            self.page.update()

        except Exception as ex:
            self.page.close(bs_loading)
            print(f"Erro IA: {ex}") 

    # --- LÓGICA PADRÃO ---
    def carregar_clientes(self):
        clientes = self.db.get_clientes()
        self.tabela.rows.clear()
        
        if not clientes:
            self.update()
            return
        
        hoje = datetime.now()
        
        for c in clientes:
            nome = c.get('nome', 'Sem Nome')
            tel = c.get('telefone', '-')
            total = c.get('total_pedidos', 0)
            
            ultima = c.get('ultima_compra')
            data_str = "-"
            
            status_icon = ft.Icon(ft.Icons.CIRCLE, color="green", size=15, tooltip="Cliente Ativo")
            
            if ultima and isinstance(ultima, datetime):
                data_str = ultima.strftime("%d/%m/%Y")
                dias_sem_comprar = (hoje - ultima).days
                
                if dias_sem_comprar > 60:
                    status_icon = ft.Icon(ft.Icons.WARNING, color="red", size=15, tooltip=f"Inativo há {dias_sem_comprar} dias!")
                elif dias_sem_comprar > 30:
                    status_icon = ft.Icon(ft.Icons.CIRCLE, color="orange", size=15, tooltip=f"Ausente há {dias_sem_comprar} dias.")
            
            self.tabela.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(nome)),
                    ft.DataCell(ft.Text(tel)),
                    ft.DataCell(ft.Text(str(total))),
                    ft.DataCell(ft.Text(data_str)),
                    ft.DataCell(status_icon),
                ])
            )
        self.update()