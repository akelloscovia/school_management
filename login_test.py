import os
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))
with app.app_context():
    client = app.test_client()
    response = client.post('/api/auth/login', json={
        'email': 'admin@hilltop.com',
        'password': 'ilovehilltop'
    })
    print('status=', response.status_code)
    print(response.get_data(as_text=True))
