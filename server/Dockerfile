FROM python:3.10-slim

ENV PYTHONUNBUFFERED True

ADD requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir -r /src/requirements.txt

COPY . /webapp
WORKDIR /webapp

ENV MODEL gpt-3.5-turbo
ENV PORT 8080

EXPOSE $PORT

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 server:app