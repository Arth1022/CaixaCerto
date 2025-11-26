import flet as ft

class ConfiguracoesScreen(ft.Column):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20
        
     
        self.tf_debito = ft.TextField(label="Taxa Débito (%)", width=150, keyboard_type=ft.KeyboardType.NUMBER, suffix_text="%")
        self.tf_credito = ft.TextField(label="Taxa Crédito (%)", width=150, keyboard_type=ft.KeyboardType.NUMBER, suffix_text="%")
        self.tf_pix = ft.TextField(label="Taxa Pix (%)", width=150, keyboard_type=ft.KeyboardType.NUMBER, suffix_text="%")
        
        self.btn_salvar = ft.ElevatedButton(
            "Salvar Configurações", 
            icon=ft.Icons.SAVE, 
            bgcolor="blue", 
            color="white", 
            height=50,
            on_click=self.salvar_taxas
        )

        self.controls = [
            ft.Text("Configurações do Sistema", size=30, weight="bold"),
            ft.Divider(),
            
            ft.Container(
                padding=20, bgcolor="white", border_radius=10, shadow=ft.BoxShadow(blur_radius=5, color="black12"),
                content=ft.Column([
                    ft.Text("Taxas das Maquininhas", size=20, weight="bold", color="blue"),
                    ft.Text("Defina a porcentagem que a operadora cobra. O sistema calculará o lucro líquido automaticamente.", color="grey"),
                    ft.Divider(),
                    ft.Row([self.tf_debito, self.tf_credito, self.tf_pix]),
                    ft.Divider(height=20, color="transparent"),
                    ft.Row([self.btn_salvar], alignment=ft.MainAxisAlignment.END)
                ])
            )
        ]

    def did_mount(self):
        self.carregar_taxas()

    def carregar_taxas(self):
        taxas = self.db.get_taxas_pagamento()
        self.tf_debito.value = str(taxas.get('debito', 0))
        self.tf_credito.value = str(taxas.get('credito', 0))
        self.tf_pix.value = str(taxas.get('pix', 0))
        self.update()

    def salvar_taxas(self, e):
        try:
            deb = float(self.tf_debito.value.replace(',', '.'))
            cred = float(self.tf_credito.value.replace(',', '.'))
            pix = float(self.tf_pix.value.replace(',', '.'))
            
            sucesso = self.db.set_taxas_pagamento(deb, cred, pix)
            if sucesso:
                self.show_snack("Taxas atualizadas com sucesso!", "green")
            else:
                self.show_snack("Erro ao salvar.", "red")
        except ValueError:
            self.show_snack("Digite apenas números válidos.", "red")

    def show_snack(self, text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        if hasattr(self.page, 'overlay'): self.page.overlay.append(snack)
        else: self.page.snack_bar = snack
        snack.open = True
        self.page.update()