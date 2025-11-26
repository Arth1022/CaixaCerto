import flet as ft
from datetime import datetime
from IA import AIManager 

class DespesasScreen(ft.Column):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.ai = AIManager()
        self.scroll = ft.ScrollMode.AUTO
        
        self.date_picked = datetime.now()
        self.txt_date = ft.Text(value=self.date_picked.strftime("%d/%m/%Y"))

        self.tf_desc = ft.TextField(label="Descrição (Ex: Luz, Aluguel)", expand=True)
        self.tf_valor = ft.TextField(label="Valor (R$)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        
        self.dd_categoria = ft.Dropdown(
            label="Categoria",
            width=200,
            options=[
                ft.dropdown.Option("Fixa (Aluguel, Net)"),
                ft.dropdown.Option("Variável (Manutenção)"),
                ft.dropdown.Option("Funcionários"),
                ft.dropdown.Option("Impostos"),
                ft.dropdown.Option("Outros"),
            ],
            dense=True
        )

        self.date_picker = ft.DatePicker(on_change=self.change_date)

        btn_salvar = ft.ElevatedButton(
            "Lançar Despesa",
            icon=ft.Icons.MONEY_OFF,  
            bgcolor="red",
            color="white",
            height=50,
            on_click=self.salvar_despesa
        )

        form_container = ft.Container(
            padding=20,
            bgcolor="white",
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=5, color="black12"),
            content=ft.Column([
                ft.Text("Lançamento de Contas", size=20, weight="bold", color="red"),
                ft.Row([self.tf_desc, self.tf_valor]),
                ft.Row([
                    self.dd_categoria,
                    ft.ElevatedButton(
                        "Data Vencimento", 
                        icon=ft.Icons.CALENDAR_MONTH, 
                        on_click=lambda _: self.page.open(self.date_picker)
                    ),
                    self.txt_date
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=20, color="transparent"),
                ft.Row([btn_salvar], alignment=ft.MainAxisAlignment.END)
            ])
        )

        self.tabela_despesas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Data")),
                ft.DataColumn(ft.Text("Descrição")),
                ft.DataColumn(ft.Text("Categoria")),
                ft.DataColumn(ft.Text("Valor"), numeric=True),
            ],
            rows=[]
        )

        
        self.btn_ia = ft.ElevatedButton(
            "Analisar Gastos", 
            icon=ft.Icons.AUTO_AWESOME, 
            bgcolor="purple", 
            color="white",
            on_click=self.abrir_analise_ia
        )

        self.controls = [
            ft.Text("Controle de Despesas", size=30, weight="bold"),
            ft.Text("Lance aqui contas que não são de estoque (Luz, Água, Salários).", color="grey700"),
            ft.Divider(height=20, color="transparent"),
            form_container,
            ft.Divider(height=20, color="transparent"),
            
            ft.Row([
                ft.Text("Últimos Lançamentos", size=20, weight="bold"),
                self.btn_ia
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            ft.Container(
                content=self.tabela_despesas,
                border=ft.border.all(1, "grey300"),
                border_radius=10,
                padding=10
            )
        ]

    def did_mount(self):
        self.carregar_tabela()

    def abrir_analise_ia(self, e):
        bs_loading = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Divider(height=10, color="transparent"),
                    ft.Text("Analisando suas despesas...", weight="bold"),
                    ft.Text("Verificando onde você pode economizar.", size=12, color="grey")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30, height=180, alignment=ft.alignment.center
            ),
            dismissible=False
        )
        self.page.open(bs_loading)
        self.page.update()

        try:
            mes = self.date_picked.month
            ano = self.date_picked.year
            
            resumo_texto = self.db.get_monthly_summary_text(mes, ano)
            
            resp = self.ai.analisar_dados(f"Foque na análise de despesas: {resumo_texto}")

            self.page.close(bs_loading)

            res_bs = ft.BottomSheet(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                [
                                    ft.Text("Controle de Despesas", weight="bold", size=20, color="black"),
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
            self.show_snack(f"Erro na IA: {ex}", "red")

    def change_date(self, e):
        self.date_picked = self.date_picker.value
        self.txt_date.value = self.date_picked.strftime("%d/%m/%Y")
        self.update()

    def salvar_despesa(self, e):
        if not self.tf_desc.value or not self.tf_valor.value or not self.dd_categoria.value:
            self.show_snack("Preencha todos os campos!", "red")
            return

        try:
            valor = float(self.tf_valor.value.replace(',', '.'))
            if valor <= 0: raise ValueError

            sucesso, msg = self.db.registrar_despesa(
                descricao=self.tf_desc.value,
                valor=valor,
                categoria=self.dd_categoria.value,
                date_obj=self.date_picked
            )

            if sucesso:
                self.show_snack(msg, "green")
                self.tf_desc.value = ""
                self.tf_valor.value = ""
                self.carregar_tabela() 
                self.update()
            else:
                self.show_snack(msg, "red")

        except ValueError:
            self.show_snack("Valor inválido!", "red")

    def carregar_tabela(self):
        despesas = self.db.get_recent_expenses()
        self.tabela_despesas.rows.clear()
        
        for item in despesas:
            valor = item.get('cust', 0)
            cat = item.get('categoria', '-')
            
            self.tabela_despesas.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item.get('data', ''))),
                    ft.DataCell(ft.Text(item.get('nome', ''))),
                    ft.DataCell(ft.Text(cat)),
                    ft.DataCell(ft.Text(f"R$ {valor:.2f}", color="red", weight="bold")),
                ])
            )
        self.update()

    def show_snack(self, text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        self.page.open(snack)
        self.page.update()