from pymongo import MongoClient
from datetime import date

#conexão#
con = MongoClient('mongodb+srv://arth1022:H&soyam01@caixacerto.c4y3jgg.mongodb.net/')
db = con.get_database("pizzaria")
colecao = db.get_collection("produtos")
money = db.get_collection("gastos/lucros")

#Variaveis Globais#
today = date.today()

#functions#
def cadastroProduto():
    produto = (input("Nome:"))
    tipo = (input("[1]Entrada | [2]Saida"))
    custo= float(input("Custo/Gasto:"))
    dataperg = (input('Data automatica? S|N')) 
    desc = (input("Descrição: "))
    pedido = (input("Pedido: "))                     #####Cadastro#####
    if dataperg.lower() == 'n':
        data = input("Digita a data (DD/MM/YYYY): ")
    else:
        data = today.strftime('%d/%m/%Y') 
    if tipo == '2':
        custo = custo - (custo*2)
    prod = {
        'nome':produto,
        'custo/gasto':custo,
        'data':data,
        "descrição": desc,
        "pedido": pedido
    }
    colecao.insert_one(prod)

def editar():
    nome = input("Nome do produto a ser editado:")
    perg = input("NOME | CUSTO | DATA | Descrição | Pedido")
    edicao = input("Qual a edição a ser feita?")                        #####Editar######
    if perg.lower() == "custo":
        perg = 'custo/gasto'
        edicao = float(edicao)
    editar = colecao.update_one({'nome':nome},{"$set":{perg.lower():edicao}})

def remover():
    nome = input("Nome do produto a ser removido:")
    veri = input("[1]Confirmar | [2]Cancelar")           ###Remove####
    if veri == "1": 
        colecao.delete_one({'nome': nome})

def getmoney():
    nomeadd = input("Digite o nome do produto para buscar o custo: ")
    produto = colecao.find_one({'nome': nomeadd})
    gasto = produto['custo/gasto']                                      #Valor do produto
    print(gasto)
    insert = {
        '$':gasto
    }
    money.insert_one(insert)

def calcula():
    lista_gastos = list(money.find())
    total = 0
    lucro = 0
    gasto = 0
    for i in lista_gastos:             
        valor = i.get('$')
        total += valor
        if valor <0:
            gasto += valor
        else:
            lucro +=valor
                
    print(total)
    print(lucro)
    print(gasto)
            
