import bcrypt
from pymongo import MongoClient
from getpass import getpass

con = MongoClient('mongodb+srv://arth1022:H&soyam01@caixacerto.c4y3jgg.mongodb.net/')

db = con.get_database('user')
user = db.get_collection('usuarios')
print('Conectado com sucesso!!')

username = input('USERNAME:')
password = input('SENHA:')
password_confirm = input('SENHA:')

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
}
user.insert_one(user_dados)
print('Cadastrado com sucesso!')

con.close()