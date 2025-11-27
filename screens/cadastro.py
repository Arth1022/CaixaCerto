import flet as ft

class CadastroScreen(ft.Column):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.scroll = ft.ScrollMode.AUTO
        
        self.tipo_selecionado = "pizza"
        self.receita_atual = [] 
        self.cache_ingredientes = {} 

        # Campos
        self.tf_nome = ft.TextField(label="Nome do Produto", expand=True)
        self.tf_custo = ft.TextField(label="Preço de Venda (R$)", width=150, keyboard_type=ft.KeyboardType.NUMBER, on_change=self.recalcular_custos)
        self.tf_desc = ft.TextField(label="Descrição")
        self.tf_pedido = ft.TextField(label="Código/Atalho")

        self.rg_tipo = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="pizza", label="Pizza (Venda)"),
                ft.Radio(value="bebida", label="Bebida (Venda/Estoque)"),
                ft.Radio(value="ingrediente", label="Ingrediente (Matéria Prima)"),
            ]),
            value="pizza",
            on_change=self.mudar_tipo_produto
        )

        self.dd_unidade = ft.Dropdown(
            label="Unidade de Compra",
            options=[
                ft.dropdown.Option("un", "Unidade (un)"),
                ft.dropdown.Option("g", "Gramas (g)"),
                ft.dropdown.Option("kg", "Quilos (kg)"),
                ft.dropdown.Option("ml", "Mililitros (ml)"),
                ft.dropdown.Option("l", "Litros (l)"),
            ],
            value="kg", 
            width=200
        )
        
        self.container_ingrediente = ft.Container(
            visible=False,
            bgcolor="orange50", padding=10, border_radius=10,
            content=ft.Column([
                ft.Text("Configuração de Matéria Prima", weight="bold", color="orange800"),
                self.dd_unidade
            ])
        )

        # Ficha Técnica
        self.dd_ingredientes_db = ft.Dropdown(label="Adicionar Ingrediente", expand=True, dense=True)
        self.tf_qtd_receita = ft.TextField(label="Qtd (g ou un)", width=120, keyboard_type=ft.KeyboardType.NUMBER, dense=True)
        
        self.btn_add_ingrediente = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE, icon_color="green", 
            tooltip="Adicionar", on_click=self.adicionar_ingrediente_receita
        )

        self.lista_receita = ft.ListView(height=120, spacing=5, padding=5)

        # Farol
        self.tf_margem = ft.TextField(label="Margem Desejada (%)", value="100", width=150, on_change=self.recalcular_custos, suffix_text="%")
        self.txt_custo_prod = ft.Text("Custo: R$ 0.00", weight="bold")
        self.txt_sugestao = ft.Text("Sugerido: R$ 0.00", weight="bold")
        self.txt_analise = ft.Text("Aguardando...", italic=True)
        self.icon_farol = ft.Icon(ft.Icons.TRAFFIC, color="grey")

        self.container_farol = ft.Container(
            bgcolor="grey100", padding=15, border_radius=10, border=ft.border.all(1, "grey300"),
            content=ft.Column([
                ft.Text("Análise de Lucro", weight="bold", size=16),
                ft.Row([
                    ft.Column([self.txt_custo_prod, self.txt_sugestao]),
                    ft.Column([self.icon_farol, self.txt_analise], horizontal_alignment="center")
                ], alignment="spaceBetween")
            ])
        )

        self.container_receita = ft.Container(
            visible=True,
            bgcolor="blue50", padding=15, border_radius=10,
            content=ft.Column([
                ft.Text("Ficha Técnica (Receita)", weight="bold", color="blue800"),
                ft.Text("Se for KG/Litro, digite em gramas/ml (Ex: 300)..", size=12, italic=True),
                ft.Row([self.dd_ingredientes_db, self.tf_qtd_receita, self.btn_add_ingrediente]),
                ft.Container(content=self.lista_receita, bgcolor="white", border_radius=5, height=100, border=ft.border.all(1, "grey300")),
                ft.Divider(),
                ft.Row([self.tf_margem], alignment="end"),
                self.container_farol
            ])
        )

        self.btn_salvar = ft.ElevatedButton("Cadastrar Produto", icon=ft.Icons.SAVE, style=ft.ButtonStyle(bgcolor="green", color="white"), height=50, width=200, on_click=self.salvar_produto)

        self.controls = [
            ft.Text("Cadastro de Produtos", size=30, weight="bold"),
            ft.Container(content=self.rg_tipo, bgcolor="grey100", padding=10, border_radius=10),
            self.container_ingrediente, self.container_receita,     
            self.tf_nome, self.tf_custo, self.tf_desc, self.tf_pedido,
            ft.Divider(color="transparent"),
            ft.Row([self.btn_salvar], alignment=ft.MainAxisAlignment.END)
        ]

    def did_mount(self):
        self.carregar_ingredientes()

    def carregar_ingredientes(self):
        todos = self.db.get_all_products(tipos=['ingrediente', 'bebida'])
        self.dd_ingredientes_db.options = []
        self.cache_ingredientes = {}
        for p in todos:
            nome = p['nome']
            self.cache_ingredientes[nome] = {'custo': p.get('custo', 0), 'unidade': p.get('unidade', 'un')}
            self.dd_ingredientes_db.options.append(ft.dropdown.Option(nome))
        self.update()

    def mudar_tipo_produto(self, e):
        tipo = self.rg_tipo.value
        self.tipo_selecionado = tipo
        if tipo == "ingrediente":
            self.container_ingrediente.visible = True; self.container_receita.visible = False
        elif tipo == "pizza":
            self.container_ingrediente.visible = False; self.container_receita.visible = True; self.carregar_ingredientes()
        else:
            self.container_ingrediente.visible = True; self.container_receita.visible = False
        self.update()

    # --- LÓGICA DE CONVERSÃO NA ENTRADA (AQUI MUDOU!) ---
    def adicionar_ingrediente_receita(self, e):
        nome = self.dd_ingredientes_db.value
        qtd_str = self.tf_qtd_receita.value
        
        if not nome or not qtd_str: return
        
        try:
            qtd_digitada = float(qtd_str)
            dados_ing = self.cache_ingredientes.get(nome)
            unidade = dados_ing['unidade'] if dados_ing else 'un'
            
            # SE FOR KG ou LITRO -> Divide por 1000 (100 vira 0.1)
            if unidade in ['kg', 'l']:
                qtd_final = qtd_digitada / 1000.0
                label_visual = f"{qtd_digitada} g ({qtd_final} {unidade})"
            else:
                qtd_final = qtd_digitada
                label_visual = f"{qtd_digitada} {unidade}"

            self.receita_atual.append({"ingrediente": nome, "qtd": qtd_final})
            
            self.lista_receita.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"{nome}", weight="bold", expand=True),
                        ft.Text(label_visual, color="blue"),
                        ft.IconButton(ft.Icons.DELETE, icon_size=18, icon_color="red", on_click=lambda e, n=nome: self.remover_item_receita(e, n))
                    ]),
                    padding=5, bgcolor="grey50", border_radius=5
                )
            )
            
            self.tf_qtd_receita.value = ""
            self.recalcular_custos(None)
            self.update()
        except ValueError:
            self.show_snack("Qtd inválida", "red")

    def remover_item_receita(self, e, nome_item):
        self.receita_atual = [i for i in self.receita_atual if i['ingrediente'] != nome_item]
        self.lista_receita.controls.clear()
        for item in self.receita_atual:
            # Recria visual (simplificado)
            self.lista_receita.controls.append(ft.Container(content=ft.Row([ft.Text(item['ingrediente'], expand=True), ft.Text(f"{item['qtd']}", color="blue"), ft.IconButton(ft.Icons.DELETE, icon_size=18, icon_color="red", on_click=lambda e, n=item['ingrediente']: self.remover_item_receita(e, n))]), padding=5, bgcolor="grey50"))
        self.recalcular_custos(None)
        self.update()

    def recalcular_custos(self, e):
        custo_total = 0.0
        for item in self.receita_atual:
            nome = item['ingrediente']
            qtd = item['qtd'] 
            dados = self.cache_ingredientes.get(nome)
            if dados:
                custo_total += dados['custo'] * qtd

        try:
            margem = float(self.tf_margem.value) if self.tf_margem.value else 0
            preco_atual = float(self.tf_custo.value.replace(',', '.')) if self.tf_custo.value else 0
        except: margem=0; preco_atual=0

        sugerido = custo_total * (1 + (margem/100))
        self.txt_custo_prod.value = f"Custo: R$ {custo_total:.2f}"
        self.txt_sugestao.value = f"Sugerido: R$ {sugerido:.2f}"
        
        if preco_atual == 0: self.container_farol.bgcolor = "grey100"; self.txt_analise.value = "-"
        elif preco_atual >= sugerido: self.container_farol.bgcolor = "green50"; self.txt_analise.value = "Lucro OK ✅"
        elif preco_atual > custo_total: self.container_farol.bgcolor = "yellow50"; self.txt_analise.value = "Margem Baixa ⚠️"
        else: self.container_farol.bgcolor = "red50"; self.txt_analise.value = "PREJUÍZO 🚨"
        self.update()

    def salvar_produto(self, e):
        try:
            if not self.tf_nome.value or not self.tf_custo.value: return
            custo = float(self.tf_custo.value.replace(',', '.'))
            uni = "un" if self.tipo_selecionado == "pizza" else self.dd_unidade.value
            rec = self.receita_atual if self.tipo_selecionado == "pizza" else []
            self.db.register_product(self.tf_nome.value, custo, self.tf_desc.value, self.tf_pedido.value, self.tipo_selecionado, uni, rec)
            self.tf_nome.value=""; self.tf_custo.value=""; self.receita_atual=[]; self.lista_receita.controls.clear();self.tf_desc.value="";self.tf_pedido.value=""
            self.show_snack("Salvo!", "green"); self.update()
        except ValueError: pass

    def show_snack(self, text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        if hasattr(self.page, 'overlay'): self.page.overlay.append(snack)
        else: self.page.snack_bar = snack
        snack.open = True; self.page.update()