import bcrypt
from pymongo import MongoClient

con = MongoClient('mongodb+srv://arth1022:H&soyam01@caixacerto.c4y3jgg.mongodb.net/')

db = con.get_database('user')
user = db.get_collection('usuarios')
print('Conectado com sucesso!!')

username = input('USERNAME:')
password = input('SENHA:')
password_confirm = input('SENHA:')
empresa = input('EMPRESA:')

if password != password_confirm:
    print('Senhas não colidem!')
    exit()
if user.find_one({'username': username}):
    print('Este usuario ja existe!')
    exit()

password_bytes = password.encode('utf-8')
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password_bytes,salt)

user_dados = {
    "username": username,
    "password_hashed": hashed_password,
    'empresa': empresa
}
user.insert_one(user_dados)
print('Cadastrado com sucesso!')
print('!!NÃO SE ESQUEÇA DE CRIAR A DB NO MONGODB!!')

con.close()