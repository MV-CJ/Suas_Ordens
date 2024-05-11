# Use a imagem oficial do Python
FROM python:3.8-slim

# Instala dependências de compilação do PostgreSQL e do wkhtmltopdf
RUN apt-get update && \
    apt-get install -y libpq-dev wkhtmltopdf

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências
RUN pip install -r requirements.txt

# Copie o restante do código para o diretório de trabalho
COPY . .

# Exponha a porta em que a aplicação Flask irá rodar
EXPOSE 5000

# Comando para executar a aplicação quando o contêiner for iniciado
CMD ["python", "run.py"]
