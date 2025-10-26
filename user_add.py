import os
import hashlib
from pymongo import MongoClient
from getpass import getpass

def hash_password(password, salt):
    """Gera um hash SHA-256 da senha com um salt."""
    pwd_bytes = password.encode('utf-8')
    salt_bytes = salt
    hashed = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, 100000)
    return hashed

con = MongoClient('mongodb+srv://arth1022:H&soyam01@caixacerto.c4y3jgg.mongodb.net/')
db = con.get_database("user")
user_collection = db.get_collection("usuarios")

username = str(input('Usuario:'))
password = input('Senha:')
password_confirmar = input('Digite sua senha novamente')

if password != password_confirmar:
    print('Senhas não são iguais')
    exit()
if user_collection.find_one({username:username}):
    print('Usuario ja existe no DB')
    exit()

salt = os.urandom(32) #Vai criar 32 bytes aleatorios para o salt
password_hash = hash_password(password,salt)

user_dados = {
    'username': username,
    'password_hash': password_hash,
    'salt':salt
}

user_collection.insert_one(user_dados)
print('Usuario Criado com sucesso!!!!')
con.close()




