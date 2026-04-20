"""Production server launcher using waitress (Windows-compatible WSGI server)."""
import os
from app import create_app
from waitress import serve

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print('智备小语 后端服务启动中...')
    print(f'监听地址: http://0.0.0.0:{port}')
    print(f'本机访问: http://localhost:{port}')
    print('按 Ctrl+C 停止服务')
    serve(app, host='0.0.0.0', port=port, threads=4)
