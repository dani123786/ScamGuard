from app import app 
client=app.test_client() 
print(client.post('/api/check/url', json={'url':'https://paypal.com/login'}).get_json()) 
print(client.post('/api/check', json={'type':'message','content':'Your account is suspended. Click this link and verify your bank details immediately.'}).get_json()) 
