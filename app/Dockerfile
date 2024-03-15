FROM python:3.9.5-slim-buster

WORKDIR /app

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD . .

CMD ["python3", "app.py"]