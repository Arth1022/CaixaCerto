import flet as ft
import threading
import time

class CozinhaScreen(ft.Column):
    def __init__(self, db_manager, page: ft.Page):
        super().__init__()
        self.db = db_manager
        self.page_ref = page
        self.expand = True 
        self.running = True 
        
      
        self.grid_pedidos = ft.GridView(
            expand=True,
            runs_count=5, 
            max_extent=300, 
            child_aspect_ratio=0.8, 
            spacing=10,
            run_spacing=10,
        )

        self.controls = [
            ft.Row([
                ft.Icon(ft.Icons.KITCHEN, size=40, color="orange"),
                ft.Text("KDS - Monitor de Cozinha", size=30, weight="bold"),
                ft.Container(content=ft.Text("Atualização Automática 🟢", color="green", size=12), padding=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Container(content=self.grid_pedidos, expand=True)
        ]

    def did_mount(self):
        self.running = True
        self.atualizar_kds()
        threading.Thread(target=self.loop_atualizacao, daemon=True).start()

    def will_unmount(self):
        self.running = False

    def loop_atualizacao(self):
        while self.running:
            time.sleep(5) 
            try:
                self.atualizar_kds()
            except:
                pass

    def atualizar_kds(self):
        pedidos = self.db.get_kds_orders()
        self.grid_pedidos.controls.clear()
        
        if not pedidos:
            self.grid_pedidos.controls.append(
                ft.Text("Cozinha Livre!", size=30, color="grey", text_align="center")
            )
        else:
            for p in pedidos:
                self.criar_card_pedido(p)
        
        self.update()

    def criar_card_pedido(self, p):
        status = p.get('status_cozinha', 'Pendente')
        p_id = p.get('pedido_id')
        hora = p.get('d_obj').strftime("%H:%M") if p.get('d_obj') else "--:--"
        itens = p.get('resumo_itens', [])
        
        cor_fundo = "white"
        cor_status = "red"
        texto_botao = "INICIAR"
        
        if status == 'Pendente':
            cor_fundo = "red50"
            cor_status = "red"
            texto_botao = "PREPARAR"
        elif status == 'Preparando':
            cor_fundo = "orange50"
            cor_status = "orange"
            texto_botao = "PRONTO"
        elif status == 'Pronto':
            cor_fundo = "green50"
            cor_status = "green"
            texto_botao = "ENTREGUE"

        lista_visual = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO, height=150)
        for item in itens:
            lista_visual.controls.append(
                ft.Text(f"• {item}", size=16, weight="bold", color="black87")
            )

        card = ft.Container(
            bgcolor=cor_fundo,
            border=ft.border.all(2, cor_status),
            border_radius=10,
            padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Text(f"#{str(p_id)[-4:]}", weight="bold", size=20), 
                    ft.Text(hora, size=16, weight="bold")
                ], alignment="spaceBetween"),
                
                ft.Divider(height=1, color=cor_status),
                
                ft.Container(
                    bgcolor=cor_status, padding=5, border_radius=5,
                    content=ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, size=10, color="white"),
                        ft.Text(status.upper(), color="white", weight="bold")
                    ], alignment="center")
                ),
                
                lista_visual,
                
                ft.ElevatedButton(
                    texto_botao, 
                    bgcolor=cor_status, 
                    color="white", 
                    width=float("inf"),
                    height=50,
                    on_click=lambda e, pid=p_id: self.acao_avancar(pid)
                )
            ])
        )
        self.grid_pedidos.controls.append(card)

    def acao_avancar(self, pedido_id):
        self.db.avancar_status_kds(pedido_id)
        self.atualizar_kds() 