from fastapi.testclient import TestClient
from App.main import app

client = TestClient(app)

r = client.post('/register', json={"username": "adm","email": "adm@x.test","password": "pass123","role": "admin"})
print('status', r.status_code)
print('body', r.text)
print('json', None)
try:
    print(r.json())
except Exception as e:
    print('json error', e)
