import pytest
import requests
from unittest.mock import MagicMock, patch
import sys
import os

# Garante que o Python reconheça a pasta raiz do projeto para encontrar o módulo 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importamos a nossa aplicação Flask para dentro do ambiente de testes
from app.app import app

# ---------------------------------------------------------
# FIXTURE: Cliente de Teste do Flask
# ---------------------------------------------------------
@pytest.fixture
def client():
    # Ativa o modo de testes do Flask (desabilita captura de erros para debug)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('app.app.get_db_connection')
def test_login_invalido(mock_get_db, client):
    # Simulamos a conexão com o banco
    mock_conn = MagicMock()

    mock_conn.execute.return_value.fetchone.return_value = None
    mock_get_db.return_value = mock_conn

    # Enviamos uma requisição POST com credenciais fictícias
    resposta = client.post('/login', data={'username': 'admin_errado', 'password': '123'})

    # A tela deve carregar sem quebrar (Status 200 OK)
    assert resposta.status_code == 200
    # A mensagem flash do Flask de erro deve estar presente no HTML (em bytes)
    assert b'Credenciais inv\xc3\xa1lidas' in resposta.data


@patch('app.app.requests.get')
def test_falha_api_agenda(mock_requests_get, client):

    with client.session_transaction() as session:
        session['user_id'] = 1

    mock_requests_get.side_effect = requests.exceptions.Timeout

    resposta = client.get('/agenda')

    # O nosso bloco try/except no backend impediu o sistema de quebrar (Status 200 OK)
    assert resposta.status_code == 200
    # A mensagem amigável que definimos foi enviada para o frontend renderizar
    assert b'N\xc3\xa3o foi poss\xc3\xadvel carregar a agenda no momento' in resposta.data