import sqlite3
import os
from werkzeug.security import generate_password_hash

# Define o caminho onde o arquivo do banco de dados será salvo
# Isso garante que ele fique dentro da pasta /database que você criou
DB_PATH = os.path.join('database', 'agenda.db')

def criar_banco_de_dados():
    # Conecta ao banco (se o arquivo agenda.db não existir, ele será criado automaticamente)
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    # 1. Criação da tabela de Usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')

    # 2. Criação da tabela de Agendamentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente TEXT NOT NULL,
        cpf TEXT NOT NULL,
        medico TEXT NOT NULL,
        especialidade TEXT NOT NULL,
        data TEXT NOT NULL,
        horario TEXT NOT NULL,
        convenio TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')

    # 3. Inserindo o usuário de teste (admin / admin123)
    # Verifica se o usuário já existe para evitar duplicação caso rode o script mais de uma vez
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        senha_criptografada = generate_password_hash('admin123')
        cursor.execute('''
        INSERT INTO users (username, password_hash) VALUES (?, ?)
        ''', ('admin', senha_criptografada))

    # 4. Inserindo agendamentos fictícios para testes
    cursor.execute('SELECT count(*) FROM appointments')
    if cursor.fetchone()[0] == 0:  # Só insere se a tabela estiver vazia
        agendamentos = [
            ('João Silva', '111.222.333-44', 'Dr. Carlos', 'Cardiologia', '2026-07-25', '10:00', 'Unimed', 'Confirmado'),
            ('Maria Souza', '555.666.777-88', 'Dra. Ana', 'Dermatologia', '2026-07-26', '14:30', 'Amil', 'Pendente')
        ]
        cursor.executemany('''
        INSERT INTO appointments (paciente, cpf, medico, especialidade, data, horario, convenio, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', agendamentos)

    # Salva as alterações e fecha a conexão
    conexao.commit()
    conexao.close()
    print("Banco de dados 'agenda.db' criado e populado com sucesso na pasta /database!")

if __name__ == '__main__':
    criar_banco_de_dados()