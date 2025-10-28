# Sistema Caixa Certo

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter(TTK)-yellowgreen.svg)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-green.svg)
![PyMongo](https://img.shields.io/badge/Driver-PyMongo-lightgreen.svg)
![Pandas](https://img.shields.io/badge/Data-Pandas-orange.svg)
![XlsxWriter](https://img.shields.io/badge/Export-XlsxWriter-red.svg)
![Bcrypt](https://img.shields.io/badge/PassWord-Bcrypt-black.svg)

## 🎯 Sobre o Projeto

O **Sistema Caixa Certo** é uma aplicação desktop desenvolvida em Python com a biblioteca Tkinter para interface gráfica, projetada para auxiliar no gerenciamento de vendas, lucros, gastos e produtos. O sistema utiliza o MongoDB como banco de dados para persistência dos dados e permite a geração de relatórios de desempenho em formato Excel (xlsx).

É ideal para pequenos negócios, como pizzarias que necessitam de uma solução simples e eficiente para controle financeiro e de estoque/produtos.

## Funcionalidades

O sistema é dividido em uma tela de LOGIN e quatro telas principais (Frames): Início, Relatório, Produtos e Cadastro.

### ➜] Login
* **Login da Empresa:** Login de USUÁRIO E SENHA da empresa (*já cadastrada anteriormente no cadastrar_usuario.py*).
* **Troca de DB** Ao realizar um login bem-sucedido, o código irá alterar para o DB que possui o nome da empresa e mostrar as outras telas do app.
### 🏠 Início 
* **Adicionar Venda/Compra:** Registro rápido de movimentações financeiras (vendas ou gastos).
* **Produto e Quantidade:** Insere o nome do produto cadastrado e a quantidade vendida/comprada. O valor é buscado automaticamente do cadastro de produtos.
* **Data Automática:** Opção para usar a data e hora atuais ou inserir uma data específica.
* **Resumo Semanal/Diário:** Exibe um resumo de *Gastos*, *Vendas (Lucros)* e *Total* do dia.

### 📈 Relatório 
* **Visualização de Dados:** Exibe todas as movimentações financeiras em uma tabela (*Treeview*).
* **Filtros de Período:** Permite filtrar a tabela por período:
    * Diário
    * Semanal
    * Mensal
    * Todas
* **Resumo Geral:** Calcula e exibe o total de Gastos, Lucros (Vendas) e o Total Geral das movimentações registradas no banco de dados.
* **Geração de Planilha Excel:** Exporta o relatório filtrado (Diário, Semanal, Mensal ou Anual) para um arquivo `.xlsx` usando as bibliotecas `pandas` e `xlsxwriter`, com formatação visual.

### 📦 Produtos 
* **Visualização de Produtos:** Lista todos os produtos cadastrados com Nome, Custo, Descrição e Pedido (campo de informação extra).
* **Edição:** Permite selecionar um produto na lista e editar um campo específico (Nome, Custo/Gasto, Descrição, Pedido).
* **Exclusão:** Permite deletar um produto pelo nome.

### 📝 Cadastro
* **Registro de Produtos:** Formulário para cadastrar novos itens.
* **Tipo de Cadastro:** Define se o item é uma `Venda` (custo positivo/lucro) ou `Compra` (custo negativo/gasto).
* **Campos:** Nome, Custo/Gasto, Descrição e Pedido.

## ⚙️ Tecnologias Utilizadas

* **Python 3.x:** Linguagem de programação principal.
* **Tkinter:** Biblioteca padrão do Python para criação da Interface Gráfica (GUI).
* **ttkthemes:** Usado para aplicar temas modernos (`arc`) ao Tkinter.
* **MongoDB (PyMongo):** Banco de dados NoSQL utilizado para armazenar produtos e movimentações financeiras.
* **Pandas:** Usado para manipulação e estruturação dos dados antes da exportação para Excel.
* **tkcalendar (DateEntry):** Componente para seleção de datas.
* **Bcrypt (Criptografia de senha)** Criptografar as senhas no db.

## 🚀 Como Executar

### Pré-requisitos

Certifique-se de ter o Python 3.x instalado.

### 1. Instalação das Dependências

O projeto utiliza bibliotecas externas que precisam ser instaladas:

**VS CODE:** pip install pymongo ttkthemes tkcalendar pandas xlsxwriter Bcrypt

Execução
Após a instalação das dependências e a configuração da conexão com o banco de dados, execute:
cadastrar_usuario.py (cadastre uma empresa ou usuário de teste)
python AppMain.py (Iniciar o app)

### 🤝 Contribuições
Este é um projeto universitário, mas contribuições, sugestões e relatórios de bugs são bem-vindos. Sinta-se à vontade para abrir uma issue ou um pull request.

## Usado por

Esse projeto é usado pelas seguintes empresas:

- Quero Pizza Patos de Minas | R. dos Guaranís, 237 - Caramuru, Patos de Minas - MG, 38701-267 Telefone: (34) 3814-1234
 
## Licença

[MIT](https://choosealicense.com/licenses/mit/)
