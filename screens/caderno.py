import flet as ft
from datetime import datetime

class CadernoScreen(ft.Column):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20
        
        self.container_principal = ft.Container()
        self.tabela_historico = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Data")),
                ft.DataColumn(ft.Text("Funcionário")),
                ft.DataColumn(ft.Text("Inicial")),
                ft.DataColumn(ft.Text("Final (Real)")),
                ft.DataColumn(ft.Text("Diferença")),
            ],
            rows=[]
        )

        self.controls = [
          
            self.container_principal,
            ft.Divider(),
            ft.Text("Histórico de Fechamentos", size=20, weight="bold"),
            ft.Container(
                content=self.tabela_historico,
                border=ft.border.all(1, "grey300"),
                border_radius=10,
                padding=10
            )
        ]

    def did_mount(self):
        self.update_ui()

    def update_ui(self):
        turno_aberto = self.db.get_status_caixa()
        self.carregar_historico()

        if turno_aberto:
            self.mostrar_caixa_aberto(turno_aberto)
        else:
            self.mostrar_caixa_fechado()
        self.update()

    def mostrar_caixa_fechado(self):
        self.tf_fundo = ft.TextField(
            label="Fundo de Troco (Dinheiro na Gaveta)", 
            value="0", 
            width=250, 
            keyboard_type=ft.KeyboardType.NUMBER,
            text_size=16,
            prefix_text="R$ "
        )
        
        self.container_principal.content = ft.Container(
            bgcolor="grey100", padding=40, border_radius=10,
            content=ft.Column([
                ft.Icon(ft.Icons.LOCK, size=60, color="grey"),
                ft.Text("O Caixa está FECHADO", size=24, weight="bold", color="grey"),
                ft.Text("Conte o dinheiro que está na gaveta para iniciar o turno.", size=16),
                ft.Divider(height=20, color="transparent"),
                ft.Row([
                    self.tf_fundo, 
                    ft.ElevatedButton(
                        "ABRIR CAIXA", 
                        bgcolor="green", 
                        color="white", 
                        height=50, 
                        icon=ft.Icons.LOCK_OPEN,
                        on_click=self.acao_abrir
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def acao_abrir(self, e):
        try:
            valor = float(self.tf_fundo.value.replace(',', '.'))
            sucesso, msg = self.db.abrir_caixa(valor, datetime.now())
            if sucesso:
                self.show_snack(msg, "green")
                self.update_ui()
            else:
                self.show_snack(msg, "red")
        except ValueError:
            self.show_snack("Valor inválido.", "red")

    def mostrar_caixa_aberto(self, turno):
        saldo_atual = self.db.calcular_saldo_atual()
        data_abertura = turno['abertura'].strftime("%H:%M")
        
        self.tf_valor_mov = ft.TextField(label="Valor", width=100, prefix_text="R$ ", keyboard_type=ft.KeyboardType.NUMBER)
        self.tf_desc_mov = ft.TextField(label="Motivo (ex: Gelo, Troco)", expand=True)
        self.tf_fechamento = ft.TextField(
            label="Valor Total Contado (Dinheiro)", 
            width=250, 
            prefix_text="R$ ",
            text_style=ft.TextStyle(size=18, weight="bold")
        )

        self.container_principal.content = ft.Column([
            ft.Container(
                bgcolor="green50", padding=20, border_radius=10, border=ft.border.all(1, "green"),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="green"),
                        ft.Text(f"Caixa ABERTO desde as {data_abertura}", color="green", weight="bold"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(),
                    
                    ft.Text("Saldo Estimado (Dinheiro na Gaveta):", size=14),
                    ft.Row([
                        ft.Text(f"R$ {saldo_atual:.2f}", size=35, weight="bold", color="black"),
                    ]),
                    ft.Text("* Atenção: Vendas no Pix/Cartão não somam aqui.", size=12, italic=True, color="red")
                ])
            ),
            
            ft.Container(
                margin=ft.margin.only(top=20), padding=20, bgcolor="white", border_radius=10, shadow=ft.BoxShadow(blur_radius=5, color="black12"),
                content=ft.Column([
                    ft.Text("Movimentação de Gaveta", weight="bold", size=16),
                    ft.Row([self.tf_valor_mov, self.tf_desc_mov]),
                    ft.Row([
                        ft.ElevatedButton("Sangria (Retirar -)", icon=ft.Icons.REMOVE, bgcolor="red", color="white", on_click=lambda e: self.acao_movimentar("sangria")),
                        ft.ElevatedButton("Suprimento (Adicionar +)", icon=ft.Icons.ADD, bgcolor="blue", color="white", on_click=lambda e: self.acao_movimentar("suprimento"))
                    ], alignment=ft.MainAxisAlignment.END)
                ])
            ),

            ft.Container(
                margin=ft.margin.only(top=20), padding=20, bgcolor="red50", border_radius=10, border=ft.border.all(1, "red"),
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.WARNING, color="red"), ft.Text("Encerrar Turno", weight="bold", color="red", size=16)]),
                    ft.Text("Conte o dinheiro físico e digite abaixo."),
                    ft.Row([
                        self.tf_fechamento,
                        ft.ElevatedButton("FECHAR CAIXA", icon=ft.Icons.LOCK, bgcolor="red", color="white", height=50, on_click=self.acao_fechar)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ])
            )
        ])

    def acao_movimentar(self, tipo):
        try:
            val = float(self.tf_valor_mov.value.replace(',', '.'))
            desc = self.tf_desc_mov.value
            if not desc: 
                self.show_snack("Digite um motivo.", "red")
                return
            
            sucesso, msg = self.db.registrar_movimentacao_caixa(tipo, val, desc, datetime.now())
            if sucesso:
                self.show_snack(msg, "green")
                self.tf_valor_mov.value = ""
                self.tf_desc_mov.value = ""
                self.update_ui()
        except ValueError:
            self.show_snack("Valor inválido.", "red")

    def acao_fechar(self, e):
        try:
            val_real = float(self.tf_fechamento.value.replace(',', '.'))
            sucesso, msg = self.db.fechar_caixa(val_real, datetime.now())
            if sucesso:
                cor = "green" if "SUCESSO" in msg else ("blue" if "SOBRA" in msg else "red")
                self.show_snack(msg, cor)
                self.update_ui()
        except ValueError:
            self.show_snack("Valor inválido.", "red")

    def carregar_historico(self):
        historico = self.db.get_historico_caixa()
        self.tabela_historico.rows.clear()
        for h in historico:
            data = h['fechamento'].strftime("%d/%m %H:%M") if h.get('fechamento') else "Erro"
            user = h['funcionario'] if h.get('funcionario') else "Desconhecido"
            inicial = h.get('saldo_inicial', 0)
            final_real = h.get('saldo_final_real', 0)
            diferenca = h.get('diferenca', 0)
            
            cor_dif = "green"
            if diferenca < -0.5: cor_dif = "red"
            elif diferenca > 0.5: cor_dif = "blue"
            
            self.tabela_historico.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(data)),
                    ft.DataCell(ft.Text(user)),
                    ft.DataCell(ft.Text(f"R$ {inicial:.2f}")),
                    ft.DataCell(ft.Text(f"R$ {final_real:.2f}")),
                    ft.DataCell(ft.Text(f"R$ {diferenca:.2f}", color=cor_dif, weight="bold")),
                ])
            )

    def show_snack(self, text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        self.page.open(snack)
        self.page.update()