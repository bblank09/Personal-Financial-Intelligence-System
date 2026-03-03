import urllib.request, json
try:
    req = urllib.request.Request('http://localhost:5001/api/login', data=json.dumps({'email':'tx@example.com', 'password':'pwd'}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as resp:
        cookie = resp.headers.get('Set-Cookie')
        print('Login success:', resp.getcode())
        
        req2 = urllib.request.Request('http://localhost:5001/api/investments', data=json.dumps({'asset_name':'ETH', 'asset_type':'Crypto', 'quantity': 0.1, 'amount':300.0, 'current_value':None, 'purchase_date':'2024-05-01'}).encode('utf-8'), headers={'Content-Type': 'application/json', 'Cookie': cookie}, method='POST')
        with urllib.request.urlopen(req2) as r2:
            print('Insert investment:', r2.getcode(), r2.read().decode('utf-8'))
except Exception as e:
    print('Error:', getattr(e, 'read', lambda: str(e))())
