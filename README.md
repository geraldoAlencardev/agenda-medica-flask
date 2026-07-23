# 🏥 Agenda Médica - Desafio Técnico

## 📖 Descrição Breve da Solução
Este projeto é uma aplicação web para visualização e gerenciamento de uma Agenda Médica. O sistema conta com uma área restrita (autenticação de usuários), uma API interna RESTful e uma interface fluida que consome esses dados. O grande foco da aplicação é a **resiliência (Graceful Degradation)**: o sistema foi arquitetado para tratar falhas de comunicação, indisponibilidade de banco de dados e dados inconsistentes sem quebrar a experiência do usuário final.

## 🛠️ Tecnologias Utilizadas
* **Backend:** Python 3.10, Flask (Framework Web)
* **Banco de Dados:** SQLite (com bibliotecas nativas do Python)
* **Integração HTTP:** Biblioteca `requests`
* **Frontend:** HTML5, CSS3, JavaScript e biblioteca **Tabulator.js** (via CDN)
* **Segurança:** `werkzeug.security` (Hash de senhas) e variáveis de ambiente (`python-dotenv`)
* **Testes:** `pytest` e `unittest.mock`
* **Infraestrutura:** Docker e Docker Compose

## 🚀 Instruções para Executar o Projeto com Docker

O projeto foi empacotado para rodar facilmente através de containers. 

1. Certifique-se de ter o **Docker** e o **Docker Compose** instalados em sua máquina.
2. Clone o repositório e abra o terminal na pasta raiz do projeto.
3. Execute o comando abaixo para construir a imagem e subir a aplicação:
   ```bash
   docker-compose up --build
