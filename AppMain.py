import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from pymongo import MongoClient
from datetime import datetime, timedelta, date
from tkinter import messagebox
from tkcalendar import DateEntry
import pandas as pd #pip install pandas xlsxwriter

con = MongoClient('mongodb+srv://arth1022:H&soyam01@caixacerto.c4y3jgg.mongodb.net/')
db = con.get_database("pizzaria")
colecao = db.get_collection("produtos")
money = db.get_collection("gastos/lucros")

class HomeFrame(ttk.Frame):
    def __init__(self, master, relatorio_frame, produtos_frame, **kwargs):
        super().__init__(master, **kwargs)

        self.relatorio_frame = relatorio_frame
        self.produtos_frame = produtos_frame
        
        self.gasto_var = tk.StringVar()
        self.lucro_var = tk.StringVar()
        self.total_var = tk.StringVar()

        self.data_auto_var_home = tk.BooleanVar(value=True)

        text_frame = ttk.Frame(self)
        text_frame.grid(row=0, column=0, sticky="we", padx=20, pady=20)
        relatorio_frame2 = ttk.Frame(self)
        relatorio_frame2.grid(row=2,column=0,sticky='w')
        add_box = ttk.LabelFrame(self,text='Adicionar Venda/Compra',padding=10)
        add_box.grid(row=1, column=0, pady=2, sticky='w')
        self.calcula()

        add_box.columnconfigure(0,weight=1)
        add_box.columnconfigure(1,weight=1)

        ttk.Label(text_frame, text="Seja Bem-vindo ao Sistema!", font=('Arial', 18, 'bold')).grid(row=0,column=0)
        
        ttk.Label(add_box, text='Nome do Produto:').grid(row=0, column=0, sticky='w')
        self.entry_nproduto = ttk.Entry(add_box, width=14)
        self.entry_nproduto.grid(row=0,column=1, sticky='ew')
        
        ttk.Label(add_box,text="Quantidade:"). grid(row=1, column=0, sticky='w')
        self.entry_qtd = ttk.Entry(add_box,width=14)
        self.entry_qtd.grid(row=1, column=1, sticky='ew')
        
        ttk.Label(add_box, text='Data:').grid(row=2, column=0, sticky='w')
        self.entry_data = DateEntry(add_box, 
                                    width=12, 
                                    date_pattern='dd/MM/yyyy', 
                                    locale='pt_BR')
        self.entry_data.grid(row=2, column=1, sticky='ew')

        self.check_data_auto = ttk.Checkbutton(add_box, 
                                                text='Data Automática', 
                                                variable=self.data_auto_var_home,
                                                command=self.toggle_date_entry)
        self.check_data_auto.grid(row=3, column=0, columnspan=2, sticky='w', pady=5)
        
        self.toggle_date_entry()

        ttk.Button(add_box, text='Confirmar', style='Green.TButton', command=self.getmoney,cursor='hand2').grid(row=4, column=1, pady=5, sticky='e')

        ttk.Label(text_frame, text="Resumo Semanal:", font=('Arial', 14, 'bold')).grid(row=1,column=0)
        
        custo_frame = ttk.LabelFrame(relatorio_frame2,text='')
        custo_frame.grid(row=0,column=0)
        ttk.Label(custo_frame,text='Gastos:',font=('Arial',12,'bold')).grid(row=0,column=0,pady=2)
        ttk.Label(custo_frame,textvariable=self.gasto_var,font=('Arial',12,'bold')).grid(row=0,column=1,pady=2)
        
        lucros_frame = ttk.LabelFrame(relatorio_frame2,text='')
        lucros_frame.grid(row=1,column=0)
        ttk.Label(lucros_frame,text='Vendas:',font=('Arial',12,'bold')).grid(row=0,column=0,pady=2)
        ttk.Label(lucros_frame,textvariable=self.lucro_var,font=('Arial',12,'bold')).grid(row=0,column=1,pady=2)

        total_frame = ttk.LabelFrame(relatorio_frame2,text='')
        total_frame.grid(row=2 ,column=0)
        ttk.Label(total_frame,text='Total:',font=('Arial',12,'bold',),foreground='Blue').grid(row=0,column=0,pady=2)
        ttk.Label(total_frame,textvariable=self.total_var,font=('Arial',12,'bold',),foreground='Blue').grid(row=0,column=2,pady=2)


    def toggle_date_entry(self):
        if self.data_auto_var_home.get():
            self.entry_data.config(state='disabled')
        else:
            self.entry_data.config(state='normal')

    def getmoney(self):
        self.data_auto_var_home.get()
        nomeadd = self.entry_nproduto.get()
        qtd = self.entry_qtd.get()
        qtd = int(qtd)
        produto = colecao.find_one({'nome': nomeadd})
        gasto = produto['custo']
        nome = produto['nome']
        
        data_para_salvar = None
        
        if self.data_auto_var_home.get() == True:
            data_para_salvar = datetime.now()
        else:
            data_obj_date = self.entry_data.get_date()
            data_para_salvar = datetime.combine(data_obj_date, datetime.min.time())

        data_str = data_para_salvar.strftime("%d/%m/%Y")

        insert = {
            'nome' : nome,
            '$': gasto * qtd,
            'data': data_str,
            'd_obj': data_para_salvar,
            'quantidade' : qtd,
        }
        money.insert_one(insert)
        self.calcula()
        self.entry_nproduto.delete(0, tk.END)
        self.entry_qtd.delete(0,tk.END)
        self.relatorio_frame.atualiza()

    def calcula(self):
        data_hoje_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        data_amanha_inicio = data_hoje_inicio + timedelta(days=1)
        f = {'d_obj': {'$gte': data_hoje_inicio, '$lt': data_amanha_inicio}}
        filtro = list(money.find(f))
        total = 0
        lucro = 0
        gasto = 0
        for i in filtro:
            valor = i.get('$')
            total += valor
            if valor < 0:
                gasto += valor
            else:
                lucro += valor
        self.int_lucro = lucro
        self.int_gasto = gasto
        self.int_total = total

        self.gasto_var.set(f'R$ {self.int_gasto}')
        self.lucro_var.set(f'R$ {self.int_lucro}')
        self.total_var.set(f'R$ {self.int_total}')

class CadastroFrame(ttk.Frame):
    def __init__(self, master, relatorio_frame, produtos_frame, **kwargs):
        super().__init__(master, **kwargs)

        self.relatorio = relatorio_frame
        self.produtos = produtos_frame
        
        self.entrada_var = tk.StringVar()
        
        self.grid_columnconfigure(1, weight=1) 
        nome_box = ttk.LabelFrame(self,text='Nome')
        nome_box.grid(row=5, column=1, pady=5, sticky='ew')


        pedido_box = ttk.LabelFrame(self, text='Pedido',)
        pedido_box.grid(row=6, column=1, pady=5, sticky='ew')

        cust_box = ttk.LabelFrame(self,text='Custo/Gasto')
        cust_box.grid(row=7, column=1, pady=5, sticky='ew')

        desc_box = ttk.LabelFrame(self,text='Descrição')
        desc_box.grid(row=8, column=1, pady=5, sticky='ew')


        ttk.Label(self, text="       Cadastro de Produto", font=('Arial', 18, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        
        ttk.Label(self, text="Tipo de cadastro:",font=('Arial', 13, 'bold')).grid(row=1, column=0, columnspan=2, pady=(10,0), sticky='w')
        ttk.Radiobutton(self, text='Venda', variable=self.entrada_var,value='venda',cursor='hand2').grid(row=2, column=0, columnspan=2, pady=5, sticky='w')
        ttk.Radiobutton(self, text='Compra', variable=self.entrada_var,value='compra',cursor='hand2').grid(row=3, column=0, columnspan=2, pady=5, sticky='w')

        self.entry_nome = ttk.Entry(nome_box, width=20)
        self.entry_nome.grid(row=0, column=1, pady=5, sticky='ew')

        self.entry_custo = ttk.Entry(cust_box, width=20)
        self.entry_custo.grid(row=0, column=1, pady=5, sticky='ew')

        self.entry_descricao = ttk.Entry(desc_box, width=20)
        self.entry_descricao.grid(row=0, column=1, pady=5, sticky='ew')

        self.entry_pedido = ttk.Entry(pedido_box, width=20)
        self.entry_pedido.grid(row=0, column=1, pady=5, sticky='ew')

        ttk.Button(self, text='Confirmar registro', command=self.enviarDados,cursor='hand2').grid(row=9, column=0, columnspan=2, pady=10,sticky='w')

    def enviarDados(self):
        recebercusto = self.entry_custo.get()
        recebercusto = int(recebercusto)

        recebertipo = self.entrada_var.get()
        receberdescri = self.entry_descricao.get()
        receberpedi = self.entry_pedido.get()

        if recebertipo == 'venda':
            custoreal = recebercusto
        elif recebertipo == 'compra':
            custoreal = recebercusto - (recebercusto * 2)
        recebernome = self.entry_nome.get()
        prod = {
            'nome': recebernome,
            'custo': custoreal,
            "descrição": receberdescri,
            "pedido": receberpedi,
        }
        colecao.insert_one(prod)
        self.limparForms()

        messagebox.showinfo(title='Cadastrado',message='Cadastrado com sucesso!')

        self.relatorio.atualiza()
        self.produtos.informacoesTabela()
            
    def limparForms(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_descricao.delete(0, tk.END)
        self.entry_pedido.delete(0, tk.END)
        self.entry_custo.delete(0, tk.END)
        self.entrada_var.set(False)
        self.entry_nome.focus_set()

class RelatorioFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.columnconfigure(0,weight=1)

        self.gasto_var = tk.StringVar()
        self.lucro_var = tk.StringVar()
        self.total_var = tk.StringVar()

        self.selected_option = tk.StringVar()

        container_dados = ttk.Frame(self)
        container_dados.grid(row=3,column=0)
        container_dados.columnconfigure(0,weight=100)
        container_dados.columnconfigure(1,weight=100)
        container_dados.columnconfigure(2,weight=100)

        container_excel = ttk.Frame(self)
        container_excel.grid(row=4, column=0,sticky='w')

        container_tabela = ttk.Frame(self)
        container_tabela.grid(row=2,column=0)

        container_tabela.rowconfigure(0,weight=1)
        container_tabela.columnconfigure(0,weight=1)

        container_filtro = ttk.Frame(self)
        container_filtro.grid(row=1)

        ttk.Label(self, text="       Relatório Gerencial", font=('Arial', 18, 'bold')).grid(row=0,column=0,sticky='we',columnspan='3')

        self.button_diario = ttk.Button(container_filtro,text='Díario',command=self.filtro_diario)
        self.button_diario.grid(row=0, column=0)
        self.button_semanal = ttk.Button(container_filtro,text='Semanal',command=self.filtro_semanal)
        self.button_semanal.grid(row=0, column=1)
        self.button_mensal = ttk.Button(container_filtro,text='Mensal', command=self.filtro_mensal)
        self.button_mensal.grid(row=0, column=2)
        self.button_todas = ttk.Button(container_filtro,text='Todas', command=self.filtro_todos)
        self.button_todas.grid(row=0, column=3)

        colunas = ('nome','custo', 'data','quantidade')
        self.tabela_relatorio = ttk.Treeview(container_tabela,columns=colunas,show='headings' )
        self.tabela_relatorio.grid(row=0,column=0)
        escrolar = ttk.Scrollbar(container_tabela,orient='vertical')
        escrolar.grid(row=0,column=1,sticky='ns')

        self.tabela_relatorio.config(yscrollcommand=escrolar.set)
        escrolar.config(command=self.tabela_relatorio.yview)

        self.tabela_relatorio.heading('nome',text='NOME')
        self.tabela_relatorio.heading('custo',text='CUSTO')
        self.tabela_relatorio.heading('data',text='DATA')
        self.tabela_relatorio.heading('quantidade',text='Quantidade')

        self.tabela_relatorio.column('nome',width=150)
        self.tabela_relatorio.column('custo',width=100,anchor='center')
        self.tabela_relatorio.column('data',width=100,anchor='center')
        self.tabela_relatorio.column('quantidade',width=200,anchor='center')

        self.informacoesTabela()
        self.calcula()

        custo_frame = ttk.LabelFrame(container_dados,text='GASTOS')
        custo_frame.grid(row=0,column=0)
        ttk.Label(custo_frame,textvariable=self.gasto_var,font=('Arial',12,'bold'),foreground='red').grid(row=0,column=0,pady=10)
        
        lucros_frame = ttk.LabelFrame(container_dados,text='LUCROS')
        lucros_frame.grid(row=0,column=1)
        ttk.Label(lucros_frame,textvariable=self.lucro_var,font=('Arial',12,'bold'),foreground='green').grid(row=0,column=1,pady=10)

        total_frame = ttk.LabelFrame(container_dados,text='TOTAL')
        total_frame.grid(row=0,column=2)
        ttk.Label(total_frame,textvariable=self.total_var,font=('Arial',12,'bold',),foreground='Blue').grid(row=0,column=2,pady=10)

        ttk.Label(container_excel,text='Gerar Relatório',font=('Arial', 15, 'bold')).grid(row=0,column=0,pady=3)
        ttk.Radiobutton(container_excel,text='Diário',variable=self.selected_option,value='diario',cursor='hand2').grid(row=1,column=0,sticky='w')
        ttk.Radiobutton(container_excel,text='Semanal',variable=self.selected_option,value='semanal',cursor='hand2').grid(row=2,column=0,sticky='w')
        ttk.Radiobutton(container_excel,text='Mensal',variable=self.selected_option,value='mensal',cursor='hand2').grid(row=3,column=0,sticky='w')
        ttk.Radiobutton(container_excel,text='Anual',variable=self.selected_option,value='anual',cursor='hand2').grid(row=4,column=0,sticky='w')
        ttk.Button(container_excel,text='GERAR',command=self.geradorPlanilha,style='Blue.TButton',cursor='hand2').grid(row=5,column=0,sticky='w')

    def filtro_diario(self):
        data_hoje_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        data_amanha_inicio = data_hoje_inicio + timedelta(days=1)
        
        f = {'d_obj': {'$gte': data_hoje_inicio, '$lt': data_amanha_inicio}}
        filtro = list(money.find(f))

        for i in self.tabela_relatorio.get_children():
            self.tabela_relatorio.delete(i)

        for i in filtro:
            nome = i['nome']
            custo = i['$']
            data = i['data']
            qtd = i['quantidade']
            self.tabela_relatorio.insert('', 'end', values=(nome, custo, data, qtd))

    def filtro_semanal(self):
        data_fim = datetime.now()
        data_inicio = (data_fim - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        f = {'d_obj': {'$gte': data_inicio, '$lte': data_fim}}
        filtro = list(money.find(f))

        for i in self.tabela_relatorio.get_children():
            self.tabela_relatorio.delete(i)

        for i in filtro:
            nome = i['nome']
            custo = i['$']
            data = i['data']
            qtd = i['quantidade']
            self.tabela_relatorio.insert('', 'end', values=(nome, custo, data, qtd))

    def filtro_mensal(self):
        data_fim = datetime.now()
        data_inicio = (data_fim - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)

        f = {'d_obj': {'$gte': data_inicio, '$lte': data_fim}}
        filtro = list(money.find(f))

        for i in self.tabela_relatorio.get_children():
            self.tabela_relatorio.delete(i)

        for i in filtro:
            nome = i['nome']
            custo = i['$']
            data = i['data']
            qtd = i['quantidade']
            self.tabela_relatorio.insert('', 'end', values=(nome, custo, data, qtd))

    def filtro_todos(self):
        filtro = list(money.find())
        for i in self.tabela_relatorio.get_children():
            self.tabela_relatorio.delete(i)
        for i in filtro:
            nome = i['nome']
            custo = i['$']
            data = i['data']
            qtd = i['quantidade']
            self.tabela_relatorio.insert('', 'end', values=(nome, custo, data,qtd))


    def geradorPlanilha(self):
        data_hoje_fim = datetime.now()
        data_hoje_inicio = data_hoje_fim.replace(hour=0, minute=0, second=0, microsecond=0)
        
        data_s = (data_hoje_fim - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        data_m = (data_hoje_fim - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        data_a = (data_hoje_fim - timedelta(days=365)).replace(hour=0, minute=0, second=0, microsecond=0)

        data_hoje_str = data_hoje_inicio.strftime('%d-%m-%Y')
        data_s_str = data_s.strftime('%d-%m-%Y')
        data_m_str = data_m.strftime('%d-%m-%Y')
        data_a_str = data_a.strftime('%d-%m-%Y')
        
        datafiltro = self.selected_option.get()
        f = {}
        nome_arquivo = 'relatorio.xlsx'

        if datafiltro == 'diario':
            f = {'d_obj': {'$gte': data_hoje_inicio, '$lt': (data_hoje_inicio + timedelta(days=1))}}
            nome_arquivo = f'Controle_Vendas_diario_{data_hoje_str}.xlsx'
        elif datafiltro =='semanal':
            f = {'d_obj': {'$gte': data_s, '$lte': data_hoje_fim}}
            nome_arquivo = f'Controle_Vendas_semanal_{data_s_str}_ate_{data_hoje_str}.xlsx'
        elif datafiltro == 'mensal': 
            f = {'d_obj': {'$gte': data_m, '$lte': data_hoje_fim}}
            nome_arquivo = f'Controle_Vendas_mensal_{data_m_str}_ate_{data_hoje_str}.xlsx'
        elif datafiltro == 'anual':
            f = {'d_obj': {'$gte': data_a, '$lte': data_hoje_fim}}
            nome_arquivo = f'Controle_Vendas_anual_{data_a_str}_ate_{data_hoje_str}.xlsx'
        
        if not f:
            messagebox.showwarning("Atenção", "Por favor, selecione um período para o relatório.")
            return
        
        filtrados = list(money.find(f))
        
        if not filtrados:
            messagebox.showinfo("Sem dados", "Nenhum dado encontrado para o período selecionado.")
            return

        df = pd.DataFrame(filtrados)
        
        mapeamento_colunas = {
            'data': 'Data',
            'nome': 'Nome',
            '$': 'Valor da Venda',
            'quantidade': 'Quantidade'
        }
        df.rename(columns=mapeamento_colunas, inplace=True)
        
        colunas_finais = ['Data', 'Nome', 'Valor da Venda', 'Quantidade']
        
        df_final = df[[col for col in colunas_finais if col in df.columns]]

        total_vendas = df_final['Valor da Venda'].sum() if 'Valor da Venda' in df_final.columns else 0

        with pd.ExcelWriter(nome_arquivo, engine='xlsxwriter') as writer:
            
            workbook = writer.book
            worksheet = workbook.add_worksheet('Relatório')

            formato_titulo = workbook.add_format({'bold': True, 'font_size': 18, 'font_color': 'white', 'bg_color': '#2F5496', 'align': 'center', 'valign': 'vcenter'})
            formato_subtitulo = workbook.add_format({'bold': True, 'font_size': 11, 'bg_color': '#BDD7EE', 'align': 'center', 'valign': 'vcenter'})
            formato_label = workbook.add_format({'bold': True, 'font_size': 10, 'align': 'right'})
            formato_input = workbook.add_format({'bg_color': '#FFFFCC', 'border': 1})
            formato_total_label = workbook.add_format({'bold': True, 'font_size': 11, 'bg_color': '#BDD7EE', 'border': 1})
            formato_total_valor = workbook.add_format({'bold': True, 'font_size': 11, 'bg_color': '#BDD7EE', 'border': 1, 'num_format': 'R$ #,##0.00'})
            formato_comissao_final = workbook.add_format({'bold': True, 'font_size': 11, 'font_color': 'white', 'bg_color': '#70AD47', 'border': 1, 'num_format': 'R$ #,##0.00'})
            formato_painel_lateral = workbook.add_format({'bg_color': "#FFFFFF"})
            formato_data = workbook.add_format({'num_format': 'dd/mm/yyyy', 'align': 'left'})
            formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})
            formato_quantidade = workbook.add_format({'align': 'center'})

            worksheet.set_column('A:B', 0, formato_painel_lateral)
            worksheet.insert_image('A1', 'logoexcel.png', {'x_scale': 0.5, 'y_scale': 0.5, 'x_offset': 10, 'y_offset': 10})

            worksheet.merge_range('C2:H3', 'CONTROLE DE VENDAS CAIXA CERTO', formato_titulo)
            worksheet.merge_range('C4:H4', 'Relatório de vendas', formato_subtitulo)
            
            (num_rows, num_cols) = df_final.shape
            headers = [{'header': col} for col in df_final.columns]
            
            if num_rows > 0:
                worksheet.add_table(10, 2, 10 + num_rows - 1, 2 + num_cols - 1, {
                    'data': df_final.values.tolist(),
                    'columns': headers,
                    'style': 'Table Style Medium 9',
                    'header_row': True
                })
            else:
                 worksheet.merge_range(10, 2, 10, 2 + num_cols - 1, 'Nenhum dado encontrado', formato_input)

            linha_inicio_totais = 10 + num_rows + 2
            worksheet.write(f'D{linha_inicio_totais}', 'Total de Vendas:', formato_total_label)
            worksheet.write(f'E{linha_inicio_totais}', total_vendas, formato_total_valor) 
            
            worksheet.set_column('C:C', 12, formato_data) 
            worksheet.set_column('D:D', 30) 
            worksheet.set_column('E:E', 18, formato_moeda)
            worksheet.set_column('F:F', 12, formato_quantidade)
            worksheet.hide_gridlines(2)
        
        messagebox.showinfo("Sucesso", f"Relatório '{nome_arquivo}' gerado com sucesso!")


    def atualiza(self):
        self.calcula()
        self.informacoesTabela()
    def calcula(self):
        lista_gastos = list(money.find())
        total = 0
        lucro = 0
        gasto = 0
        for i in lista_gastos:
            valor = i.get('$')
            total += valor
            if valor < 0:
                gasto += valor
            else:
                lucro += valor
        self.int_lucro = lucro
        self.int_gasto = gasto
        self.int_total = total
        self.gasto_var.set(f'R$ {self.int_gasto}')
        self.lucro_var.set(f'R$ {self.int_lucro}')
        self.total_var.set(f'R$ {self.int_total}')

    def informacoesTabela(self):
        for i in self.tabela_relatorio.get_children():
            self.tabela_relatorio.delete(i)
        dados = list(money.find({}))
        for i in dados:
            nome = i['nome']
            custo = i['$']
            data = i['data']
            qtd = i['quantidade']
            self.tabela_relatorio.insert('', 'end', values=(nome, custo, data,qtd))

        

        
class ProdutosFrame(ttk.Frame):
    def __init__(self, master, relatorio_frame, **kwargs):
        super().__init__(master, **kwargs)

        self.variavel_string_combo = tk.StringVar()
        
        self.relatorio_frame = relatorio_frame
        
        self.grid_columnconfigure(1, weight=1) 

        main_labelframe = ttk.Frame(self)
        main_labelframe.grid(column=0,row=0,pady=3,columnspan=3)
        tabela_frame = ttk.Frame(self)
        tabela_frame.grid(row=1,column=0,columnspan=2,sticky="nsew",padx=10,pady=10)

        tabela_frame.grid_rowconfigure(0, weight=1)
        tabela_frame.grid_columnconfigure(0, weight=1)

        colunas = ('Nome','Custo','Descrição','Pedido')
        self.tabelap = ttk.Treeview(tabela_frame,columns=colunas,show='headings') 
        escrolar = ttk.Scrollbar(tabela_frame,orient='vertical')

        self.tabelap.config(yscrollcommand=escrolar.set)
        escrolar.config(command=self.tabelap.yview)

        escrolar.grid(row=0,column=1,sticky='ns')
        self.tabelap.bind("<<TreeviewSelect>>", self.itemSelecionado) 



        editar_box = ttk.LabelFrame(main_labelframe,text='Editar Produto',padding=10)
        editar_box.grid(row=0, column=1, pady=2, sticky='n')

        delete_box = ttk.LabelFrame(main_labelframe,text='Excluir',padding=10)
        delete_box.grid(row=0,column=2,pady=2, sticky='en')




        ttk.Label(editar_box, text='Nome:').grid(row=1, column=0, pady=2, sticky='w')
        self.entry_enome = ttk.Entry(editar_box)
        self.entry_enome.grid(row=1, column=1, pady=2, sticky='ew')
        ttk.Label(editar_box, text='Campo:').grid(row=2, column=0, pady=2, sticky='w')
        self.escolher_combo = ttk.Combobox(editar_box,textvariable=self.variavel_string_combo,values=['Nome','Custo/Gasto','Descrição','Pedido',],state='readonly')
        self.escolher_combo.grid(row=2,column=1,pady=2)

        ttk.Label(editar_box, text='Edição:').grid(row=3, column=0, pady=2, sticky='w')
        self.entry_editor = ttk.Entry(editar_box, width=20)
        self.entry_editor.grid(row=3, column=1, pady=2, sticky='ew')

        ttk.Button(editar_box, text='Confirmar', command=self.editar, style='Green.TButton',cursor='hand2').grid(row=4, column=1, pady=5, sticky='w')

        ttk.Label(delete_box, text='Nome:').grid(row=0, column=0, pady=0, sticky='ew')
        self.entry_exnome = ttk.Entry(delete_box)
        self.entry_exnome.grid(row=0, column=1, pady=0, sticky='ew')

        ttk.Button( delete_box, text='Confirmar', command=self.delete, style='Red.TButton',cursor='hand2').grid(row=2, column=1, pady=5, sticky='w')

        self.tabelap.heading('Nome',text='Nome do Produto')
        self.tabelap.heading('Custo',text='Custo') 
        self.tabelap.heading('Descrição',text=' Descrição')
        self.tabelap.heading('Pedido',text=' Pedido')

        self.tabelap.column('Nome',width=100)
        self.tabelap.column('Custo',width=100)
        self.tabelap.column('Descrição',width=100)
        self.tabelap.column('Pedido',width=100)

        self.informacoesTabela()

        self.tabelap.grid(row=0,column=0,sticky='nsew',)


    def itemSelecionado(self, event): 
        itemsele = self.tabelap.focus() 
        dadositem = self.tabelap.item(itemsele) 
        valores = dadositem.get('values') 
        nome = valores[0]
        self.entry_enome.delete(0,tk.END)
        self.entry_exnome.delete(0,tk.END)
        self.entry_enome.insert(0,nome)
        self.entry_exnome.insert(0,nome)

    def informacoesTabela(self):
        for item in self.tabelap.get_children(): 
            self.tabelap.delete(item)
        dados = list(colecao.find({}))
        for i in dados:
            nome = i['nome']
            custo = i['custo']
            descr = i['descrição']
            peidod = i['pedido']
            self.tabelap.insert('',index='end',values = (nome,custo,descr,peidod))


    def delete(self):
        nome = self.entry_exnome.get()
        messagebox_do_delete = messagebox.askokcancel(title='Confirmação', message='Deseja EXCLUIR o produto?')
        if messagebox_do_delete == True: 
            colecao.delete_one({'nome': nome})
            self.informacoesTabela()
            self.limparForms()

    
    def editar(self):
        nome = self.entry_enome.get().lower()
        campo = self.variavel_string_combo.get().lower()
        if campo == "custo/gasto":
            campo = 'custo'
        editor = self.entry_editor.get().lower()
        messagebox_do_edit = messagebox.askokcancel(title='Confirmação', message='Deseja EDITAR o produto?')
        if messagebox_do_edit == True:
            if campo == 'custo':
                editor = float(editor)
            colecao.update_one({'nome': nome}, {"$set": {campo: editor}})
            self.informacoesTabela()
            self.limparForms()
    
    def limparForms(self):
        self.entry_enome.delete(0, tk.END)
        self.entry_editor.delete(0, tk.END)
        self.entry_exnome.delete(0, tk.END)
        self.entry_enome.focus_set()

class App(ThemedTk):
    def __init__(self):
        super().__init__(theme='arc')
        self.title("Sistema CaixaCerto")
        self.geometry("800x600")

        style = ttk.Style(self,)
        style.configure('Green.TLabel', foreground='green')
        style.configure('Red.TLabel', foreground='red') 
        style.configure('Blue.TLabel', foreground='blue')
        style.configure('Green.TButton', foreground='green') 
        style.configure('Red.TButton', foreground='red')
        style.configure('Blue.TButton',foreground='blue')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        sidebar = ttk.Frame(self, width=150)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(5, weight=1)
        
        ttk.Label(sidebar, text="Caixa Certo", font=('Arial', 14, 'bold'),).grid(row=0, column=0, padx=10, pady=20)

        container = ttk.Frame(self)
        container.grid(row=0, column=1, sticky="nsew", padx=20, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.buttons = {}
        
        relatorio_frame = RelatorioFrame(container)
        produtos_frame = ProdutosFrame(container,relatorio_frame=relatorio_frame)
        
        home_frame = HomeFrame(
            container, 
            relatorio_frame=relatorio_frame, 
            produtos_frame=produtos_frame
        )
        
        cadastro_frame = CadastroFrame(
            container, 
            relatorio_frame=relatorio_frame, 
            produtos_frame=produtos_frame
        )
        
        self.frames['home'] = home_frame
        self.frames['cadastro'] = cadastro_frame
        self.frames['relatorio'] = relatorio_frame
        self.frames['produtos'] = produtos_frame
    
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.buttons['home'] = ttk.Button(sidebar, text="Início", command=lambda: self.show_frame("home"),cursor='hand2')
        self.buttons['home'].grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.buttons['relatorio'] = ttk.Button(sidebar, text="Relatório", command=lambda: self.show_frame("relatorio"),cursor='hand2')
        self.buttons['relatorio'].grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.buttons['produtos'] = ttk.Button(sidebar, text="Produtos", command=lambda: self.show_frame("produtos"),cursor='hand2')
        self.buttons['produtos'].grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        self.buttons['cadastro'] = ttk.Button(sidebar, text="Cadastro", command=lambda: self.show_frame("cadastro"),cursor='hand2')
        self.buttons['cadastro'].grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        self.show_frame("home")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        
        for name, button in self.buttons.items():
            if name == page_name:
                button.state(['disabled'])
            else:
                button.state(['!disabled'])

if __name__ == "__main__":
    app = App()
    app.mainloop()