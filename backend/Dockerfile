FROM python:3.9.18

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY .. .

ENV DJANGO_SETTINGS_MODULE=foodgram.settings

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]