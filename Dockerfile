FROM python:3.6-slim

WORKDIR /usr/src/cnc-motor-control

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]