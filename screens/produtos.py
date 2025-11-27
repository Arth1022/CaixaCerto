import flet as ft

class ProdutosScreen(ft.Column):
    def __init__(self, db_manager, shared_actions=None):
        super().__init__()
        self.db = db_manager
        self.shared_actions = shared_actions 
        self.scroll = ft.ScrollMode.AUTO
        
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Custo"), numeric=True),
                ft.DataColumn(ft.Text("Descrição")),
                ft.DataColumn(ft.Text("Pedido")),
                ft.DataColumn(ft.Text("Ação")), 
            ],
            rows=[]
        )

        self.tf_nome = ft.TextField(label="Produto Selecionado", read_only=True, prefix_icon="label")
        
        self.dd_campo = ft.Dropdown(
            label="Campo",
            options=[
                ft.dropdown.Option("custo"),
                ft.dropdown.Option("descrição"),
                ft.dropdown.Option("pedido"),
            ]
        )
        
        self.tf_valor = ft.TextField(label="Novo Valor")

        self.btn_salvar = ft.ElevatedButton(
            "Salvar Edição", 
            icon="save", 
            bgcolor="blue600", 
            color="white",
            on_click=self.editar
        )
        
        self.btn_excluir = ft.ElevatedButton(
            "Excluir Produto", 
            icon="delete", 
            bgcolor="red600", 
            color="white",
            on_click=self.abrir_confirmacao_exclusao
        )

        self.bs_confirmar = ft.BottomSheet(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Text("Confirmar Exclusão", size=20, weight="bold"),
                        ft.Text("Tem certeza que deseja excluir este produto permanentemente?"),
                        ft.Row(
                            controls=[
                                ft.TextButton("Cancelar", on_click=lambda e: self.fechar_bottom_sheet(e)),
                                ft.TextButton("Excluir", on_click=self.excluir, style=ft.ButtonStyle(color="red")),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        )
                    ]
                )
            )
        )

        self.controls = [
            ft.Text("Gerenciar Produtos", size=30, weight="bold"),
            
            ft.Container(
                content=self.data_table,
                border=ft.border.all(1, "grey300"),
                border_radius=10,
                padding=10,
            ),
            
            ft.Divider(),
            
            ft.Card(
                elevation=5,
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("Editar Selecionado", size=20, weight="bold"),
                        ft.Row([self.tf_nome, self.dd_campo]),
                        self.tf_valor,
                        ft.Row([self.btn_salvar, self.btn_excluir], alignment=ft.MainAxisAlignment.END)
                    ])
                )
            )
        ]

    def did_mount(self):
        self.update_view()

    def update_view(self):
        self.data_table.rows.clear()
       
        prods = self.db.get_all_products()
        
        for p in prods:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(p['nome'])),
                    ft.DataCell(ft.Text(f"R$ {p['custo']}")),
                    ft.DataCell(ft.Text(p.get('descrição', ''))),
                    ft.DataCell(ft.Text(p.get('pedido', ''))),
                    ft.DataCell(
                        ft.IconButton(
                            "edit", 
                            icon_color="blue", 
                            tooltip="Editar este item",
                            on_click=lambda e, prod=p: self.preencher_form(prod)
                        )
                    ),
                ]
            )
            self.data_table.rows.append(row)
        self.update()

    def preencher_form(self, produto):
        self.tf_nome.value = produto['nome']
        self.tf_valor.value = "" 
        self.dd_campo.value = None
        self.update()

    def editar(self, e):
        nome = self.tf_nome.value
        campo = self.dd_campo.value
        valor = self.tf_valor.value
        
        if not nome or not campo or not valor:
            self.show_snack(e, "Selecione um produto, um campo e digite o valor!", "red")
            return
        
        if campo == 'custo': 
            try: 
                valor = float(valor.replace(',', '.'))
            except ValueError: 
                self.show_snack(e, "O custo deve ser um número!", "red")
                return
            
        self.db.update_product(nome, campo, valor)
        self.update_view()
        self.tf_valor.value=""
        self.show_snack(e, f"Produto '{nome}' atualizado!", "green");self.update()

    def abrir_confirmacao_exclusao(self, e):
        if not self.tf_nome.value:
            self.show_snack(e, "Nenhum produto selecionado para excluir.", "red")
            return
        
        e.page.open(self.bs_confirmar)
        e.page.update()

    def fechar_bottom_sheet(self, e):
        e.page.close(self.bs_confirmar)
        e.page.update()

    def excluir(self, e):
        nome = self.tf_nome.value
        
        self.db.delete_product(nome)
        
        self.fechar_bottom_sheet(e)
        
        self.update_view()
        self.show_snack(e, "Produto excluído com sucesso!", "green")
        
        self.tf_nome.value = ""
        self.tf_valor.value = ""

    def show_snack(self, e, text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        e.page.open(snack)