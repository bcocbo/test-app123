import http.client
import sys
import os

port = int(os.environ.get('PORT', 8000))

try:
    conn = http.client.HTTPConnection('localhost', port, timeout=2)
    conn.request('GET', '/health')
    response = conn.getresponse()
    
    if response.status == 200:
        print(f'✅ Health check passed: {response.status}')
        sys.exit(0)
    else:
        print(f'❌ Health check failed: {response.status}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Health check error: {e}')
    sys.exit(1)
finally:
    if 'conn' in locals():
        conn.close()
