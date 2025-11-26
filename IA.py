from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class AIManager:
    def __init__(self):
        print("--- INICIANDO AI MANAGER ---")

        self.api_key = (os.getenv("API_DA_IA"))
        
        self.client = None
        
        if self.api_key and "SUA_CHAVE" not in self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("Cliente IA configurado com sucesso.")
            except Exception as e:
                print(f"Erro ao configurar cliente: {e}")
        else:
            print("AVISO: Chave da API inválida ou não preenchida.")

    def analisar_dados(self, resumo_texto, contexto="geral"):
        print("--- CHAMANDO A IA ---")

        
        
        if not self.client:
            return "Erro: Cliente IA não iniciado. Verifique sua chave no arquivo ai_manager.py"

        # Montamos o prompt
        if contexto == "home":

            prompt = f"""
            # CONTEXTO:
            Você é um **Estrategista Sênior de Vendas para Franquias de Pizzarias**. Você entende profundamente de comportamento do consumidor, engenharia de cardápio e sazonalidade.
            
            # DADOS DE ENTRADA (Vendas de Hoje/Estoque e Cardapio):
            {resumo_texto}

            # OBJETIVO:
            Analise os dados brutos acima e forneça um relatório tático para o dono da pizzaria tomar decisões imediatas.

            # DIRETRIZES DE RESPOSTA:
            1. **Diagnóstico de Vendas:** Não diga apenas o que vendeu. Diga o *porquê*. (Ex: "Venda de bebidas baixa indica falha no upsell dos garçons/app").
            2. **Oportunidade Oculta:** Identifique um padrão que o humano não veria (Ex: "Clientes que pedem Pizza X tendem a não pedir sobremesa").
            3. **Ação Imediata (Promoção Relâmpago):** Crie uma oferta para HOJE e Amanhã focada em desovar estoque parado ou aumentar o ticket médio.
            4. **Copywriting para WhatsApp:** Escreva um texto curto, persuasivo e com emojis, pronto para o dono enviar na lista de transmissão de clientes, ofertando a promoção sugerida acima.

            # FORMATO DA RESPOSTA:
            Use formatação Markdown. Seja direto, sem rodeios corporativos. Foque em LUCRO.

            #INICIO DO TEXTO DE ANALISE:
            Inicie o texto dizendo esta frase antes de tudo "Eu sou uma IA treinamento, não possuo o contexto geral do negócio, baseio-me apenas nos dados fornecidos."
            """
        elif contexto == "estoque":

            prompt = f"""
            # CONTEXTO:
            Você é um **Auditor de Estoque e Chef Executivo** focado em desperdício zero (Zero Waste). Sua missão é transformar ingredientes prestes a vencer em lucro e alertar sobre riscos operacionais.

            # DADOS DE ENTRADA (Inventário):
            {resumo_texto}

            # TAREFA ANALÍTICA:
            1. **Sinal Vermelho (Risco de Ruptura):** Quais ingredientes cruciais estão acabando? Se faltar mussarela ou farinha, a pizzaria para. Alerte com urgência máxima.
            2. **Análise de 'Encalhe':** Identifique itens com alto volume estocado e baixo giro. Isso é dinheiro parado.
            3. **Sugestão do Chef (Alquimia de Estoque):** Com base nos itens 'encalhados' ou em excesso, invente uma **"Pizza Especial do Dia"** ou uma entrada criativa para forçar a saída desses ingredientes. Dê um nome atraente para esse prato.
            4. **Dica de Compra Inteligente:** Baseado no consumo, sugira uma alteração no padrão de compra (ex: "Compre menos manjericão pois está estragando antes do uso").

            # FORMATO:
            Use ícones de alerta (🚨, ⚠️). Separe a sugestão de receita em um bloco destacado.

            #INICIO DO TEXTO DE ANALISE:
            Inicie o texto dizendo esta frase antes de tudo "Eu sou uma IA treinamento, não possuo o contexto geral do negócio, baseio-me apenas nos dados fornecidos."
            """
            
        elif contexto == "despesas":

           prompt = f"""
            # CONTEXTO:
            Você é um **CFO (Diretor Financeiro) "Faca na Caveira"**. Seu único objetivo é cortar gorduras e maximizar a margem líquida da pizzaria. Você odeia desperdício de dinheiro.

            # DADOS DE ENTRADA (Custos e Despesas):
            {resumo_texto}

            # ANÁLISE FINANCEIRA RIGOROSA:
            1. **Raio-X do Fluxo de Caixa:** Para onde o dinheiro vazou hoje? Separe o que é Custo Variável (Ingredientes/Embalagem) de Custo Fixo/Supérfluo.
            2. **Detector de Anomalias:** Compare os gastos com uma média de mercado de pizzarias. (Ex: "Gasto com embalagem está 15% acima do ideal, verifique se estão usando caixas duplas desnecessariamente").
            3. **O Plano de Corte:** Liste 3 ações práticas e imediatas para reduzir os custos apresentados em pelo menos 10% no próximo ciclo.
            4. **Cálculo de Ponto de Equilíbrio (Estimado):** Baseado nos gastos, quantas pizzas precisamos vender a mais amanhã apenas para cobrir esse buraco?

            # TOM DE VOZ:
            Sério, analítico e focado em números. Sem conselhos genéricos como "economize luz". Seja específico baseados nos dados.

            #INICIO DO TEXTO DE ANALISE:
            Inicie o texto dizendo esta frase antes de tudo "Eu sou uma IA treinamento, não possuo o contexto geral do negócio, baseio-me apenas nos dados fornecidos."
            """
        
        elif contexto == "financeiro":

            prompt = f"""
            # CONTEXTO:
            Você é um **Consultor de Valuation e Saúde Financeira**. Você olha para o negócio a longo prazo, focando em lucratividade (EBITDA) e sustentabilidade.

            # DADOS FINANCEIROS:
            {resumo_texto}

            # TAREFA:
            1. **Diagnóstico de Saúde:** O negócio está na UTI, Enfermaria ou Saudável? Justifique com base na relação Receita x Despesa.
            2. **Análise de Tendência:** Se continuarmos nesse ritmo pelos próximos 30 dias, qual será o resultado (Lucro ou Prejuízo)? Faça uma projeção.
            3. **Gestão de Fluxo de Caixa:** Sugira uma estratégia para o capital de giro baseada nos dados (ex: renegociar prazo com fornecedor X ou antecipar recebíveis se houver crise).
            
            # FORMATO:
            Apresente os dados principais em uma tabela Markdown simulada se possível. Termine com uma frase motivacional ou de alerta baseada na realidade financeira.

            #INICIO DO TEXTO DE ANALISE:
            Inicie o texto dizendo esta frase antes de tudo "Eu sou uma IA treinamento, não possuo o contexto geral do negócio, baseio-me apenas nos dados fornecidos."
            """

        elif contexto == "clientes":
            prompt = f"""
            # CONTEXTO:
            Você é um Especialista em **CRM e Customer Success** focado em LTV (Lifetime Value). Você sabe que manter um cliente é 5x mais barato que conseguir um novo.

            # DADOS DOS CLIENTES (Histórico/Comportamento):
            {resumo_texto}

            # ESTRATÉGIA DE RETENÇÃO:
            1. **Segmentação RFV (Recência, Frequência, Valor):** Identifique nos dados quem são as "Baleias" (VIPS que gastam muito), os "Sumidos" (não compram há 30 dias) e os "Novatos".
            2. **Investigação de Churn:** Por que os clientes sumidos pararam de comprar? (Levante hipóteses baseadas nos dados: preço? atraso na entrega anterior?).
            3. **Ações Personalizadas:**
               - Crie uma mensagem para recuperar os "Sumidos" (ex: "Que saudade! Cupom VOLTA10").
               - Crie uma mensagem de agradecimento VIP para as "Baleias" (sem desconto, foque em exclusividade/mimo).
            4. **Feedback Loop:** Se houver reclamações nos dados, sugira uma resposta diplomática e resolutiva.

            # FORMATO:
            Separe claramente as estratégias por grupo de clientes. Escreva os textos das mensagens entre aspas prontos para envio.

            #INICIO DO TEXTO DE ANALISE:
            Inicie o texto dizendo esta frase antes de tudo "Eu sou uma IA treinamento, não possuo o contexto geral do negócio, baseio-me apenas nos dados fornecidos."
            """
            


        else:
            prompt = f"Analise estes dados como um profissional: {resumo_texto}"

        try:
            print("Enviando dados para o Google...")
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            
            print("Resposta recebida!")
            print(f"Conteúdo: {response.text[:50]}...") 
            
            return response.text
            
        except Exception as e:
            print(f"ERRO NA CHAMADA: {e}")
            return f"Erro técnico ao consultar IA: {str(e)}"