#-*- coding: utf-8 -*-
"""
	a microblog example application written as Flask tutorial
	with Flask and sqlite3.
"""
from __future__ import with_statement
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def render_redirect(template, url, error):
    if error == None:
        return redirect(url_for(url))
    return render_template(template, error=error)

class User(object):
    '''
    Represent a user.
    init whit login, have session
    '''

    def __init__(self, email):
        self.signed_in = False
        self.email = email
        self.db = connect_db()

    def signin(self, pwss):
        error = None
        cur = self.db.cursor()

        email_ = cur.execute(u"SELECT EXISTS ( SELECT email FROM userdata where email = ?)", (self.email, ) ).fetchone()
        if email_[0] == 0:
            error = "Invalid"
        else:
            pwss_ = cur.execute(u"SELECT EXISTS ( SELECT password FROM userdata where email = ?)", (self.email, ) ).fetchone()
            if pwss_[0] == pwss:
                error = "Invalid"
            else:
                session['logged_in'] = True
                self.signed_in = True
                self.name = self.db.execute('select username from userdata where email=\'' + request.form['email'] + '\'').fetchone()
                flash('Welcom ' + self.name[0])
        return error

    def signup(self, email, name, pwss, pwsc):
        error = None
        cur = self.db.cursor()

        if "" in [email, name, pwss, pwsc]:
            error = "Filed is Empty!"
        elif pwss != pwsc:
            error = 'Password does not match'
        else:
            email_ = cur.execute(u'SELECT EXISTS (SELECT email FROM userdata WHERE email = ?)', (email, )).fetchone()
            name_ = cur.execute(u'SELECT EXISTS (SELECT username FROM userdata WHERE username = ?)', (name, )).fetchone()
            
            if email_[0] == 0 and name_[0] == 0:
                flash('Account Created!')
                self.db.execute('insert into userdata (email, username, password) values (?, ?, ?)', [email, name, pwss])
                self.db.commit()
            else:
                error = "Already Exist"
        return error
    
    def changeinfo(self):
        error = None
        return redirect(url_for('mypage'))

    def signout(self):
        error = None
        return redirect(url_for('signin'))



def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', "r") as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def front():
    #db = get_db()
    #cur = db.execute('select title, text from entries order by id desc')
    #entries = cur.fetchall()
    return render_template('front.html')

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['username']
        pwss = request.form['password']
        pwsc = request.form['passconf']

        if "" in [email, name, pwss, pwsc]:
            error = 'Empty Filed'
        else:
            user = User(email)
            error = user.signup(email, name, pwss, pwsc)
        return render_redirect('signup.html', 'signin', error)
    else:
        return render_template('signup.html', error=error)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        pwss = request.form['password']
        if "" in [email, pwss]:
            error = 'Empty Filed'
        else:
            user = User(email)
            error = user.signin(pwss)
        return render_redirect('signin.html', 'front', error)
    else:
        return render_template('signin.html', error=error)

@app.route('/signout')
def signout():
    session.pop('logged_in', None)
    flash('Sign out')
    return redirect(url_for('front'))

@app.route('/mypage')
def mypage():
    error = None

    return render_template('mypage.html', error=error)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80)
