import sqlite3
import os
import requests
import logging
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

app = Flask(__name__, template_folder=template_dir)

app.secret_key = os.getenv('SECRET_KEY', 'chave_secreta_super_segura')



def get_db_connection():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, '..', 'database', 'agenda.db')

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"Erro fatal de conexão com o banco de dados: {e}")
        return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()

        if conn is None:
            flash('Sistema temporariamente indisponível. Tente novamente mais tarde.')
            return render_template('login.html')

        try:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        except sqlite3.Error as e:
            logging.error(f"Erro ao consultar usuário: {e}")
            flash('Erro interno ao validar credenciais.')
            user = None
        finally:
            conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect(url_for('agenda'))
        else:
            flash('Credenciais inválidas.')

    return render_template('login.html')


@app.route('/agenda')
@login_required
def agenda():
    url_api = os.getenv('API_URL', 'http://127.0.0.1:5000/api/agendamentos')

    agendamentos_validados = []
    mensagem_erro = None

    try:
        resposta = requests.get(url_api, timeout=5, cookies=request.cookies)
        resposta.raise_for_status()
        dados_json = resposta.json()

        campos_obrigatorios = ['paciente', 'CPF', 'medico', 'especialidade', 'data', 'horario', 'convenio', 'status']

        for item in dados_json:
            if all(campo in item for campo in campos_obrigatorios):
                agendamentos_validados.append(item)
            else:
                logging.warning(f"Registro ignorado por falta de campos obrigatórios: {item}")

    except requests.exceptions.Timeout:
        logging.error("Timeout: A API de agendamentos demorou muito para responder.")
        mensagem_erro = "Não foi possível carregar a agenda no momento."
    except requests.exceptions.ConnectionError:
        logging.error("Connection Error: Falha ao tentar conectar na API de agendamentos.")
        mensagem_erro = "Não foi possível carregar a agenda no momento."
    except ValueError:
        logging.error("Erro de Parsing: A resposta da API não é um JSON válido.")
        mensagem_erro = "Erro ao processar os dados da agenda."
    except Exception as e:
        logging.error(f"Erro inesperado ao consultar agendamentos: {e}")
        mensagem_erro = "Ocorreu um erro inesperado."

    return render_template('agenda.html', agendamentos=agendamentos_validados, mensagem_erro=mensagem_erro)


@app.route('/api/agendamentos', methods=['GET'])
@login_required
def obter_agendamentos():
    conn = get_db_connection()

    if conn is None:
        return jsonify([])

    try:
        agendamentos_db = conn.execute('''
                                       SELECT paciente,
                                              cpf as CPF,
                                              medico,
                                              especialidade,
                                              data,
                                              horario,
                                              convenio,
                                              status
                                       FROM appointments
                                       ''').fetchall()

        # Converte as linhas do banco (sqlite3.Row) para uma lista de dicionários padrão do Python
        agendamentos_reais = [dict(row) for row in agendamentos_db]

        return jsonify(agendamentos_reais)

    except sqlite3.Error as e:
        logging.error(f"Erro ao buscar agendamentos na API: {e}")
        return jsonify([])

    finally:
        if conn:
            conn.close()


@app.route('/')
def index():
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')