import flet as ft
from datetime import datetime
from IA import AIManager

class EstoqueScreen(ft.Column):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.ai = AIManager()
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20
        
        # --- TABELA DE DADOS ---
        self.tabela_estoque = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Produto")),
                ft.DataColumn(ft.Text("Custo Unit."), numeric=True),
                ft.DataColumn(ft.Text("Estoque Atual"), numeric=True),
                ft.DataColumn(ft.Text("Status")),
            ],
            rows=[]
        )

        self.dd_produtos = ft.Dropdown(label="Produto", expand=True, options=[], dense=True)
        self.tf_qtd = ft.TextField(label="Qtd", width=100, value="1", keyboard_type=ft.KeyboardType.NUMBER)
        self.btn_repor = ft.ElevatedButton("Repor (Compra)", icon=ft.Icons.ADD_SHOPPING_CART, bgcolor="green", color="white", on_click=self.repor_estoque)

        form_reposicao = ft.Container(
            padding=15, bgcolor="white", border_radius=10, shadow=ft.BoxShadow(blur_radius=5, color="black12"),
            content=ft.Column([
                ft.Text("Entrada de Mercadoria", weight="bold", color="green"),
                ft.Row([self.dd_produtos, self.tf_qtd, self.btn_repor])
            ])
        )

        # --- BOTÕES DO TOPO ---
        self.btn_ia = ft.ElevatedButton(
            "Análise IA", 
            icon=ft.Icons.INVENTORY, 
            bgcolor="purple", 
            color="white", 
            on_click=self.abrir_painel_ia
        )
        
        self.btn_perda = ft.ElevatedButton(
            "Registrar Perda", 
            icon=ft.Icons.DELETE_FOREVER, 
            bgcolor="red", 
            color="white", 
            on_click=self.abrir_painel_perda
        )

        # --- LAYOUT ---
        self.controls = [
            ft.Row([
                ft.Text("Gestão de Estoque", size=30, weight="bold"), 
                ft.Row([self.btn_perda, self.btn_ia])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            form_reposicao,
            
            ft.Divider(height=20, color="transparent"),
            ft.Text("Inventário Atual", size=20, weight="bold"),
            
            ft.Container(
                content=self.tabela_estoque, 
                border=ft.border.all(1, "grey300"), 
                border_radius=10, 
                padding=10
            )
        ]

    def did_mount(self):
        self.carregar_dados()


    def abrir_painel_perda(self, e):
        dd_prod_perda = ft.Dropdown(label="Produto Perdido", options=self.dd_produtos.options, expand=True)
        tf_qtd_perda = ft.TextField(label="Qtd Perdida", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        dd_motivo = ft.Dropdown(
            label="Motivo",
            options=[
                ft.dropdown.Option("Vencimento"),
                ft.dropdown.Option("Queima/Erro Cozinha"),
                ft.dropdown.Option("Queda/Acidente"),
                ft.dropdown.Option("Consumo Interno"),
            ],
            expand=True
        )

        def confirmar_click(e):
            self.processar_perda(dd_prod_perda.value, tf_qtd_perda.value, dd_motivo.value, bs)

        painel = ft.Container(
            padding=30,
            bgcolor="white",
            border_radius=ft.border_radius.only(top_left=20, top_right=20),
            height=400,
            content=ft.Column([
                ft.Row([
                    ft.Text("Registrar Perda", size=20, weight="bold", color="red"),
                    ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: self.page.close(bs))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Text("Isso baixará o estoque e gerará um prejuízo."),
                dd_prod_perda,
                ft.Row([tf_qtd_perda, dd_motivo]),
                ft.Divider(height=20, color="transparent"),
                ft.ElevatedButton("CONFIRMAR PERDA", bgcolor="red", color="white", height=50, width=200, on_click=confirmar_click)
            ])
        )

        bs = ft.BottomSheet(content=painel, dismissible=True)
        self.page.open(bs)
        self.page.update()

    def processar_perda(self, nome, qtd_str, motivo, bs_instance):
        if not nome or not qtd_str or not motivo:
            self.show_snack("Preencha tudo!", "red")
            return
        
        try:
            qtd = float(qtd_str.replace(',', '.'))
            sucesso, msg = self.db.registrar_perda(nome, qtd, motivo, datetime.now())
            
            self.page.close(bs_instance) # Fecha o painel
            
            if sucesso:
                self.show_snack(msg, "orange")
                self.carregar_dados()
            else:
                self.show_snack(msg, "red")
        except ValueError:
            self.show_snack("Quantidade inválida", "red")



    def abrir_painel_ia(self, e):
        bs_loading = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Divider(height=10, color="transparent"),
                    ft.Text("Analisando Balanço...", weight="bold"),
                    ft.Text("Verificando lucros, despesas e tendências.", size=12, color="grey")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30, height=180, alignment=ft.alignment.center
            ),
            dismissible=False
        )
        
        bs_ia = ft.BottomSheet(content=bs_loading, dismissible=False)
        self.page.open(bs_ia)
        self.page.update()

        try:
            dados = self.db.get_inventory_text()
            resp = self.ai.analisar_dados(dados, contexto="estoque")
            
            self.page.close(bs_ia) 
            resultado_content = ft.Container(
                padding=30, bgcolor="white", height=500,
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.AUTO_AWESOME, color="purple"),
                        ft.Text("Gerente de Logística", weight="bold", size=20, color="purple"),
                        ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: self.page.close(bs_res))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Column([
                        ft.Markdown(resp, selectable=True, extension_set="gitHubWeb")
                    ], scroll=ft.ScrollMode.AUTO, expand=True)
                ])
            )
            
            bs_res = ft.BottomSheet(content=resultado_content, dismissible=True, enable_drag=True)
            self.page.open(bs_res)
            self.page.update()

        except Exception as ex:
            self.page.close(bs_ia)
            self.show_snack(f"Erro IA: {ex}", "red")

    def carregar_dados(self):
        tipos = ['ingrediente', 'bebida']
        nomes = self.db.get_products_names(tipos=tipos)
        self.dd_produtos.options = [ft.dropdown.Option(n) for n in nomes]
        
        prods = self.db.get_all_products(tipos=tipos)
        self.tabela_estoque.rows.clear()
        
        for p in prods:
            est = p.get('estoque', 0)
            custo = p.get('custo', 0)
            uni = p.get('unidade', 'un')
            txt_est = f"{est:.1f} {uni}"
            
            icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color="green") if est > 5 else ft.Icon(ft.Icons.WARNING, color="red")
            color_txt = "black" if est > 5 else "red"
            
            self.tabela_estoque.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(p['nome'])),
                    ft.DataCell(ft.Text(f"R$ {custo:.2f}")),
                    ft.DataCell(ft.Text(txt_est, color=color_txt, weight="bold")),
                    ft.DataCell(icon)
                ])
            )
        self.update()

    def repor_estoque(self, e):
        if not self.dd_produtos.value or not self.tf_qtd.value: return
        try:
            qtd = float(self.tf_qtd.value.replace(',', '.'))
            nome = self.dd_produtos.value
            sucesso, msg = self.db.repor_estoque(nome, qtd, datetime.now())
            if sucesso:
                self.show_snack(msg, "green")
                self.tf_qtd.value = "1"
                self.dd_produtos.value = None
                self.carregar_dados()
            else: self.show_snack(msg, "red")
        except ValueError: self.show_snack("Qtd inválida", "red")

    def show_snack(self, text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        self.page.open(snack)
        self.page.update()