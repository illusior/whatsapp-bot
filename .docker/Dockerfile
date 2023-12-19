FROM python:3.10-alpine as app

WORKDIR /app

COPY ./ ./

RUN pip3 install -r requirements.txt --no-cache-dir

CMD python3 src/run.py && python3 src/manage.py runserver 0.0.0.0:8080
