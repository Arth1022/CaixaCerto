import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox 
from pymongo import MongoClient
from datetime import date
from tkinter import messagebox

#conexão#
con = MongoClient('mongodb+srv://arth1022:H&soyam01@caixacerto.c4y3jgg.mongodb.net/')
db = con.get_database("pizzaria")
colecao = db.get_collection("produtos")
money = db.get_collection("gastos/lucros")

#Variaveis Globais#

# =================================================================
# 1. TELAS (FRAMES)
# =================================================================

class HomeFrame(tk.Frame):
    """Tela Inicial:"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Grid para dividir a tela em 2 colunas: Textos (0) e Gráfico (1)
        self.columnconfigure(0, weight=1) # Coluna 0 (textos) se expande
        self.columnconfigure(1, weight=0) # Coluna 1 (gráfico) não se expande
        
        # --- FRAME para Textos e Boas-Vindas (Coluna 0) ---
        text_frame = tk.Frame(self)
        text_frame.grid(row=0, column=0, sticky="nsw", padx=20, pady=20)
        
        tk.Label(text_frame, text="Seja Bem-vindo ao Sistema!", font=('Arial', 18, 'bold')).pack(anchor='w', pady=(0, 5))
        tk.Label(text_frame, text="Patos Pizzas.", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 20))
        
        tk.Label(text_frame, text="Resumo Semanal:", font=('Arial', 14, 'bold')).pack(anchor='w', pady=(10, 5))
        
        tk.Label(text_frame,text="LUCROS:", fg='green', font=('Arial', 14, 'bold')).pack(anchor='w', pady=(10, 5))
        tk.Label(text_frame,text="GASTOS:",fg = 'red', font=('Arial', 14, 'bold')).pack(anchor='w', pady=(10, 5))
        tk.Label(text_frame,text="TOTAL MENSAL:",font=('Arial', 14, 'bold') ).pack(anchor='w', pady=(10, 5))
        
    def calcula():
        lista_gastos = list(money.find())
        total = 0
        lucro = 0
        gasto = 0
        for i in lista_gastos:             #####Precisa ser implementado#######
            valor = i.get('$')
            total += valor
            if valor <0:
                gasto += valor
            else:
                lucro +=valor
                    
        print(total)
        print(lucro)
        print(gasto)
            


class CadastroFrame(tk.Frame): # TELA DE CADASTRO
   

    def __init__(self, master, **kwargs):

        self.entrada_saida_var = tk.BooleanVar() # true ou false
        self.data_auto_var = tk.BooleanVar()

        super().__init__(master, **kwargs)
        
        tk.Label(self, text="Cadastro de Produto", font=('Arial', 18, 'bold')).pack(pady=10)
        
        tk.Label(self, text="Selecioner tipo de cadastro [Marcado]Entrada | [Em Branco]Saida").pack(pady=10,anchor='w')
        tk.Checkbutton(self,text='Entrada/Saida',variable=self.entrada_saida_var).pack(pady=10, anchor='w') # add um popup para que tenha um entry para escrever a data(Da teu jeito ae joao)

        tk.Checkbutton(self,text='Data Automatica',variable=self.data_auto_var).pack(pady=0,anchor='w')



        tk.Label(self,text='Nome:').pack(pady=0,anchor='w')
        self.entry_nome = tk.Entry(self,width=20)
        self.entry_nome.pack(pady=0,anchor='w')

        tk.Label(self,text='Custo/Gasto:').pack(pady=0,anchor='w')
        self.entry_custo = tk.Entry(self,width=20)
        self.entry_custo.pack(pady=0,anchor='w')

        tk.Label(self,text='Descrição:').pack(pady=0,anchor='w')
        self.entry_descricao = tk.Entry(self,width=40,)
        self.entry_descricao.pack(pady=0,anchor='w')

        tk.Label(self,text='Pedido:').pack(pady=0,anchor='w')
        self.entry_pedido = tk.Entry(self,width=40)
        self.entry_pedido.pack(pady=0,anchor='w')

        tk.Button(self,text='Confirmar registro',font=('Arial', 12, 'bold'),width=30,command=self.enviarDados).pack(pady=10,)

    def enviarDados(self):

        recebercusto = self.entry_custo.get()
        recebercusto = int(recebercusto)


        recebertipo = self.entrada_saida_var.get()
        receberdescri = self.entry_descricao.get()
        receberpedi = self.entry_pedido.get()
        if recebertipo == False:
            custoreal = recebercusto - (recebercusto *2)
        else:
            custoreal = recebercusto
        receberdata =  self.data_auto_var.get()
        if receberdata == True:
            data = date.today()
            data = str(data)
        else:
            data  = "Joao ainda nao fez o entry da data" 

        recebernome = self.entry_nome.get()   
        prod = {
        'nome':recebernome,
        'custo':custoreal,
        'data':data,
        "descrição":receberdescri,
        "pedido":receberpedi,
        }
        colecao.insert_one(prod)
        self.limparForms()
            
    def limparForms(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_descricao.delete(0, tk.END)
        self.entry_pedido.delete(0, tk.END)
        
        #Adicionada a limpeza do campo de custo.
        self.entry_custo.delete(0, tk.END)

        #Reseta os Checkbuttons para o estado padrão
        self.entrada_saida_var.set(False)
        self.data_auto_var.set(True) # Volta a ser marcado por padrão
        
        #Opcional: Coloca o foco de volta no primeiro campo
        self.entry_nome.focus_set()



class RelatorioFrame(tk.Frame):
    """Tela de Relatório: Visualização de dados."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        tk.Label(self, text="Relatório Gerencial", font=('Arial', 18, 'bold')).pack(pady=20)
        
        tk.Label(self, text="<< Conteúdo de Relatórios e Gráficos Aqui >>").pack(pady=30)
        
        
class ProdutosFrame(tk.Frame):
    """Tela de Produtos: Listagem e Gestão."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        #AINDA A FAZER : Fazer uma lista de produtos para que seja mostrado no program#

        #Campo Editar
        tk.Label(self,text='Editar Produto',font=('Arial', 12, 'bold')).pack(pady=0,anchor='w')
        tk.Label(self,text='Nome:').pack(pady=0,anchor='w')
        self.entry_enome = tk.Entry(self)
        self.entry_enome.pack(pady=0,anchor='w')
        tk.Label(self,text='Campo a ser editado::').pack(pady=0,anchor='w')
        self.entry_campo = tk.Entry(self,width=10)
        self.entry_campo.pack(pady=0,anchor='w')
        tk.Label(self,text='Edição:').pack(pady=0,anchor='w')
        self.entry_editor = tk.Entry(self,width=10)
        self.entry_editor.pack(pady=0,anchor='w')

        self.button_editar = tk.Button(self,text='Confirmar',command=self.editar,fg='green').pack(pady=0,anchor='w')

        #Campo Deletar
        tk.Label(self,text='Excluir Produto',font=('Arial', 12, 'bold')).pack(pady=0,anchor='w')
        tk.Label(self,text='Nome:').pack(pady=0,anchor='w')
        self.entry_exnome = tk.Entry(self)
        self.entry_exnome.pack(pady=0,anchor='w')

        self.button_excluir = tk.Button(self,text='Confirmar',command=self.delete,fg='red').pack(pady=2,anchor='w')

        tk.Label(self,text='AQUI VAI A LISTA DE PRODUTOS JA ADICIONADOS').pack(pady=0)       ########FAÇA AQUI UM SISTEMA DE ROLAGEM PARA COLOCAR OS PRODUTOS, 
                                                                                           ###TKINTER NAO TEM UMA LABEL NATIVA, MAIS E POSSIVEL FAZER USANDO WIDGET################
        #Adicionar venda/compra
        tk.Label(self, text='Adicionar Venda/Compra').pack(pady=5,side='left')
        self.entry_nproduto = tk.Entry(self, width=20, )
        self.entry_nproduto.pack(pady=10,side='left')

        tk.Button(self,text='Confirmar',fg='green',command=self.getmoney).pack(pady=2,side='left')

    def getmoney(self):
        nomeadd = self.entry_nproduto.get()
        produto = colecao.find_one({'nome': nomeadd})
        gasto = produto['custo']  
        insert = {
            '$':gasto
        }
        self.entry_nproduto.delete(0, tk.END)
        money.insert_one(insert)

    def delete(self):
        nome = self.entry_exnome.get()
        colecao.delete_one({'nome':nome})
        self.limparForms
    

    def editar(self):
        nome = self.entry_enome.get()
        campo = self.entry_campo.get()
        editor = self.entry_editor.get()                                             #####Editar######
        if campo.lower() == 'custo':
            editor = float(editor)
        colecao.update_one({'nome':nome},{"$set":{campo:editor}})
        self.limparForms
    
    def limparForms(self):

        self.entry_campo.delete(0,tk.END)
        self.entry_enome.delete(0,tk.END)
        self.entry_editor.delete(0,tk.END)
        self.entry_enome.focus_set()





# =================================================================
# 2. APLICATIVO PRINCIPAL (Gerencia o Layout e a Troca)
# =================================================================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema CaixaCerto")
        self.geometry("800x500")
        
        # Configuração do Grid principal (Menu e Conteúdo)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1) # Coluna de conteúdo se expande

        # ----------------------------------------------------
        # MENU LATERAL (Sidebar Frame)
        # ----------------------------------------------------
        sidebar = tk.Frame(self, bg='lightgray', width=150)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(5, weight=1)
        
        tk.Label(sidebar, text="CaixaCerto", font=('Arial', 14, 'bold'), bg='lightgray').grid(row=0, column=0, padx=10, pady=20)

        # ----------------------------------------------------
        # CONTAINER (Onde as Telas Serão Empilhadas)
        # ----------------------------------------------------
        container = tk.Frame(self)
        container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.buttons = {}
        
        # Instancia todas as telas e as empilha no container
        for F in (HomeFrame, CadastroFrame, RelatorioFrame, ProdutosFrame): 
            frame_name = F.__name__.replace('Frame', '').lower()
            frame = F(master=container)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew") # Empilhamento

        # ----------------------------------------------------
        # BOTÕES DE NAVEGAÇÃO
        # ----------------------------------------------------
        
        self.buttons['home'] = ttk.Button(sidebar, text="Início", command=lambda: self.show_frame("home"))
        self.buttons['home'].grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.buttons['cadastro'] = ttk.Button(sidebar, text="Cadastro", command=lambda: self.show_frame("cadastro"))
        self.buttons['cadastro'].grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.buttons['relatorio'] = ttk.Button(sidebar, text="Relatório", command=lambda: self.show_frame("relatorio"))
        self.buttons['relatorio'].grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        self.buttons['produtos'] = ttk.Button(sidebar, text="Produtos", command=lambda: self.show_frame("produtos"))
        self.buttons['produtos'].grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        self.show_frame("home") # Define a tela inicial

    def show_frame(self, page_name):
        """Traz o Frame (Tela) desejado para o topo e atualiza o estado do menu."""
        
        frame = self.frames[page_name]
        frame.tkraise()
        
        # Atualiza o estado dos botões (desativa o botão da tela atual)
        for name, button in self.buttons.items():
            if name == page_name:
                button.state(['disabled'])
            else:
                button.state(['!disabled'])


if __name__ == "__main__":
    app = App()
    app.mainloop()