import flet as ft
from datetime import datetime
import pandas as pd
from IA import AIManager

class RelatorioScreen(ft.Column):
    def __init__(self, db_manager, page: ft.Page): 
        super().__init__()
        self.db = db_manager
        self.page_ref = page 
        self.ai = AIManager()
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20
        
        hoje = datetime.now()
        self.mes_selecionado = hoje.month
        self.ano_selecionado = hoje.year
        self.apenas_vendas = False

        meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                       "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        
        self.dd_mes = ft.Dropdown(
            width=150, label="Mês", value=str(self.mes_selecionado),
            options=[ft.dropdown.Option(str(i+1), m) for i, m in enumerate(meses_nomes)], dense=True
        )
        
        self.dd_ano = ft.Dropdown(
            width=100, label="Ano", value=str(self.ano_selecionado),
            options=[ft.dropdown.Option(str(y)) for y in range(2023, 2030)], dense=True
        )
        
        self.sw_vendas = ft.Switch(label="Ocultar Despesas", value=False, on_change=self.aplicar_filtro)

        self.btn_ia = ft.ElevatedButton(
            "Consultor Financeiro", 
            icon=ft.Icons.AUTO_AWESOME, 
            bgcolor="purple", 
            color="white", 
            on_click=self.abrir_analise_ia
        )

        filtros_row = ft.Container(
            padding=15, bgcolor="white", border_radius=10, shadow=ft.BoxShadow(blur_radius=5, color="black12"),
            content=ft.Column([
                ft.Row([
                    self.dd_mes, self.dd_ano, 
                    ft.ElevatedButton("Filtrar", icon=ft.Icons.FILTER_LIST, on_click=self.aplicar_filtro),
                    ft.IconButton(ft.Icons.FILE_DOWNLOAD, tooltip="Excel", on_click=self.gerar_excel)
                ]),
                ft.Row([self.sw_vendas, self.btn_ia], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ])
        )

        self.chart_container = ft.Container(
            content=ft.Text("Carregando..."),
            padding=10, bgcolor="white", border_radius=10, shadow=ft.BoxShadow(blur_radius=5, color="black12"),
            margin=ft.margin.only(bottom=20, top=20),
            height=500 
        )

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Data")),
                ft.DataColumn(ft.Text("Descrição")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Pagamento")),
                ft.DataColumn(ft.Text("Valor"), numeric=True),
            ],
            rows=[]
        )

        self.controls = [
            ft.Text("Relatório Financeiro", size=30, weight="bold"),
            filtros_row,
            self.chart_container,
            ft.Text("Extrato Detalhado", weight="bold", size=16),
            ft.Container(
                content=self.data_table,
                border=ft.border.all(1, "grey300"),
                border_radius=10,
                padding=10
            )
        ]

    def did_mount(self):
        self.aplicar_filtro(None)

    def abrir_analise_ia(self, e):
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
        self.page_ref.open(bs_loading)
        self.page_ref.update()

        try:
            mes = int(self.dd_mes.value)
            ano = int(self.dd_ano.value)
            resumo_texto = self.db.get_monthly_summary_text(mes, ano)
            
            resp = self.ai.analisar_dados(resumo_texto, contexto="financeiro")

            self.page_ref.close(bs_loading)

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
            self.page_ref.open(res_bs)
            self.page_ref.update()

        except Exception as ex:
            self.page_ref.close(bs_loading)
            self.show_snack(f"Erro na IA: {ex}", "red")

    def aplicar_filtro(self, e):
        try:
            mes = int(self.dd_mes.value)
            ano = int(self.dd_ano.value)
            ocultar_gastos = self.sw_vendas.value
            
            dados_brutos = self.db.get_financial_data_by_month(mes, ano)
            
            dados_filtrados = []
            for item in dados_brutos:
                tipo = item.get('tipo', 'venda')
                if ocultar_gastos and (tipo == 'reposicao' or tipo == 'despesa' or tipo == 'perda'): continue 
                dados_filtrados.append(item)

            self.popular_tabela(dados_filtrados)
            self.atualizar_grafico_plotly(dados_filtrados)
            self.update()
        except Exception as ex: print(f"Erro filtro: {ex}")

    def popular_tabela(self, dados):
        self.data_table.rows.clear()
        dados_sorted = sorted(dados, key=lambda x: x.get('d_obj', ''), reverse=True)

        for item in dados_sorted:
            valor = item.get('cust', 0)
            tipo = item.get('tipo', 'venda')
            pag = item.get('pagamento', '-')
            nome = item.get('nome', '')
            
            cor_valor = "green" if valor >= 0 else "red"
            
            label_tipo = "Venda"
            if tipo == 'reposicao': label_tipo = "Compra Estoque"
            elif tipo == 'despesa': label_tipo = "Despesa Fixa"
            elif tipo == 'perda': label_tipo = "Perda/Quebra"
            
            self.data_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item.get('data', ''))),
                    ft.DataCell(ft.Text(nome, width=200, no_wrap=True, tooltip=nome)),
                    ft.DataCell(ft.Text(label_tipo)),
                    ft.DataCell(ft.Text(pag)),
                    ft.DataCell(ft.Text(f"R$ {valor:.2f}", color=cor_valor, weight="bold")),
                ])
            )

    def atualizar_grafico_plotly(self, dados):
        dias_agrupados = {}
        for item in dados:
            dia_str = item.get('data', '')
            if not dia_str: continue
            val = item.get('cust', 0)
            dias_agrupados[dia_str] = dias_agrupados.get(dia_str, 0) + val

        try:
            datas_ordenadas = sorted(dias_agrupados.keys(), key=lambda x: datetime.strptime(x, "%d/%m/%Y"))
        except:
            datas_ordenadas = sorted(dias_agrupados.keys()) 

        valores = [dias_agrupados[d] for d in datas_ordenadas]
        if not valores:
            valores = [0]
            
        max_val = max(valores)
        min_val = min(valores)
        
       
        max_y = max_val * 1.2 if max_val > 0 else 100
        min_y = min_val * 1.2 if min_val < 0 else 0

        chart_groups = []
        x_labels = []

        for i, dia in enumerate(datas_ordenadas):
            valor = dias_agrupados[dia]
            cor = ft.Colors.BLUE if valor >= 0 else ft.Colors.RED
            
            chart_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=valor,
                            width=30, 
                            color=cor,
                            tooltip=f"{dia}\nR$ {valor:.2f}",
                            border_radius=4
                        )
                    ]
                )
            )
            
            try:
                dt_obj = datetime.strptime(dia, "%d/%m/%Y")
                label_text = f"{dt_obj.day:02d}/{dt_obj.month:02d}"
            except:
                label_text = dia

            x_labels.append(
                ft.ChartAxisLabel(
                    value=i,
                    label=ft.Text(label_text, size=12, weight="bold") 
                )
            )

        chart = ft.BarChart(
            bar_groups=chart_groups,
            bottom_axis=ft.ChartAxis(
                labels=x_labels,
                labels_size=50, 
            ),
            left_axis=ft.ChartAxis(
                labels_size=50, 
                title=ft.Text("Valor (R$)", size=12, weight="bold")
            ),
            min_y=min_y, 
            max_y=max_y, 
            border=ft.border.all(1, ft.Colors.GREY_200),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.Colors.GREY_100, width=1, dash_pattern=[3, 3]
            ),
            tooltip_bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.BLACK),
            interactive=True,
            expand=True
        )

        self.chart_container.content = chart
        self.chart_container.update()

    def gerar_excel(self, e):
        try:
            mes = int(self.dd_mes.value)
            ano = int(self.dd_ano.value)
        except:
            self.show_snack("Selecione um mês e ano válidos.", "red")
            return

        dados_brutos = self.db.get_financial_data_by_month(mes, ano)
        
        if not dados_brutos:
            self.show_snack("Nenhum dado encontrado para este período.", "orange")
            return

        try:
            df = pd.DataFrame(dados_brutos)
            
            mapeamento_colunas = {
                'data': 'Data',
                'nome': 'Nome',
                'cust': 'Valor da Venda',
                'quantidade': 'Quantidade'
            }
            df.rename(columns=mapeamento_colunas, inplace=True)

            colunas_finais = ['Data', 'Nome', 'Valor da Venda', 'Quantidade']
            for col in colunas_finais:
                if col not in df.columns:
                    df[col] = 0 if col in ['Valor da Venda', 'Quantidade'] else ''

            df_final = df[colunas_finais]
            total_vendas = df_final['Valor da Venda'].sum()
            
            nome_arquivo = f'Relatorio_Financeiro_{mes}_{ano}.xlsx'

            with pd.ExcelWriter(nome_arquivo, engine='xlsxwriter') as writer:
                workbook = writer.book
                worksheet = workbook.add_worksheet('Relatório')

                formato_titulo = workbook.add_format({'bold': True, 'font_size': 18, 'font_color': 'white', 'bg_color': '#2F5496', 'align': 'center', 'valign': 'vcenter'})
                formato_subtitulo = workbook.add_format({'bold': True, 'font_size': 11, 'bg_color': '#BDD7EE', 'align': 'center', 'valign': 'vcenter'})
                formato_input = workbook.add_format({'bg_color': '#FFFFCC', 'border': 1})
                formato_total_label = workbook.add_format({'bold': True, 'font_size': 11, 'bg_color': '#BDD7EE', 'border': 1})
                formato_total_valor = workbook.add_format({'bold': True, 'font_size': 11, 'bg_color': '#BDD7EE', 'border': 1, 'num_format': 'R$ #,##0.00'})
                formato_painel_lateral = workbook.add_format({'bg_color': "#FFFFFF"})
                formato_data = workbook.add_format({'num_format': 'dd/mm/yyyy', 'align': 'left'})
                formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})
                formato_quantidade = workbook.add_format({'align': 'center'})

                worksheet.set_column('A:B', 0, formato_painel_lateral)
                
                try:
                    worksheet.insert_image('A1', 'logoexcel.png', {'x_scale': 0.5, 'y_scale': 0.5, 'x_offset': 10, 'y_offset': 10})
                except:
                    pass 

                worksheet.merge_range('C2:H3', 'CONTROLE DE VENDAS CAIXA CERTO', formato_titulo)
                worksheet.merge_range('C4:H4', f'Relatório Mensal - {mes}/{ano}', formato_subtitulo)
                
                (num_rows, num_cols) = df_final.shape
                headers = [{'header': col} for col in df_final.columns]
                
                if num_rows > 0:
                    worksheet.add_table(10, 2, 10 + num_rows, 2 + num_cols - 1, {
                        'data': df_final.values.tolist(),
                        'columns': headers,
                        'style': 'Table Style Medium 9',
                    })
                else:
                    worksheet.merge_range(10, 2, 10, 2 + num_cols - 1, 'Nenhum dado encontrado', formato_input)

                linha_inicio_totais = 10 + num_rows + 2
                worksheet.write(f'D{linha_inicio_totais}', 'Total de Vendas:', formato_total_label)
                worksheet.write(f'E{linha_inicio_totais}', total_vendas, formato_total_valor) 
                
                worksheet.set_column('C:C', 15, formato_data) 
                worksheet.set_column('D:D', 35) 
                worksheet.set_column('E:E', 18, formato_moeda)
                worksheet.set_column('F:F', 12, formato_quantidade)
                worksheet.hide_gridlines(2)

            self.show_snack(f"Sucesso! Salvo em: {nome_arquivo}", "green")

        except Exception as ex:
            print(ex)
            self.show_snack(f"Erro ao gerar Excel: {ex}", "red")

    def show_snack(self, text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color, show_close_icon=True)
        self.page_ref.open(snack)
        self.page_ref.update()