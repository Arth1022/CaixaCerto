import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from pymongo import MongoClient
from datetime import date, timedelta
from tkinter import messagebox
import pandas as pd #pip install pandas xlsxwriter

con = MongoClient('mongodb+srv://arth1022:H&soyam01@caixacerto.c4y3jgg.mongodb.net/')
db = con.get_database("pizzaria")
colecao = db.get_collection("produtos")
money = db.get_collection("gastos/lucros")

class HomeFrame(ttk.Frame):
    def __init__(self, master, relatorio_frame, produtos_frame, **kwargs):
        super().__init__(master, **kwargs)

        # ARMAZENAR AS REFERÊNCIAS
        self.relatorio_frame = relatorio_frame
        self.produtos_frame = produtos_frame
        
        #Variaveis de string para atualizar automaticamente
        self.gasto_var = tk.StringVar()
        self.lucro_var = tk.StringVar()
        self.total_var = tk.StringVar()

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
        
        ttk.Label(add_box, text='Nome do Produto:').grid(column=0)
        self.entry_nproduto = ttk.Entry(add_box, width=14)
        self.entry_nproduto.grid(row=0,column=1)
        ttk.Label(add_box,text="Quatidade:").grid(row=1,column=0,pady=2)
        self.entry_qtd = ttk.Entry(add_box,width=14)
        self.entry_qtd.grid(row=1, column=1)

        ttk.Button(add_box, text='Confirmar', style='Green.TButton', command=self.getmoney).grid(row=2,column=1,pady=5)

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
    
    def getmoney(self):
        nomeadd = self.entry_nproduto.get()
        qtd = self.entry_qtd.get()
        qtd = int(qtd)
        produto = colecao.find_one({'nome': nomeadd})
        gasto = produto['custo']
        nome = produto['nome']
        data0 = produto['data']
        data = date.today()
        data_str = data.strftime("%d%m%Y")
        data_int = int(data_str)
        insert = {
            'nome' : nome,
            '$': gasto * qtd,
            'data': data0,
            'quantidade' : qtd,
            'dint': data_int
        }
        money.insert_one(insert)
        self.calcula()
        self.entry_nproduto.delete(0, tk.END)
        self.entry_qtd.delete(0,tk.END)
        self.relatorio_frame.atualiza()

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

class CadastroFrame(ttk.Frame):
    def __init__(self, master, relatorio_frame, produtos_frame, **kwargs):
        super().__init__(master, **kwargs)

        self.relatorio = relatorio_frame
        self.produtos = produtos_frame
        
        self.entrada_var = tk.BooleanVar()
        self.saida_var = tk.BooleanVar() 
        self.data_auto_var = tk.BooleanVar(value=True)
        
        self.grid_columnconfigure(1, weight=1) 
        nome_box = ttk.LabelFrame(self,text='Nome')
        nome_box.grid(row=5, column=1, pady=5, sticky='ew')


        pedido_box = ttk.LabelFrame(self, text='Pedido',)
        pedido_box.grid(row=6, column=1, pady=5, sticky='ew')

        cust_box = ttk.LabelFrame(self,text='Custo/Gasto')
        cust_box.grid(row=7, column=1, pady=5, sticky='ew')

        desc_box = ttk.LabelFrame(self,text='Descrição')
        desc_box.grid(row=8, column=1, pady=5, sticky='ew')


        ttk.Label(self, text="                 Cadastro de Produto", font=('Arial', 18, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        
        ttk.Label(self, text="Tipo de cadastro:",font=('Arial', 13, 'bold')).grid(row=1, column=0, columnspan=2, pady=(10,0), sticky='w')
        ttk.Checkbutton(self, text='Entrada', variable=self.entrada_var).grid(row=2, column=0, columnspan=2, pady=5, sticky='w')
        ttk.Checkbutton(self, text='Saida', variable=self.saida_var).grid(row=3, column=0, columnspan=2, pady=5, sticky='w')

        ttk.Checkbutton(self, text='Data Automatica', variable=self.data_auto_var).grid(row=4, column=0, columnspan=2, pady=5, sticky='w')

        self.entry_nome = ttk.Entry(nome_box, width=20)
        self.entry_nome.grid(row=0, column=1, pady=5, sticky='ew')

        self.entry_custo = ttk.Entry(cust_box, width=20)
        self.entry_custo.grid(row=0, column=1, pady=5, sticky='ew')

        self.entry_descricao = ttk.Entry(desc_box, width=20)
        self.entry_descricao.grid(row=0, column=1, pady=5, sticky='ew')

        self.entry_pedido = ttk.Entry(pedido_box, width=20)
        self.entry_pedido.grid(row=0, column=1, pady=5, sticky='ew')

        ttk.Button(self, text='Confirmar registro', command=self.enviarDados).grid(row=9, column=0, columnspan=2, pady=10,sticky='w')

    def enviarDados(self):
        recebercusto = self.entry_custo.get()
        recebercusto = int(recebercusto)

        recebertipo = self.entrada_var.get()
        recebertipo2 = self.saida_var.get()

        receberdescri = self.entry_descricao.get()
        receberpedi = self.entry_pedido.get()

        if recebertipo == True and recebertipo2 == True or recebertipo == False and recebertipo2 == False:
            custoreal = recebercusto
            custoreal = 0
        elif recebertipo2 == True:
            custoreal = recebercusto - (recebercusto * 2)
        elif recebertipo == True:
            custoreal = recebercusto
        
        receberdata = self.data_auto_var.get()

        data = date.today()
        data_str = data.strftime("%d%m%Y")
        data_int = int(data_str)

        if receberdata == True:
            data = str(data)
        else:
            data = "Joao ainda nao fez o entry da data"                    #########FAZ A DATA JOAO###########

        recebernome = self.entry_nome.get()
        prod = {
            'nome': recebernome,
            'custo': custoreal,
            'data': data,
            "descrição": receberdescri,
            "pedido": receberpedi,
            'dint': data_int
        }
        colecao.insert_one(prod)
        self.limparForms()
        self.relatorio.atualiza()
        self.produtos.informacoesTabela()
            
    def limparForms(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_descricao.delete(0, tk.END)
        self.entry_pedido.delete(0, tk.END)
        self.entry_custo.delete(0, tk.END)
        self.entrada_var.set(False)
        self.saida_var.set(False)
        self.data_auto_var.set(True)
        self.entry_nome.focus_set()

class RelatorioFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        ttk.Label(self, text="                          Relatório Gerencial", font=('Arial', 18, 'bold')).grid(row=0,column=0,sticky='we',columnspan='3')

        self.columnconfigure(0,weight=1)

        self.gasto_var = tk.StringVar()
        self.lucro_var = tk.StringVar()
        self.total_var = tk.StringVar()

        self.selected_option = tk.StringVar()

        container_dados = ttk.Frame(self)
        container_dados.grid(row=2,column=0)
        container_dados.columnconfigure(0,weight=100)
        container_dados.columnconfigure(1,weight=100)
        container_dados.columnconfigure(2,weight=100)

        container_excel = ttk.Frame(self)
        container_excel.grid(row=3, column=0,sticky='w')

        container_tabela = ttk.Frame(self)
        container_tabela.grid(row=1,column=0)

        container_tabela.rowconfigure(0,weight=1)
        container_tabela.columnconfigure(0,weight=1)

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

        ttk.Label(container_excel,text='Gerar Relatório em EXCEL',font=('Arial', 15, 'bold')).grid(row=0,column=0)
        ttk.Radiobutton(container_excel,text='Diário',variable=self.selected_option,value='diario').grid(row=1,column=0,sticky='w')
        ttk.Radiobutton(container_excel,text='Semanal',variable=self.selected_option,value='semanal').grid(row=2,column=0,sticky='w')
        ttk.Radiobutton(container_excel,text='Mensal',variable=self.selected_option,value='mensal').grid(row=3,column=0,sticky='w')
        ttk.Radiobutton(container_excel,text='Anual',variable=self.selected_option,value='anual').grid(row=4,column=0,sticky='w')
        ttk.Button(container_excel,text='GERAR',command=self.geradorPlanilha,style='Blue.TButton').grid(row=5,column=0,sticky='w')
        
    def geradorPlanilha(self):
        #Vai calcular o passado anual,mensal.etc...
        data_hoje = date.today()
        data_sete_dias_atras = data_hoje - timedelta(days=7)
        data_um_mes_atras = data_hoje - timedelta(days=30)
        data_um_ano = data_hoje - timedelta(days=365)
        data_strhj = data_hoje.strftime("%d%m%Y")
        data_strmes = data_um_mes_atras.strftime("%d%m%Y")
        data_strsemana = data_sete_dias_atras.strftime("%d%m%Y")
        data_anual = data_um_ano.strftime("%d%m%Y")

        #Vai transformar em um numero inteiro para fazer o calculo
        dataa = int(data_anual)
        datahj = int(data_strhj)
        datam = int(data_strmes)
        datase = int(data_strsemana)

        datafiltro = self.selected_option.get()
        filtrados = []

        if datafiltro == 'diario':
            f = {'dint': {'$eq':datahj }}
            nome_arquivo = f'Controle_Vendas_diario_{data_hoje}.xlsx'
        elif datafiltro =='semanal':
            f = {'dint': {'$gte':datase, '$lte':datahj}}
            nome_arquivo = f'Controle_Vendas_semanal_{data_sete_dias_atras}.xlsx'
        elif datafiltro == 'mensal':  
            f = {'dint': {'$gte':datam}}
            nome_arquivo = f'Controle_Vendas_mensal_{data_um_mes_atras}.xlsx'
        elif datafiltro == 'anual':
            f = {'dint': {'$lte': datahj}}
            nome_arquivo = f'Controle_Vendas_anual_{data_um_ano}.xlsx'
        if f:
            filtrados = list(money.find(f))
        else:
            filtrados = []
        df = pd.DataFrame(filtrados)

        #Usei IA para fazer a formatação do excel um pouco mais profissional e fiz alterações, mas aconselho saber pelo menos o basico para poder fazer modificações,adicinar e etc...Use a 
        #documentação do PANDAS e xlsxwriter
        # ======================================================================
        # 2. PREPARAÇÃO DOS DADOS PARA O NOVO TEMPLATE (A ponte entre os códigos)
        # ======================================================================
        # Supondo que seus dados em 'filtrados' tenham as colunas: 'data', 'nome', 'custo'
        # Vamos renomeá-las para corresponder ao nosso template profissional.
        mapeamento_colunas = {
            'data': 'Data',
            'nome': 'Nome',
            '$': 'Valor da Venda'
            # Adicione aqui outros mapeamentos se necessário, ex: 'id_venda': 'Nº da Venda'
        }
        df.rename(columns=mapeamento_colunas, inplace=True)
            
        # Selecionando a ordem final das colunas que queremos na tabela
        colunas_finais = ['Data', 'Nome', 'Valor da Venda', 'total']
        # Filtra o dataframe para garantir que só existam as colunas desejadas e na ordem certa
        df_final = df[[col for col in colunas_finais if col in df.columns]]

        # Calculando os totais com base nos dados reais do banco
        total_vendas = df_final['Valor da Venda'].sum() if 'Valor da Venda' in df_final.columns else 0

        # ======================================================================
        # 3. CRIAÇÃO DA PLANILHA FORMATADA (Lógica do novo template)
        # ======================================================================
        with pd.ExcelWriter(nome_arquivo, engine='xlsxwriter') as writer:
            
            workbook = writer.book
            worksheet = workbook.add_worksheet('Relatório')

            # --- Definição de todos os formatos ---
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

            # --- Desenhando o Layout ---
            
            # A. Painel Lateral
            worksheet.set_column('A:B', 0, formato_painel_lateral)
            worksheet.insert_image('A1', 'logoexcel.png', {'x_scale': 0.5, 'y_scale': 0.5, 'x_offset': 10, 'y_offset': 10})

            # B. Títulos e Inputs
            worksheet.merge_range('C2:H3', 'CONTROLE DE VENDAS CAIXA CERTO', formato_titulo)
            worksheet.merge_range('C4:H4', 'Relatório de vendas', formato_subtitulo)
            # C. Tabela Principal usando add_table() para estilo zebrado
            (num_rows, num_cols) = df_final.shape
            headers = [{'header': col} for col in df_final.columns]
            worksheet.add_table(10, 2, 10 + num_rows, 2 + num_cols - 1, {
                'data': df_final.values.tolist(),
                'columns': headers,
                'style': 'Table Style Medium 9',
                'header_row': True
            })
            
            # D. Totais
            linha_inicio_totais = 10 + num_rows + 2
            worksheet.write(f'D{linha_inicio_totais}', 'Total de Vendas:', formato_total_label)
            worksheet.write(f'E{linha_inicio_totais}', total_vendas, formato_total_valor)           
            # E. Ajustes Finais de Colunas
            worksheet.set_column('C:C', 12, formato_data)  # Data
            worksheet.set_column('D:D', 30)                # Nome
            worksheet.set_column('E:E', 18, formato_moeda) # Valor da Venda
            worksheet.set_column('F:F', 18, formato_moeda) # Comissão
            worksheet.hide_gridlines(2)


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
        
        self.relatorio_frame = relatorio_frame
        
        self.grid_columnconfigure(1, weight=1) 

        main_labelframe = ttk.Frame(self)
        main_labelframe.grid(column=0,row=0,pady=3,columnspan=3)
        tabela_frame = ttk.Frame(self)
        tabela_frame.grid(row=1,column=0,columnspan=2,sticky="nsew",padx=10,pady=10)

        tabela_frame.grid_rowconfigure(0, weight=1)
        tabela_frame.grid_columnconfigure(0, weight=1)

        colunas = ('Nome','Custo','Data','Descrição','Pedido')
        self.tabelap = ttk.Treeview(tabela_frame,columns=colunas,show='headings') 
        escrolar = ttk.Scrollbar(tabela_frame,orient='vertical')

        #Config
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
        self.entry_campo =ttk.Entry(editar_box, width=20)
        self.entry_campo.grid(row=2, column=1, pady=2, sticky='ew')
        ttk.Label(editar_box, text='Edição:').grid(row=3, column=0, pady=2, sticky='w')
        self.entry_editor = ttk.Entry(editar_box, width=20)
        self.entry_editor.grid(row=3, column=1, pady=2, sticky='ew')

        #Confirmar
        ttk.Button(editar_box, text='Confirmar', command=self.editar, style='Green.TButton').grid(row=4, column=1, pady=5, sticky='w')
        #Confirmar

        ttk.Label(delete_box, text='Nome:').grid(row=0, column=0, pady=0, sticky='ew')
        self.entry_exnome = ttk.Entry(delete_box)
        self.entry_exnome.grid(row=0, column=1, pady=0, sticky='ew')

        ttk.Button( delete_box, text='Confirmar', command=self.delete, style='Red.TButton').grid(row=2, column=1, pady=5, sticky='w')

        self.tabelap.heading('Nome',text='Nome do Produto')
        self.tabelap.heading('Custo',text='Custo/Preço') 
        self.tabelap.heading('Data',text=' Data') 
        self.tabelap.heading('Descrição',text=' Descrição')
        self.tabelap.heading('Pedido',text=' Pedido')

        self.tabelap.column('Nome',width=100)
        self.tabelap.column('Custo',width=100)
        self.tabelap.column('Data',width=100,anchor='center') 
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
        self.entry_enome.insert(0,nome)

    def informacoesTabela(self):
        for item in self.tabelap.get_children(): 
            self.tabelap.delete(item)
        dados = list(colecao.find({}))
        for i in dados:
            nome = i['nome']
            custo = i['custo']
            data = i['data']
            descr = i['descrição']
            peidod = i['pedido']
            self.tabelap.insert('',index='end',values = (nome,custo,data,descr,peidod,))


    def delete(self):
        nome = self.entry_exnome.get()
        colecao.delete_one({'nome': nome})
        self.informacoesTabela()
        self.limparForms()
        self.relatorio_frame.atualiza()
    
    def editar(self):
        nome = self.entry_enome.get()
        campo = self.entry_campo.get()
        editor = self.entry_editor.get()
        if campo.lower() == 'custo':
            editor = float(editor)
        colecao.update_one({'nome': nome}, {"$set": {campo: editor}})
        self.informacoesTabela()
        self.limparForms()
        self.relatorio_frame.atualiza()
    
    def limparForms(self):
        self.entry_campo.delete(0, tk.END)
        self.entry_enome.delete(0, tk.END)
        self.entry_editor.delete(0, tk.END)
        self.entry_exnome.delete(0, tk.END)
        self.entry_enome.focus_set()

class App(ThemedTk):
    def __init__(self):
        super().__init__(theme='arc')
        self.title("Sistema CaixaCerto")
        self.geometry("800x500")

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
        
        # 4. Posiciona todas as telas no grid (uma em cima da outra)
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.buttons['home'] = ttk.Button(sidebar, text="Início", command=lambda: self.show_frame("home"))
        self.buttons['home'].grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.buttons['cadastro'] = ttk.Button(sidebar, text="Cadastro", command=lambda: self.show_frame("cadastro"))
        self.buttons['cadastro'].grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.buttons['relatorio'] = ttk.Button(sidebar, text="Relatório", command=lambda: self.show_frame("relatorio"))
        self.buttons['relatorio'].grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        self.buttons['produtos'] = ttk.Button(sidebar, text="Produtos", command=lambda: self.show_frame("produtos"))
        self.buttons['produtos'].grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
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