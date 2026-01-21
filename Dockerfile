FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py .
COPY engagement/ ./engagement/
COPY conversations/ ./conversations/

ENV DJANGO_SETTINGS_MODULE=engagement.settings

RUN mkdir -p logs

RUN python manage.py migrate --noinput && \
    python manage.py test conversations.tests --noinput

COPY . .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]
