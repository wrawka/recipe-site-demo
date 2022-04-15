FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements/common.txt --no-cache-dir

CMD ["gunicorn", "config.wsgi:application", "--bind", ":8000"]