import flet as ft

class LoginScreen(ft.Container):
    def __init__(self, page, db_manager, on_login_success):
        super().__init__()
        self.page_ref = page 
        self.db = db_manager
        self.on_success = on_login_success
        
        self.alignment = ft.alignment.center
        self.expand = True

        self.user_input = ft.TextField(
            label="Usuário", 
            width=280, 
            prefix_icon="person", 
            border_radius=10
        )
        
        self.pass_input = ft.TextField(
            label="Senha", 
            width=280, 
            password=True, 
            can_reveal_password=True, 
            prefix_icon="lock", 
            border_radius=10,
            on_submit=self.login
        )

        self.content = ft.Card(
            elevation=10,
            color="white",
            content=ft.Container(
                padding=40,
                border_radius=15,
                content=ft.Column(
                    [
                        ft.Image(src="logoexcel.png", width=100, height=100, fit=ft.ImageFit.CONTAIN),
                        ft.Text("CaixaCerto", size=24, weight="bold", color="bluegrey900"),
                        ft.Divider(height=20, color="transparent"),
                        self.user_input,
                        self.pass_input,
                        ft.Divider(height=20, color="transparent"),
                        ft.ElevatedButton(
                            "ENTRAR", 
                            width=280, 
                            height=50, 
                            on_click=self.login,
                            style=ft.ButtonStyle(
                                bgcolor="blue600",
                                color="white",
                                shape=ft.RoundedRectangleBorder(radius=8)
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True
                )
            )
        )

    def login(self, e):
        user = self.user_input.value
        pwd = self.pass_input.value
        
        if not user or not pwd:
            self.show_snack("Preencha todos os campos!", "red")
            return

        success, msg = self.db.authenticate(user, pwd)
        
        if success:
            self.show_snack("Login realizado!", "green")
            self.on_success()
        else:
            self.show_snack(msg, "red")

    def show_snack(self, text, color_name):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color_name)
        self.page_ref.overlay.append(snack)
        snack.open = True
        self.page_ref.update()