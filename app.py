from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from chatbot import get_response


app = Flask(__name__)
app.secret_key = 'secretkey123'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Kosongkan jika XAMPP tidak pakai password
        database="data_mahasiswa"  # Ganti sesuai nama database kamu di phpMyAdmin
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user'] = user
            session['chat_history'] = []
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error='Login gagal.')
    return render_template('login.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == 'POST':
        user_input = request.form['message']
        response = get_response(user_input)
        session['chat_history'].append(('Anda', user_input))
        session['chat_history'].append(('Bot', response))
        session.modified = True  # Penting agar perubahan disimpan

    return render_template('chat.html', chat_history=session['chat_history'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
