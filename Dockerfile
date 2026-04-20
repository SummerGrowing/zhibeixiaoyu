# Deploy v8
FROM python:3.9

WORKDIR /app

# 复制并安装后端依赖
COPY zhibei_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY zhibei_backend/ .

# 复制前端文件（app.py 需要它）
COPY zhibei_frontend/ /app/zhibei_frontend/

# 设置前端目录环境变量
ENV FRONTEND_DIR=/app/zhibei_frontend

EXPOSE 5000

ENTRYPOINT ["python", "run_prod.py"]
