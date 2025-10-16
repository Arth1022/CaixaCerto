📊 Sistema CaixaCerto

Um sistema de gestão de caixa desenvolvido em Python com Tkinter e MongoDB, que permite cadastrar produtos, registrar vendas/compras, acompanhar relatórios financeiros e exportar planilhas em Excel.

🚀 Funcionalidades

-Tela inicial (Home)

Registrar vendas/compras rapidamente.

Visualizar resumo semanal de gastos, lucros e total.

-Cadastro de Produtos

Adicionar novos produtos (entrada/saída).

Informar custo, descrição, pedido e data automática.

-Relatórios Gerenciais

Tabela de movimentações com gastos, lucros e totais.

Exportação de relatórios em Excel (Diário, Semanal, Mensal, Anual).

Arquivos gerados com layout formatado (título, tabela e totais).

-Gestão de Produtos

Listagem completa de produtos cadastrados.

Edição de informações (nome, custo, descrição, etc).

Exclusão de registros.

🛠️ Tecnologias Utilizadas

Python 3.10+

Tkinter (Interface gráfica)

ttkthemes (Estilização de interface)

MongoDB Atlas (Banco de dados em nuvem)

Pandas e XlsxWriter (Exportação para Excel)

📦 Instalação

Clone o repositório:

git clone https://github.com/Arth1022/CaixaCerto.git
cd CaixaCerto


Crie um ambiente virtual (opcional, mas recomendado):

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install pymongo pandas xlsxwriter ttkthemes

▶️ Uso

Execute o programa com:

python AppMain.py


A janela principal do sistema será aberta com as opções: Início, Cadastro, Relatório e Produtos.

📂 Estrutura do Projeto

AppMain.py(Aplicativo Principal), README.md,  logoexcel.png 

📊 Relatório Excel

Geração automática de relatórios profissionais em Excel.

Inclui logotipo, tabela formatada e totais de vendas.

⚠️ Observações

É necessário ter um banco de dados MongoDB Atlas configurado.

Atualize a string de conexão no código (AppMain.py) com suas credenciais.

O arquivo logoexcel.png precisa estar na pasta raiz para aparecer nos relatórios.

👨‍💻 Autor

Desenvolvido por Arthur
