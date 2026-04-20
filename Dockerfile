# Deploy v5
FROM python:3.9-slim

WORKDIR /app

COPY zhibei_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY zhibei_backend/ .

RUN chmod +x start.sh

EXPOSE 5000

ENTRYPOINT ["/app/start.sh"]
