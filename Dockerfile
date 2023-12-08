FROM python:3.6-slim

WORKDIR /app

COPY requirements.txt ./
# Copia los archivos locales al contenedor en /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "main.py" ]