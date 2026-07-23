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
            ('Maria Souza', '555.666.777-88', 'Dra. Ana', 'Dermatologia', '2026-07-26', '14:30', 'Amil', 'Pendente'),
            ('Carlos Eduardo', '222.333.444-55', 'Dr. Roberto', 'Ortopedia', '2026-07-27', '09:15', 'Bradesco Saúde',
             'Confirmado'),
            ('Ana Clara', '333.444.555-66', 'Dra. Beatriz', 'Pediatria', '2026-07-27', '11:00', 'SulAmérica',
             'Cancelado'),
            ('Marcos Paulo', '444.555.666-77', 'Dr. Carlos', 'Cardiologia', '2026-07-28', '15:45', 'Unimed',
             'Pendente'),
            ('Juliana Costa', '666.777.888-99', 'Dra. Fernanda', 'Ginecologia', '2026-07-29', '08:30', 'Amil',
             'Confirmado'),
            ('Rafael Gomes', '777.888.999-00', 'Dr. João', 'Clínico Geral', '2026-07-30', '13:20', 'Particular',
             'Pendente'),
            ('Patrícia Lima', '888.999.000-11', 'Dra. Ana', 'Dermatologia', '2026-07-31', '16:00', 'Bradesco Saúde',
             'Confirmado'),
            ('Lucas Ferreira', '999.000.111-22', 'Dr. Roberto', 'Ortopedia', '2026-08-01', '10:30', 'Unimed',
             'Confirmado'),
            ('Camila Alves', '000.111.222-33', 'Dra. Beatriz', 'Pediatria', '2026-08-02', '14:00', 'Particular',
             'Confirmado')
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