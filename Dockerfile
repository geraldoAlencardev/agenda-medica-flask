# Usa uma imagem oficial e leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas o arquivo de dependências primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do projeto para dentro do container
COPY . .

# Expõe a porta 5000, que é a porta padrão do Flask
EXPOSE 5000

# Define a variável de ambiente nativa do Flask para dizer onde está o app
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Comando final para rodar a aplicação quando o container iniciar
CMD ["flask", "run"]