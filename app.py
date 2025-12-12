from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        'message': '¡Hola Mundo desde tes-app-123!',
        'description': 'Aplicación desplegada con ArgoCD y GitOps',
        'environment': 'dev',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'tes-app-123',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/info')
def info():
    return jsonify({
        'name': 'tes-app-123',
        'description': 'Aplicación desplegada con ArgoCD y GitOps',
        'environment': 'dev',
        'language': 'Python',
        'framework': 'Flask',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print('=' * 50)
    print(f'🚀 tes-app-123 iniciando...')
    print(f'📊 Entorno: dev')
    print(f'🌐 Puerto: {port}')
    print(f'✅ Health check: http://localhost:{port}/health')
    print(f'ℹ️  Info: http://localhost:{port}/info')
    print('=' * 50)
    app.run(host='0.0.0.0', port=port, debug=False)
