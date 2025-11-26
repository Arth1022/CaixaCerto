from pymongo import MongoClient
from datetime import datetime, timedelta
import bcrypt
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseManager:
    def __init__(self):
        uri = 'mongodb+srv://arth1022:H&soyam01@caixacerto.c4y3jgg.mongodb.net/'
        self.client = MongoClient(uri)
        self.user_db = self.client.get_database('user')
        self.users_collection = self.user_db.get_collection('usuarios')
        
        self.current_db = None
        self.products_col = None
        self.finance_col = None
        self.caixa_col = None
        self.clients_col = None
        self.company_name = None

    def authenticate(self, username, password):
        user_data = self.users_collection.find_one({'username': username})
        if not user_data: return False, "Usuário não cadastrado!"
        self.username = user_data['username']
        stored_hash = user_data['password_hashed']
        if isinstance(password, str): password = password.encode('utf-8')
            
        if bcrypt.checkpw(password, stored_hash):
            self.setup_company_context(user_data['empresa'])
            return True, "Login realizado com sucesso"
        else:
            return False, "Senha incorreta!"

    def setup_company_context(self, company_name):
        self.company_name = company_name
        self.current_db = self.client.get_database(company_name)
        self.products_col = self.current_db.get_collection("produtos")
        self.caixa_col = self.current_db.get_collection("caixa_turnos")
        self.clients_col = self.current_db.get_collection("clients")
        self.finance_col = self.current_db.get_collection("gastos/lucros")

    # --- PRODUTOS ---
    def get_products_names(self, tipos=None):
        if self.products_col is None: return []
        query = {}
        if tipos:
            query = {'tipo_produto': {'$in': tipos}}
        return [p['nome'] for p in self.products_col.find(query)]

    def get_all_products(self, tipos=None):
        if self.products_col is None: return []
        query = {}
        if tipos:
            query = {'tipo_produto': {'$in': tipos}}
        return list(self.products_col.find(query))

    def get_product_details(self, product_name):
        if self.products_col is None: return 0, 0, ""
        data = self.products_col.find_one({'nome': product_name})
        if data:
            return data.get('custo', 0), data.get('estoque', 0), data.get('tipo_produto', 'produto')
        return 0, 0, ""

    def registrar_venda_carrinho(self, itens_carrinho, pagamento, data_obj, taxa_entrega=0.0, entregador_nome="", cliente_dict=None):
        if self.products_col is None: return False, print("Erro BD")
        
        pedido_id = int(datetime.now().timestamp())
        total_produtos = 0
        
        print(f"\nINICIANDO VENDA {pedido_id}") 

        try:
            for item in itens_carrinho:
                if item.get('is_half'):
                    total_produtos += item['total']
                    sabores = [item['sabor1'], item['sabor2']]
                    for sabor in sabores:
                        prod_db = self.products_col.find_one({'nome': sabor})
                        if prod_db:
                            receita = prod_db.get('receita', [])
                            for ing in receita:
                                self.products_col.update_one({'nome': ing['ingrediente']}, {'$inc': {'estoque': -(ing['qtd'] * item['qtd'] * 0.5)}})
                else:
                    prod_db = self.products_col.find_one({'nome': item['nome']})
                    if not prod_db: continue
                    total_produtos += prod_db.get('custo', 0) * item['qtd']
                    receita = prod_db.get('receita', [])
                    if receita:
                        for ing in receita:
                            self.products_col.update_one({'nome': ing['ingrediente']}, {'$inc': {'estoque': -(ing['qtd'] * item['qtd'])}})
                    else:
                        self.products_col.update_one({'nome': item['nome']}, {'$inc': {'estoque': -item['qtd']}})

            valor_bruto = total_produtos + taxa_entrega
            
            taxas = self.get_taxas_pagamento()
            percentual_taxa = 0.0
            
            import unicodedata 
            pag_lower = unicodedata.normalize('NFKD', pagamento).encode('ASCII', 'ignore').decode('ASCII').lower()
            
            if "debito" in pag_lower: percentual_taxa = taxas.get('debito', 0)
            elif "credito" in pag_lower: percentual_taxa = taxas.get('credito', 0)
            elif "pix" in pag_lower: percentual_taxa = taxas.get('pix', 0)
            
            desconto_maquina = valor_bruto * (percentual_taxa / 100)
            valor_liquido = valor_bruto - desconto_maquina

            resumo_visual = []
            for i in itens_carrinho:
                if i.get('is_half'): resumo_visual.append(f"{i['qtd']}x 1/2 {i['sabor1']} / 1/2 {i['sabor2']}")
                else: resumo_visual.append(f"{i['qtd']}x {i['nome']}")

            doc_venda = {
                'pedido_id': pedido_id, 
                'nome': f"Pedido #{pedido_id}", 
                'resumo_itens': resumo_visual,
                'cust': valor_bruto,       
                'valor_liquido': valor_liquido, 
                'taxa_maquina_cobrada': desconto_maquina, 
                'valor_produtos': total_produtos, 
                'taxa_entrega': taxa_entrega,
                'entregador': entregador_nome, 
                'data': data_obj.strftime("%d/%m/%Y"), 
                'd_obj': data_obj,
                'quantidade': 1, 
                'pagamento': pagamento, 
                'tipo': 'venda',
                'status_cozinha': 'Pendente', 
                'modo': 'delivery' if taxa_entrega > 0 else 'balcao',
                'cliente_telefone': cliente_dict.get('telefone') if cliente_dict else None
            }
                       
            self.finance_col.insert_one(doc_venda)

            if cliente_dict and cliente_dict.get('telefone'):
                self.registrar_interacao_cliente(cliente_dict['telefone'], cliente_dict.get('nome'), data_obj)

            return True, f"Venda Salva! Líquido: R$ {valor_liquido:.2f}"
            
        except Exception as e:
            print(f"ERRO FATAL: {e}") 
            return False, f"Erro: {str(e)}"
    
    def verificar_estoque_suficiente(self, itens_carrinho):
        if self.products_col is None: return False, "Erro BD"
        demanda_total = {}
        
        for item in itens_carrinho:
            if item.get('is_half'):
               
                sabores = [item['sabor1'], item['sabor2']]
                qtd_item = item['qtd']
                
                for sabor in sabores:
                    prod_db = self.products_col.find_one({'nome': sabor})
                    if not prod_db: continue
                    
                    receita = prod_db.get('receita', [])
                    fator = 0.5
                    
                    if receita:
                        for ing in receita:
                            demanda_total[ing['ingrediente']] = demanda_total.get(ing['ingrediente'], 0) + (ing['qtd'] * qtd_item * fator)
            else:
                prod_db = self.products_col.find_one({'nome': item['nome']})
                if not prod_db: continue
                
                receita = prod_db.get('receita', [])
                if receita:
                    for ing in receita:
                        demanda_total[ing['ingrediente']] = demanda_total.get(ing['ingrediente'], 0) + (ing['qtd'] * item['qtd'])
                else:
                    demanda_total[item['nome']] = demanda_total.get(item['nome'], 0) + item['qtd']
        
        erros = []
        for nome, qtd_nec in demanda_total.items():
            item_db = self.products_col.find_one({'nome': nome})
            if not item_db: continue
            
            if item_db.get('estoque', 0) < qtd_nec:
                erros.append(f"Falta {(qtd_nec - item_db.get('estoque', 0)):.3f} de {nome}")
        
        return (False, "\n".join(erros)) if erros else (True, "OK")

    def register_product(self, name, cost, description, 
                         request_code, tipo_produto="pizza",unidade="un",receita=None):
        if self.products_col is None: return
        
        prod = {
            'nome': name.lower(),
            'custo': cost,
            "descrição": description.lower(),
            "pedido": request_code.lower(),
            "estoque": 0,
            "unidade": unidade,
            "tipo_produto": tipo_produto,
            "receita": receita if receita else [] #
        }
        self.products_col.insert_one(prod)

    def update_product(self, name, field, value):
        if self.products_col is None: return
        self.products_col.update_one({'nome': name}, {"$set": {field: value}})

    def delete_product(self, name):
        if self.products_col is None: return
        self.products_col.delete_one({'nome': name})

    # --- BUSCAS FINANCEIRAS ---
    
    def get_financial_data(self, start_date=None, end_date=None):
        if self.finance_col is None: return []
        query = {}
        if start_date:
             query = {'d_obj': {'$gte': start_date, '$lt': start_date + timedelta(days=1)}}
        return list(self.finance_col.find(query))

    def get_financial_data_by_month(self, month, year):
        if self.finance_col is None: return []
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
            
        query = {'d_obj': {'$gte': start_date, '$lt': end_date}}
        return list(self.finance_col.find(query))

    def get_payments_by_month(self, month, year):
        if self.finance_col is None: return []
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        pipeline = [
            {"$match": {
                "tipo": "venda",
                "d_obj": {"$gte": start_date, "$lt": end_date}
            }},
            {"$group": {
                "_id": "$pagamento",
                "total": {"$sum": "$cust"}
            }},
            {"$sort": {"total": -1}}
        ]
        return list(self.finance_col.aggregate(pipeline))

    # --- GRÁFICOS HOME ---
    def get_top_products(self):
      
        if self.finance_col is None: return []
        
        vendas = self.finance_col.find({'tipo': 'venda', 'd_obj' : {'$gte' : datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}})
        
        contador = {}

        for v in vendas:
           
            if 'resumo_itens' in v and isinstance(v['resumo_itens'], list):
                for item_str in v['resumo_itens']:
                    try:
                        qtd_str, nome_prod = item_str.split('x ', 1)
                        qtd = int(qtd_str)
                        
                        contador[nome_prod] = contador.get(nome_prod, 0) + qtd
                    except:
                        continue 

            else:
                nome = v.get('nome', 'Desconhecido')
                if "Pedido #" in nome: continue
                
                qtd = v.get('quantidade', 1)
                contador[nome] = contador.get(nome, 0) + qtd

        sorted_items = sorted(contador.items(), key=lambda x: x[1], reverse=True)[:5]
        
        resultado = [{"_id": name, "total_qtd": qtd} for name, qtd in sorted_items]
        
        return resultado
    
    def get_weekly_balance(self):
        if self.finance_col is None: return []
        start_date = datetime.now() - timedelta(days=6)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {"$match": {"d_obj": {"$gte": start_date}}}, 
            {"$group": {
                "_id": {"$dateToString": {"format": "%d/%m", "date": "$d_obj"}},
                "saldo": {"$sum": "$cust"}
            }},
            {"$sort": {"_id": 1}} 
        ]
        return list(self.finance_col.aggregate(pipeline))
    
    def registrar_despesa(self, descricao, valor, categoria, date_obj):
        if self.finance_col is None: return False, "Erro BD"

        valor_final = -abs(valor)

        self.finance_col.insert_one({
            'nome': descricao,     
            'cust': valor_final,    
            'data': date_obj.strftime("%d/%m/%Y"),
            'd_obj': date_obj,
            'quantidade': 1,        
            'pagamento': 'Gasto Mensal',
            'tipo': 'despesa', 
            'categoria': categoria  
        })

        return True, "Despesa Regeistrada com sucesso"

    def get_recent_expenses(self, limit=20):
        if self.finance_col is None: return []
        
        cursor = self.finance_col.find({'tipo': 'despesa'}).sort('d_obj', -1).limit(limit)
        return list(cursor)
    

    
    def get_status_caixa(self):
        if self.caixa_col is None: return None
        return self.caixa_col.find_one({'status': 'aberto'})

    def abrir_caixa(self, valor_inicial, data_obj):
        if self.caixa_col is None: return False, "Erro BD"
        if self.get_status_caixa(): return False, "Caixa já está aberto!"
        self.caixa_col.insert_one({
            'abertura': data_obj,
            'funcionario': self.username,
            'fechamento': None,
            'saldo_inicial': valor_inicial,
            'saldo_final_sistema': 0,
            'saldo_final_real': 0,
            'diferenca': 0,
            'status': 'aberto'
        })
        return True, "Caixa aberto!"

    def registrar_movimentacao_caixa(self, tipo, valor, descricao, data_obj):
        if self.finance_col is None: return False, "Erro BD"
        turno = self.get_status_caixa()
        if not turno: return False, "Abra o caixa primeiro!"

        valor_final = -abs(valor) if tipo == 'sangria' else abs(valor)
        
        self.finance_col.insert_one({
            'nome': f"{tipo.upper()}: {descricao}",
            'cust': valor_final,
            'data': data_obj.strftime("%d/%m/%Y"),
            'd_obj': data_obj,
            'quantidade': 1,
            'pagamento': 'Dinheiro', 
            'tipo': 'movimentacao_caixa',
            'subtipo': tipo,
            'turno_id': turno['_id']
        })
        return True, f"{tipo} registrada!"

    def calcular_saldo_atual(self):
        turno = self.get_status_caixa()
        if not turno: return 0.0
        
        saldo = turno['saldo_inicial']
        abertura = turno['abertura']
        
        movimentacoes = self.finance_col.find({
            'd_obj': {'$gte': abertura},
            'pagamento': 'Dinheiro' 
        })
        mov_list = list(movimentacoes)
        for mov in mov_list:
            saldo += mov.get('valor_liquido', 0)
            
        return saldo

    def fechar_caixa(self, valor_conferido, data_obj):
        turno = self.get_status_caixa()
        if not turno: return False, "Caixa fechado."
        
        saldo_sistema = self.calcular_saldo_atual()
        diferenca = valor_conferido - saldo_sistema
        
        self.caixa_col.update_one(
            {'_id': turno['_id']},
            {'$set': {
                'fechamento': data_obj,
                'funcionario': self.username,
                'saldo_final_sistema': saldo_sistema,
                'saldo_final_real': valor_conferido,
                'diferenca': diferenca,
                'status': 'fechado'
            }}
        )
        return True, f"Caixa Fechado! Diferença: R$ {diferenca:.2f}"

    def get_historico_caixa(self):
        if self.caixa_col is None: return []
        return list(self.caixa_col.find({'status': 'fechado'}).sort('fechamento', -1).limit(10))
    
    # --- CONTROLE DE PERDAS E DESPERDÍCIO/Estoque ---
    def repor_estoque(self, nome_produto, quantidade, data_obj):
    
        if self.products_col is None: return False, "Erro de conexão com BD"
        
        prod = self.products_col.find_one({'nome': nome_produto})
        if not prod: return False, "Produto não encontrado no banco."

        try:
            self.products_col.update_one(
                {'nome': nome_produto},
                {'$inc': {'estoque': quantidade}}
            )

            return True, f"Sucesso! +{quantidade} {prod.get('unidade', 'un')} em {nome_produto}"

        except Exception as e:
            return False, f"Erro ao atualizar: {str(e)}"

    def registrar_perda(self, nome_produto, qtd, motivo, data_obj):
        if self.products_col is None: return False, "Erro BD"
        
        prod = self.products_col.find_one({'nome': nome_produto})
        if not prod: return False, "Produto não encontrado"
        if prod.get('unidade') == 'kg' or prod.get('unidade') == 'l':
            qtd /= 1000
        
        custo_unitario = prod.get('custo', 0)
        prejuizo_total = -(custo_unitario * qtd) 
        
        try:
            self.products_col.update_one(
                {'nome': nome_produto}, 
                {'$inc': {'estoque': -qtd}}
            )
            
            self.finance_col.insert_one({
                'nome': f"PERDA: {nome_produto}", 
                'cust': prejuizo_total,            
                'data': data_obj.strftime("%d/%m/%Y"),
                'd_obj': data_obj,
                'quantidade': qtd,
                'pagamento': 'Estoque Perdido',    
                'tipo': 'perda',                   
                'motivo': motivo,                  
                'categoria': 'Prejuízo Operacional'
            })
            
            return True, f"Perda de {qtd} {prod.get('unidade','un')} registrada."
            
        except Exception as e:
            return False, f"Erro ao registrar perda: {str(e)}"
        
        # --- GESTÃO DE MOTOBOYS ---
    def add_entregador(self, nome):
        if self.current_db is None: return False
        config_col = self.current_db.get_collection("configuracoes")
        
        config_col.update_one(
            {"tipo": "lista_entregadores"},
            {"$addToSet": {"nomes": nome}}, 
            upsert=True
        )
        return True

    def get_entregadores(self):
        if self.current_db is None: return []
        config_col = self.current_db.get_collection("configuracoes")
        doc = config_col.find_one({"tipo": "lista_entregadores"})
        if doc and "nomes" in doc:
            return sorted(doc["nomes"])
        return []

    # --- DADOS PARA IA  ---
    def get_daily_sales_text(self): ##IA da home
        try:
            hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            dados_daily = self.get_financial_data(hoje)
            if dados_daily is None:
                return [],
            all_products = self.get_all_products()
            if all_products is None:
                return [],
            return list(dados_daily,all_products)
        except:
            print ("Erro ao obter dados diários para IA")

    def get_inventory_text(self):
        prods = self.get_all_products(['ingrediente', 'bebida'])
        res = "Estoque:\n"
        for p in prods: res += f"- {p['nome']}: {p.get('estoque', 0)} {p.get('unidade','un')}\n"
        return res

    def get_expenses_text(self):
        desps = self.get_recent_expenses()
        res = "Despesas Recentes:\n"
        for d in desps: res += f"- {d['nome']}: R$ {abs(d.get('cust', 0)):.2f}\n"
        return res
    
    def get_monthly_summary_text(self, m, y):
        dados = self.get_financial_data_by_month(m, y)
        dados_financeiro = list(dados)
        return dados_financeiro
    

    
    def delete_transaction(self, t_id):
        if self.finance_col:
            self.finance_col.delete_one({'_id': ObjectId(t_id)})
            return True, "Apagado"
        return False, "Erro"
    
    def get_clientes(self):
        if self.clients_col is None: return []
        return list(self.clients_col.find().sort("ultima_compra", -1))
    

    def buscar_cliente_pelo_telefone(self, telefone):
        if self.clients_col is None or not telefone: return None
        tel_limpo = "".join(filter(str.isdigit, telefone))
        return self.clients_col.find_one({"telefone": tel_limpo})

    def registrar_interacao_cliente(self, telefone, nome_opcional, data_obj):
  
        if self.clients_col is None or not telefone: return
        
        tel_limpo = "".join(filter(str.isdigit, telefone))
        if not tel_limpo: return

        update_data = {
            "$set": {"ultima_compra": data_obj},
            "$inc": {"total_pedidos": 1}
        }
        

        if nome_opcional:
            update_data["$set"]["nome"] = nome_opcional

        self.clients_col.update_one(
            {"telefone": tel_limpo},
            update_data,
            upsert=True 
        )

    def set_taxas_pagamento(self, debito, credito, pix):

        if self.current_db is None: return False
        config_col = self.current_db.get_collection("configuracoes")

        config_col.update_one(
            {"tipo": "taxas_pagamento"},
            {"$set": {
                "debito": float(debito),
                "credito": float(credito),
                "pix": float(pix)
            }},
            upsert=True
        )
        return True
        
    def get_taxas_pagamento(self):

        if self.current_db is None: return {"debito": 0.0, "credito": 0.0, "pix": 0.0}
        config_col = self.current_db.get_collection("configuracoes")

        dados = config_col.find_one({"tipo": "taxas_pagamento"})
        if dados:
            return {
                "debito": dados.get("debito", 0.0),
                "credito": dados.get("credito", 0.0),
                "pix": dados.get("pix", 0.0)
            }
        return {"debito": 0.0, "credito": 0.0, "pix": 0.0}
    
    # --- KDS (COZINHA) ---
    def get_kds_orders(self):
        if self.finance_col is None: return []
        query = {
            'tipo': 'venda',
            'status_cozinha': {'$in': ['Pendente', 'Preparando', 'Pronto']}
        }
        return list(self.finance_col.find(query).sort('pedido_id', 1))

    def avancar_status_kds(self, pedido_id):
        if self.finance_col is None: return False
        
        pedido = self.finance_col.find_one({'pedido_id': pedido_id})
        if not pedido: return False
        
        atual = pedido.get('status_cozinha', 'Pendente')
        novo = atual
        
        if atual == 'Pendente': novo = 'Preparando'
        elif atual == 'Preparando': novo = 'Pronto'
        elif atual == 'Pronto': novo = 'Entregue' 
        
        self.finance_col.update_one(
            {'pedido_id': pedido_id},
            {'$set': {'status_cozinha': novo}}
        )
        return True, novo