FROM python:3.9-slim

WORKDIR /app

COPY zhibei_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY zhibei_backend/ .

EXPOSE 5000

CMD ["python", "run_prod.py"]
