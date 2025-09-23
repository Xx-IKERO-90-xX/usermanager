import os
import sys
import json
from datetime import datetime
from flask import request, Flask, render_template, redirect, session, sessions, url_for
from werkzeug.utils import secure_filename
import asyncio
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from models.User import User
import controller.SecurityController as security

settings = {}

with open("settings.json") as setting:
    settings = json.load(setting)

app = Flask(__name__)
app.secret_key = "a40ecfce592fd63c8fa2cda27d19e1dbc531e946"
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{settings['mysql']['user']}:{settings['mysql']['passwd']}@{settings['mysql']['host']}/{settings['mysql']['db']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context()


@app.route('/')
async def index():
    if await security.admin_user_exists():
        if 'id' in session:
            return render_template('index.jinja')
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('start'))

# Ruta para crear el usuario Administrador
@app.route('/start', methods=['GET', 'POST'])
async def start():
    if not await security.admin_user_exists(): 
        if request.method == 'GET':
            return render_template('start.jinja')
        
        else:
            passwd = request.form['passwd']
            passwd_confirm = request.form['passwd_confirm']
            
            if passwd_confirm == passwd:
                passwd = await security.encrypt_passwd(passwd)

                user = User('Administrator', passwd, 'Admin', True, True)
                db.session.add(user)
                db.session.commit()

                return redirect(url_for('login'))

            else:
                error_msg = "Las contraseñas no coinciden!!!"
                return render_template(
                    'start.jinja', 
                    error_msg=error_msg
                )
    
    else:
        return redurect(url_for('index'))

# Ruta para el Login
@app.route('/login', methods=['GET', 'POST'])
async def login():
    if 'id' not in session:
        if request.method == 'GET':
            return render_template('login.jinja')
        
        else:
            username = request.form['username']
            passwd = request.form['passwd']

            if await security.verify_login(username, passwd):
                user = db.session.query(User).filter(User.username == username).first()

                session['id'] = user.id
                session['username'] = user.username
                session['role'] = user.role

                return redirect(url_for('index'))
            
            else:
                error_msg = 'Los datos del login son incorrectos!!!'
                return render_template(
                    'login.jinja',
                    error_msg=error_msg
                )

    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(
        host=settings['flask']['host'],
        port=settings['flask']['port'],
        debug=settings['flask']['debug']
    )
