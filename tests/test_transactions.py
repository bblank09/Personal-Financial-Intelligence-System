import json

def test_add_transaction(client):
    # Setup user and login
    client.post('/api/register', data=json.dumps({"username": "txuser", "email": "tx@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "tx@example.com", "password": "pwd"}), content_type='application/json')
    
    response = client.post('/api/transactions', 
        data=json.dumps({
            "type": "income",
            "amount": 1000.0,
            "category": "Salary",
            "date": "2024-05-01",
            "note": "Initial salary"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    assert b"Transaction added" in response.data

def test_delete_transaction(client):
    client.post('/api/register', data=json.dumps({"username": "txuser2", "email": "tx2@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "tx2@example.com", "password": "pwd"}), content_type='application/json')
    
    # Add a transaction
    tx_res = client.post('/api/transactions', 
        data=json.dumps({"type": "expense", "amount": 100.0, "category": "Food", "date": "2024-05-02"}),
        content_type='application/json'
    )
    tx_data = json.loads(tx_res.data)
    tx_id = tx_data['transaction']['id']
    
    # Delete it
    del_res = client.delete(f'/api/transactions/{tx_id}')
    assert del_res.status_code == 200
    assert b"Transaction deleted successfully" in del_res.data

def test_filter_transactions(client):
    client.post('/api/register', data=json.dumps({"username": "txuser3", "email": "tx3@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "tx3@example.com", "password": "pwd"}), content_type='application/json')
    
    # Add multiple transactions
    client.post('/api/transactions', data=json.dumps({"type": "expense", "amount": 50.0, "category": "Food", "date": "2024-05-02"}), content_type='application/json')
    client.post('/api/transactions', data=json.dumps({"type": "income", "amount": 2000.0, "category": "Salary", "date": "2024-05-05"}), content_type='application/json')
    client.post('/api/transactions', data=json.dumps({"type": "expense", "amount": 150.0, "category": "Transport", "date": "2024-06-10"}), content_type='application/json')
    
    # Test month filter
    res_month = client.get('/api/transactions?month=2024-05')
    assert len(json.loads(res_month.data)['transactions']) == 2
    
    # Test type filter
    res_type = client.get('/api/transactions?type=income')
    assert len(json.loads(res_type.data)['transactions']) == 1
    assert json.loads(res_type.data)['transactions'][0]['category'] == 'Salary'
    
    # Test category filter
    res_cat = client.get('/api/transactions?category=Food')
    assert len(json.loads(res_cat.data)['transactions']) == 1
    assert json.loads(res_cat.data)['transactions'][0]['amount'] == 50.0

def test_update_transaction(client):
    client.post('/api/register', data=json.dumps({"username": "txuser4", "email": "tx4@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "tx4@example.com", "password": "pwd"}), content_type='application/json')
    
    # Add a transaction
    tx_res = client.post('/api/transactions', 
        data=json.dumps({"type": "expense", "amount": 100.0, "category": "Food", "date": "2024-05-02"}),
        content_type='application/json'
    )
    tx_id = json.loads(tx_res.data)['transaction']['id']
    
    # Update it
    update_res = client.put(f'/api/transactions/{tx_id}', 
        data=json.dumps({"amount": 120.0, "category": "Dining Out", "date": "2024-05-03"}),
        content_type='application/json'
    )
    assert update_res.status_code == 200
    
    updated_tx = json.loads(update_res.data)['transaction']
    assert updated_tx['amount'] == 120.0
    assert updated_tx['category'] == 'Dining Out'
    assert updated_tx['date'] == '2024-05-03'


def test_add_transaction_without_login(client):
    response = client.post('/api/transactions',
        data=json.dumps({"type": "income", "amount": 1000.0, "category": "Salary", "date": "2024-05-01"}),
        content_type='application/json'
    )
    assert response.status_code == 401


def test_delete_nonexistent_transaction(client):
    client.post('/api/register', data=json.dumps({"username": "txuser5", "email": "tx5@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "tx5@example.com", "password": "pwd"}), content_type='application/json')

    response = client.delete('/api/transactions/99999')
    assert response.status_code == 404
    assert b"Transaction not found" in response.data


def test_get_transactions_empty(client):
    client.post('/api/register', data=json.dumps({"username": "txuser6", "email": "tx6@example.com", "password": "pwd"}), content_type='application/json')
    client.post('/api/login', data=json.dumps({"email": "tx6@example.com", "password": "pwd"}), content_type='application/json')

    response = client.get('/api/transactions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['transactions'] == []
