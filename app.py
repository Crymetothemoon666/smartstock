from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def init_db():
    conn = sqlite3.connect('smartstock.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS catalog (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user TEXT, item TEXT, quantity INTEGER, date TEXT)')
    c.executemany("INSERT OR IGNORE INTO catalog (id, name, quantity) VALUES (?, ?, ?)", [
        (1, 'Tomate', 50), (2, 'Papa', 80), (3, 'Zanahoria', 60), (4, 'Manzana', 40),
        (5, 'Arroz', 100), (6, 'Lechuga', 70), (7, 'Huevos', 30), (8, 'Pan', 90), (9, 'Frijoles', 60),
        (10, 'Leche', 55), (11, 'Queso', 45), (12, 'Cebolla', 75), (13, 'Pepino', 65)
    ])
    conn.commit()
    conn.close()

@app.route('/')
def home():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect('smartstock.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (user, pwd))
        result = c.fetchone()
        conn.close()
        if result:
            session['user'] = user
            return redirect(url_for('home'))
        return "Credenciales incorrectas"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect('smartstock.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (user, pwd))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/catalogo')
def catalogo():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('smartstock.db')
    c = conn.cursor()
    c.execute('SELECT * FROM catalog')
    items = c.fetchall()
    conn.close()
    return render_template('catalogo.html', items=items)

@app.route('/pedidos', methods=['GET', 'POST'])
def pedidos():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('smartstock.db')
    c = conn.cursor()
    c.execute('SELECT * FROM catalog')
    items = c.fetchall()
    if request.method == 'POST':
        alimento = request.form['alimento']
        cantidad = int(request.form['cantidad'])
        user = session['user']
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('UPDATE catalog SET quantity = quantity - ? WHERE name = ?', (cantidad, alimento))
        c.execute('INSERT INTO orders (user, item, quantity, date) VALUES (?, ?, ?, ?)', (user, alimento, cantidad, date_str))
        conn.commit()
        conn.close()
        return redirect(url_for('historial'))
    conn.close()
    return render_template('pedidos.html', items=items)

@app.route('/nuevo_alimento', methods=['GET', 'POST'])
def nuevo_alimento():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        conn = sqlite3.connect('smartstock.db')
        c = conn.cursor()
        c.execute('INSERT INTO catalog (name, quantity) VALUES (?, ?)', (name, quantity))
        conn.commit()
        conn.close()
        return redirect(url_for('catalogo'))
    return render_template('nuevo_alimento.html')

@app.route('/historial')
def historial():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('smartstock.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE user = ?', (session['user'],))
    orders = c.fetchall()
    conn.close()
    return render_template('historial.html', orders=orders)

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
