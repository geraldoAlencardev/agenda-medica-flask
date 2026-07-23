import sqlite3
import os
import requests
import logging
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps
from dotenv import load_dotenv  # <-- NOVO IMPORT

# Carrega as variáveis do arquivo .env
load_dotenv()  # <-- NOVA CHAMADA

# Configuração básica de Logs para registrar erros no terminal
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Mapeia o caminho absoluto para a pasta templates na raiz do projeto
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')

# Inicializa o Flask apontando para a pasta correta
app = Flask(__name__, template_folder=template_dir)

# Substituímos a chave hardcoded para buscar do arquivo .env (com fallback de segurança)
app.secret_key = os.getenv('SECRET_KEY', 'chave_secreta_super_segura')


# ---------------------------------------------------------
# FUNÇÃO AUXILIAR: Conexão com o Banco de Dados (Protegida)
# ---------------------------------------------------------
def get_db_connection():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, '..', 'database', 'agenda.db')

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        # Registra o log técnico e retorna None para ser tratado pela rota
        logging.error(f"Erro fatal de conexão com o banco de dados: {e}")
        return None


# ---------------------------------------------------------
# FUNÇÃO AUXILIAR: Proteção de Rotas
# ---------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# ---------------------------------------------------------
# ROTA DE LOGIN (Protegida contra falhas de BD)
# ---------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()

        # Tratamento: Banco de dados inacessível
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


# ---------------------------------------------------------
# ROTA PRINCIPAL DA AGENDA (Protegida contra falhas de API)
# ---------------------------------------------------------
@app.route('/agenda')
@login_required
def agenda():
    # Substituímos a URL fixa para buscar do arquivo .env (com fallback)
    url_api = os.getenv('API_URL', 'http://127.0.0.1:5000/api/agendamentos')

    agendamentos_validados = []
    mensagem_erro = None

    try:
        # Timeout de 5 segundos para evitar travamento da tela
        resposta = requests.get(url_api, timeout=5, cookies=request.cookies)
        resposta.raise_for_status()
        dados_json = resposta.json()

        # Tratamento: Resposta Vazia ou Faltando Campos
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


# ---------------------------------------------------------
# ROTA DA API (Agora consumindo dados reais do Banco SQLite)
# ---------------------------------------------------------
@app.route('/api/agendamentos', methods=['GET'])
@login_required
def obter_agendamentos():
    conn = get_db_connection()

    # Se o banco estiver inacessível, retorna lista vazia
    if conn is None:
        return jsonify([])

    try:
        # Consulta os dados que o seed.py inseriu na tabela appointments
        # Usamos "cpf as CPF" para garantir que a chave do JSON fique em maiúsculo como o frontend espera
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
    # O host '0.0.0.0' é muito importante para rodar via Docker!
    app.run(debug=True, host='0.0.0.0')