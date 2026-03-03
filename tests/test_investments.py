import json

def test_add_investment(client):
    client.post('/api/register', data=json.dumps({"username": "invuser1", "email": "inv1@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "inv1@example.com", "password": "pwd"}), content_type='application/json')
    
    response = client.post('/api/investments', 
        data=json.dumps({
            "symbol": "AAPL",
            "asset_name": "Apple Inc.",
            "quantity": 10.0,
            "price": 150.0,
            "purchase_date": "2024-05-01"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    assert b"Investment transaction added" in response.data

def test_get_investments_transactions(client):
    client.post('/api/register', data=json.dumps({"username": "invuser2", "email": "inv2@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "inv2@example.com", "password": "pwd"}), content_type='application/json')
    
    client.post('/api/investments', data=json.dumps({"symbol": "AAPL", "asset_name": "Apple Inc.", "quantity": 5.0, "price": 100.0, "purchase_date": "2024-05-01"}), content_type='application/json')
    client.post('/api/investments', data=json.dumps({"symbol": "VTI", "asset_name": "Vanguard Total Stock Market", "quantity": 10.0, "price": 200.0, "purchase_date": "2024-06-01"}), content_type='application/json')
    
    res = client.get('/api/investments')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert 'transactions' in data
    assert len(data['transactions']) == 2

def test_get_investment_summary_avg_price(client):
    client.post('/api/register', data=json.dumps({"username": "invuser3", "email": "inv3@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "inv3@example.com", "password": "pwd"}), content_type='application/json')
    
    # Add two transactions for AAPL to test average price
    client.post('/api/investments', data=json.dumps({"symbol": "AAPL", "asset_name": "Apple Inc.", "quantity": 10.0, "price": 100.0, "purchase_date": "2024-05-01"}), content_type='application/json')
    client.post('/api/investments', data=json.dumps({"symbol": "AAPL", "asset_name": "Apple Inc.", "quantity": 10.0, "price": 200.0, "purchase_date": "2024-06-01"}), content_type='application/json')
    
    res = client.get('/api/investments/summary')
    assert res.status_code == 200
    data = json.loads(res.data)
    
    assert 'assets' in data
    assert len(data['assets']) == 1
    
    aapl = data['assets'][0]
    assert aapl['symbol'] == "AAPL"
    assert aapl['total_quantity'] == 20.0
    assert aapl['avg_price'] == 150.0  # (10*100 + 10*200) / 20 = 150.0
    assert aapl['total_invested'] == 3000.0

def test_update_investment(client):
    client.post('/api/register', data=json.dumps({"username": "invuser4", "email": "inv4@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "inv4@example.com", "password": "pwd"}), content_type='application/json')
    
    inv_res = client.post('/api/investments', data=json.dumps({"symbol": "TSLA", "asset_name": "Tesla", "quantity": 10.0, "price": 150.0, "purchase_date": "2024-05-01"}), content_type='application/json')
    inv_id = json.loads(inv_res.data)['investment']['id']
    
    update_res = client.put(f'/api/investments/{inv_id}', 
        data=json.dumps({"price": 200.0, "quantity": 15.0}),
        content_type='application/json'
    )
    assert update_res.status_code == 200
    
    updated_inv = json.loads(update_res.data)['investment']
    assert updated_inv['price'] == 200.0
    assert updated_inv['quantity'] == 15.0

def test_delete_investment(client):
    client.post('/api/register', data=json.dumps({"username": "invuser5", "email": "inv5@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "inv5@example.com", "password": "pwd"}), content_type='application/json')
    
    inv_res = client.post('/api/investments', data=json.dumps({"symbol": "GOLD", "asset_name": "Gold", "quantity": 10.0, "price": 1000.0, "purchase_date": "2024-05-01"}), content_type='application/json')
    inv_id = json.loads(inv_res.data)['investment']['id']
    
    del_res = client.delete(f'/api/investments/{inv_id}')
    assert del_res.status_code == 200
    assert b"Investment deleted successfully" in del_res.data
    
    get_res = client.get('/api/investments')
    assert len(json.loads(get_res.data)['transactions']) == 0

def test_search_assets(client):
    client.post('/api/register', data=json.dumps({"username": "invuser6", "email": "inv6@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "inv6@example.com", "password": "pwd"}), content_type='application/json')

    res_short = client.get('/api/assets/search?q=a')
    assert res_short.status_code == 200
    assert json.loads(res_short.data) == []

    res_valid = client.get('/api/assets/search?q=apple')
    assert res_valid.status_code == 200
    data = json.loads(res_valid.data)
    assert isinstance(data, list)

def test_get_asset_price(client):
    client.post('/api/register', data=json.dumps({"username": "invuser7", "email": "inv7@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "inv7@example.com", "password": "pwd"}), content_type='application/json')

    res_missing = client.get('/api/assets/price')
    assert res_missing.status_code == 400

    res_valid = client.get('/api/assets/price?ticker=AAPL&date=2024-05-01')
    assert res_valid.status_code == 200
    data = json.loads(res_valid.data)
    assert data['ticker'] == 'AAPL'
    assert 'current_price' in data
    assert 'historical_price' in data
