from passlib.hash import pbkdf2_sha256
from models.User import User
from extensions import db

# Comprueba si el usuario administrador existe o no
async def admin_user_exists():
    admin_user = db.session.query(User).filter(User.username == 'Administrator').first()
    return True if admin_user else False

# Verifica el Login
async def verify_login(username, passwd):
    valid = False
    user = db.session.query(User).filter(User.username == username).first()
    
    if user:
        if await verify_passwd(passwd, user.passwd):
            valid = True

    return valid


# Encripta la contraseña
async def encrypt_passwd(passwd):
    hash_passwd = pbkdf2_sha256.hash(passwd)
    return hash_passwd

# Verifica si la contraseña concuerda con la del hash
async def verify_passwd(passwd, hash):
    return pbkdf2_sha256.verify(passwd, hash)