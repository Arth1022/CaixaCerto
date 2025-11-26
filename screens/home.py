import flet as ft
from datetime import datetime
from IA import AIManager 

class HomeScreen(ft.Column):
    def __init__(self, db_manager, page: ft.Page):
        super().__init__()
        self.db = db_manager
        self.page_ref = page 
        self.ai = AIManager()
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 10
        
        self.carrinho = [] 
        self.total_produtos = 0.0
        self.total_final = 0.0
        self.date_picked = datetime.now()
        self.txt_date = ft.Text(value=self.date_picked.strftime("%d/%m/%Y"))
        
        self.card_gasto = self._build_stat_card("Gastos", "R$ 0,00", ft.Icons.MONEY_OFF, "red")
        self.card_lucro = self._build_stat_card("Vendas", "R$ 0,00", ft.Icons.ATTACH_MONEY, "green")
        self.card_total = self._build_stat_card("Total", "R$ 0,00", ft.Icons.ACCOUNT_BALANCE_WALLET, "blue")
        
        self.btn_ia = ft.ElevatedButton(
            "Marketing", 
            icon=ft.Icons.AUTO_AWESOME, 
            bgcolor="purple", 
            color="white",
            on_click=self.abrir_analise_ia
        )

        # --- PDV ---
        self.dd_produtos = ft.Dropdown(label="Produto", expand=True, options=[], on_change=self.on_prod_change, dense=True)
        self.tf_custo_display = ft.TextField(label="R$ Unit.", width=80, read_only=True, height=50, content_padding=10, text_size=12)
        self.tf_estoque_display = ft.TextField(label="Est.", width=60, read_only=True, height=50, content_padding=10, text_size=12)
        self.tf_qtd = ft.TextField(label="Qtd", width=60, value="1", keyboard_type=ft.KeyboardType.NUMBER, height=50, content_padding=10)
        
        btn_adicionar = ft.ElevatedButton("Adicionar", icon=ft.Icons.ADD, bgcolor="blue", color="white", on_click=self.adicionar_ao_carrinho, height=50)
        self.btn_meio_a_meio = ft.ElevatedButton("Montar Pizza", icon=ft.Icons.PIE_CHART, bgcolor="orange", color="white", height=50, on_click=self.abrir_painel_meio_a_meio)

        self.tabela_carrinho = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Produto")),
                ft.DataColumn(ft.Text("Qtd"), numeric=True),
                ft.DataColumn(ft.Text("Total"), numeric=True),
                ft.DataColumn(ft.Text("Remover")),
            ],
            rows=[]
        )
        
        # --- DELIVERY ---
        self.sw_delivery = ft.Switch(label="Modo Delivery", value=False, on_change=self.toggle_delivery)
        self.tf_taxa = ft.TextField(label="Taxa Entrega (R$)", value="0", width=150, keyboard_type=ft.KeyboardType.NUMBER, on_change=self.recalcular_total)
        self.dd_motoboy = ft.Dropdown(label="Entregador", expand=True, dense=True)
        self.btn_add_moto = ft.IconButton(icon=ft.Icons.PERSON_ADD, tooltip="Novo Motoboy", on_click=self.abrir_painel_motoboy)

        self.container_delivery = ft.Container(
            visible=False,
            bgcolor="orange50", padding=15, border_radius=10, border=ft.border.all(1, "orange"),
            content=ft.Column([
                ft.Text("Dados da Entrega", weight="bold", color="orange800"),
                ft.Row([self.tf_taxa, self.dd_motoboy, self.btn_add_moto])
            ])
        )

        # --- CLIENTE ---
        self.tf_telefone = ft.TextField(
            label="Cliente CPF/Celular", 
            expand=True, 
            height=40,
            content_padding=10,
            text_size=14,
            keyboard_type=ft.KeyboardType.PHONE, 
            suffix_icon=ft.Icons.SEARCH,
            on_change=self.buscar_cliente_rapido
        )
        
        self.btn_add_cliente = ft.IconButton(
            icon=ft.Icons.PERSON_ADD_ALT_1, 
            icon_color="blue",
            tooltip="Cadastrar Novo Cliente",
            on_click=self.abrir_painel_novo_cliente
        )

        self.txt_nome_cliente = ft.Text("Cliente não identificado", size=12, color="grey")
        self.nome_cliente_cache = "" 

        self.txt_total_pedido = ft.Text("Total Final: R$ 0,00", size=25, weight="bold", color="blue")
        self.dd_pagamento = ft.Dropdown(label="Pagamento", width=200, options=[ft.dropdown.Option("Dinheiro"), ft.dropdown.Option("Pix"), ft.dropdown.Option("Débito"), ft.dropdown.Option("Crédito")], value="Dinheiro", dense=True)
        
        btn_finalizar = ft.ElevatedButton("FINALIZAR VENDA", icon=ft.Icons.CHECK_CIRCLE, bgcolor="green", color="white", height=50, width=200, on_click=self.finalizar_venda)

        pdv_container = ft.Container(
            padding=20, bgcolor="white", border_radius=15, shadow=ft.BoxShadow(blur_radius=5, color="black12"),
            content=ft.Column([
                ft.Row([ft.Text("Novo Pedido", size=20, weight="bold"), self.sw_delivery], alignment="spaceBetween"),
                ft.Row([self.dd_produtos, self.tf_estoque_display, self.tf_custo_display, self.tf_qtd, btn_adicionar]),
                ft.Row([self.btn_meio_a_meio], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Container(content=self.tabela_carrinho, border=ft.border.all(1, "grey200"), border_radius=10, height=150),
                self.container_delivery,
                
                ft.Divider(),
                ft.Row([self.tf_telefone, self.btn_add_cliente]),
                self.txt_nome_cliente,
                
                ft.Row([self.txt_total_pedido], alignment=ft.MainAxisAlignment.END),
                ft.Divider(),
                ft.Row([
                    self.dd_pagamento,
                    ft.ElevatedButton("Data", icon=ft.Icons.CALENDAR_MONTH, on_click=lambda _: self.page_ref.open(self.date_picker)),
                    self.txt_date,
                    btn_finalizar
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ])
        )

        self.date_picker = ft.DatePicker(on_change=self.change_date)
        
        self.chart_pizza = ft.PieChart(
            sections=[], 
            sections_space=1, 
            center_space_radius=60, 
            height=400 
        )
        
        self.controls = [
            ft.Row([ft.Text("Frente de Caixa", size=30, weight="bold"), self.btn_ia], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.card_gasto, self.card_lucro, self.card_total], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
            pdv_container,
            ft.Container(padding=20, content=ft.Column([ft.Text("Top Produtos (Dia)", weight="bold", size=20), self.chart_pizza], horizontal_alignment="center"))
        ]

    # --- LÓGICA VENDA ---
    def finalizar_venda(self, e):
        if not self.carrinho:
            self.show_snack("Carrinho vazio!", "red"); return
        
        taxa_final = 0.0
        entregador_final = ""
        if self.sw_delivery.value:
            try: 
                taxa_final = float(self.tf_taxa.value.replace(',', '.'))
                entregador_final = self.dd_motoboy.value
            except: return

        tem_estoque, msg_estoque = self.db.verificar_estoque_suficiente(self.carrinho)
        if not tem_estoque: self.show_snack(f"{msg_estoque}", "red"); return

        dados_cliente = None
        if self.tf_telefone.value:
            nome_final = self.nome_cliente_cache if self.nome_cliente_cache else "Novo Cliente"
            dados_cliente = {"telefone": self.tf_telefone.value, "nome": nome_final}

        sucesso, msg = self.db.registrar_venda_carrinho(
            itens_carrinho=self.carrinho, 
            pagamento=self.dd_pagamento.value, 
            data_obj=self.date_picked, 
            taxa_entrega=taxa_final, 
            entregador_nome=entregador_final, 
            cliente_dict=dados_cliente 
        )
        
        if sucesso:
            self.carrinho = []; self.sw_delivery.value = False; self.container_delivery.visible = False; self.tf_taxa.value = "0"
            self.tf_telefone.value = ""; self.txt_nome_cliente.value = "Cliente não identificado"; self.nome_cliente_cache = ""
            self.atualizar_tabela_carrinho(); self.update_dashboard(); self.show_snack(msg, "green")
        else:
            self.show_snack(msg, "red")

    # --- OUTROS MÉTODOS ---
    def buscar_cliente_rapido(self, e):
        tel = self.tf_telefone.value
        if len(tel) < 4:
            self.txt_nome_cliente.value = "Cliente não identificado"; self.nome_cliente_cache = ""; self.update(); return
        
        c = self.db.buscar_cliente_pelo_telefone(tel)
        if c:
            self.nome_cliente_cache = c.get('nome', 'Sem Nome')
            self.txt_nome_cliente.value = f"{self.nome_cliente_cache} ({c.get('total_pedidos', 0)} pedidos)"
            self.txt_nome_cliente.color = "green"
        else:
            self.nome_cliente_cache = ""
            self.txt_nome_cliente.value = "Novo Cliente"; self.txt_nome_cliente.color = "blue"
        self.update()

    def abrir_painel_novo_cliente(self, e):
        n = ft.TextField(label="Nome", autofocus=True); t = ft.TextField(label="Tel")
        def ok(e):
            if n.value and t.value:
                self.tf_telefone.value = t.value; self.nome_cliente_cache = n.value
                self.txt_nome_cliente.value = f"{n.value}"; self.txt_nome_cliente.color = "blue"
                self.page_ref.close(bs); self.update()
        bs = ft.BottomSheet(ft.Container(padding=20, height=300, bgcolor="white", content=ft.Column([ft.Text("Novo Cliente"), n, t, ft.ElevatedButton("Confirmar", on_click=ok)])), dismissible=True)
        self.page_ref.open(bs); self.page_ref.update()

    def did_mount(self): self.update_combos(); self.update_dashboard(); self.carregar_motoboys()
    
    def adicionar_ao_carrinho(self, e):
        nome = self.dd_produtos.value
        if not nome: return
        try:
            qtd = int(self.tf_qtd.value); custo = float(self.tf_custo_display.value)
            self.carrinho.append({"nome": nome, "qtd": qtd, "unit": custo, "total": custo * qtd, "is_half": False})
            self.atualizar_tabela_carrinho(); self.tf_qtd.value = "1"; self.dd_produtos.value = None; self.tf_custo_display.value=""; self.tf_estoque_display.value=""; self.update()
        except ValueError: pass

    def remover_item(self, index): del self.carrinho[index]; self.atualizar_tabela_carrinho()

    def atualizar_tabela_carrinho(self):
        self.tabela_carrinho.rows.clear(); self.total_produtos = 0.0
        for i, item in enumerate(self.carrinho):
            self.total_produtos += item['total']
            self.tabela_carrinho.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(item['nome'], width=120)), ft.DataCell(ft.Text(str(item['qtd']))), ft.DataCell(ft.Text(f"R$ {item['total']:.2f}")), ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", on_click=lambda e, idx=i: self.remover_item(idx)))]))

        self.recalcular_total(None)

    def toggle_delivery(self, e): self.container_delivery.visible = self.sw_delivery.value; self.recalcular_total(None); self.update()

    def recalcular_total(self, e): 
        try: taxa = float(self.tf_taxa.value.replace(',', '.')) if self.tf_taxa.value else 0.0
        except: taxa = 0.0
        self.total_final = self.total_produtos + taxa; self.txt_total_pedido.value = f"Total Final: R$ {self.total_final:.2f}"; self.update()

    def abrir_painel_motoboy(self, e):
        nome_field = ft.TextField(label="Nome"); 
        def save(e): 
            if nome_field.value: self.db.add_entregador(nome_field.value); self.page_ref.close(bs); self.carregar_motoboys()
        bs = ft.BottomSheet(ft.Container(content=ft.Column([ft.Text("Novo Motoboy"), nome_field, ft.ElevatedButton("Salvar", on_click=save)]), padding=20, bgcolor="white", height=200), dismissible=True)
        self.page_ref.open(bs); self.page_ref.update()

    def carregar_motoboys(self): self.dd_motoboy.options = [ft.dropdown.Option(m) for m in self.db.get_entregadores()]; self.update()

    def abrir_painel_meio_a_meio(self, e):
        nomes = self.db.get_products_names(['pizza']); op = [ft.dropdown.Option(n) for n in nomes]
        s1 = ft.Dropdown(label="Sabor 1", options=op, expand=True); s2 = ft.Dropdown(label="Sabor 2", options=op, expand=True); bo = ft.TextField(label="Borda R$", width=100, value="0")
        def confirm(e):
            if not s1.value or not s2.value: return
            p1,_,_ = self.db.get_product_details(s1.value); p2,_,_ = self.db.get_product_details(s2.value)
            total = max(p1, p2) + float(bo.value or 0)
            self.carrinho.append({"nome": f"1/2 {s1.value} + 1/2 {s2.value}", "qtd": 1, "total": total, "is_half": True, "sabor1": s1.value, "sabor2": s2.value})
            self.page_ref.close(bs); self.atualizar_tabela_carrinho()
        bs = ft.BottomSheet(ft.Container(content=ft.Column([ft.Text("2 Sabores"), ft.Row([s1, s2]), bo, ft.ElevatedButton("Add", on_click=confirm)]), padding=20, height=350, bgcolor="white"), dismissible=True)
        self.page_ref.open(bs); self.page_ref.update()

    def abrir_analise_ia(self, e):
        # --- 1. MOSTRA O LOADING ---
        bs_loading = ft.BottomSheet(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Divider(height=10, color="transparent"),
                    ft.Text("A IA está analisando sua pizzaria...", weight="bold", color="black"),
                    ft.Text("Gerando estratégias de venda...", size=12, color="grey")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                padding=30, 
                height=200, 
                bgcolor="white",
                border_radius=20,
                alignment=ft.alignment.center
            ),
            dismissible=False
        )
        self.page_ref.open(bs_loading)
        self.page_ref.update()

        # --- 2. PROCESSAMENTO ---
        try:
            resp = self.ai.analisar_dados(self.db.get_daily_sales_text(), contexto="home")
            
            self.page_ref.close(bs_loading)

            res_bs = ft.BottomSheet(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                [
                                    ft.Text("Estratégia da IA", weight="bold", size=20, color="black"),
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
            self.page_ref.open(res_bs)
            self.page_ref.update()

        except Exception as ex:
            self.page_ref.close(bs_loading)
            print(f"Erro IA: {ex}")
            
            if hasattr(self, 'show_snack'):
                self.show_snack(f"Erro ao consultar IA: {ex}", "red")
            else:
                self.page_ref.snack_bar = ft.SnackBar(content=ft.Text(f"Erro: {ex}"), bgcolor="red")
                self.page_ref.snack_bar.open = True
                self.page_ref.update()
    def update_dashboard(self):
        hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0); dados = self.db.get_financial_data(start_date=hoje)
        
        l = sum(d.get('valor_liquido',0) for d in dados if d.get('valor_liquido',0)>=0); g = sum(d.get('valor_liquido',0) for d in dados if d.get('valor_liquido',0)<0)
        
        self.card_gasto.content.controls[1].value = f"R$ {g:.2f}"; self.card_lucro.content.controls[1].value = f"R$ {l:.2f}"; self.card_total.content.controls[1].value = f"R$ {l+g:.2f}"
        
        top = self.db.get_top_products(); clr = ["blue", "orange", "purple", "green", "red"]
        
        if not top: self.chart_pizza.sections = [ft.PieChartSection(1, title="Vazio", color="grey", radius=40)]
        
        else: self.chart_pizza.sections = [ft.PieChartSection(i['total_qtd'], title=f"{i['_id']}\n({i['total_qtd']})", color=clr[idx%5], radius=100, title_style=ft.TextStyle(size=12, color="white", weight="bold")) for idx, i in enumerate(top)]
        
        self.update()
   
    def update_combos(self): self.dd_produtos.options = [ft.dropdown.Option(n) for n in self.db.get_products_names(['pizza', 'bebida'])]; self.update()
    
    def on_prod_change(self, e): c,e_q,t = self.db.get_product_details(self.dd_produtos.value); self.tf_custo_display.value=str(c); self.tf_estoque_display.value = "-" if t=='pizza' else str(e_q); self.update()
    
    def change_date(self, e):
        data_apenas = self.date_picker.value.date()
        
        hora_atual = datetime.now().time()
        
        self.date_picked = datetime.combine(data_apenas, hora_atual)
        
        self.txt_date.value = self.date_picked.strftime("%d/%m/%Y %H:%M")
        self.update()
            
    def show_snack(self, t, c): self.page_ref.open(ft.SnackBar(ft.Text(t), bgcolor=c)); self.page_ref.update()
   
    def _build_stat_card(self, t, v, i, c): return ft.Container(content=ft.Column([ft.Row([ft.Icon(i, color="white", size=30), ft.Text(t, color="white", weight="bold", size=18)]), ft.Text(v, size=24, color="white", weight="bold")]), bgcolor=c, padding=20, border_radius=15, width=300, height=120, shadow=ft.BoxShadow(blur_radius=5, color="black26"))