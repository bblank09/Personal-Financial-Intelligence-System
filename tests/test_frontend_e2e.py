import pytest
from app import create_app
from app.extensions import db
from app.config import Config
from werkzeug.serving import make_server
import threading
import time

class TestConfigE2E(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///e2e_test.db'
    WTF_CSRF_ENABLED = False
    MONGO_URI = 'mongodb://mongo:27017/test_finance_db_e2e'
    # SERVER_NAME is usually required for url_for to work outside request context, 
    # but since Werkzeug test server binds to localhost, leaving it unset works fine for relative paths.

class ServerThread(threading.Thread):
    def __init__(self, app, port):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()
        self.ctx.pop()

@pytest.fixture(scope="module")
def live_server():
    app = create_app(TestConfigE2E)
    port = 8999
    with app.app_context():
        db.create_all()
        # Clean any existing users from mongo mock if it fails
        
    server = ServerThread(app, port)
    server.start()
    
    time.sleep(1) # Wait for server
    
    yield f"http://127.0.0.1:{port}"
    
    server.shutdown()
    server.join()
    with app.app_context():
        db.drop_all()
    import os
    if os.path.exists("e2e_test.db"):
        os.remove("e2e_test.db")

def test_login_and_dashboard(live_server, page):
    # 1. Register
    page.goto(f"{live_server}/register")
    page.fill('input[name="email"]', 'e2e1@example.com')
    page.fill('input[name="name"]', 'e2e_user1')
    page.fill('input[name="password"]', 'password123')
    page.fill('input[name="confirm-password"]', 'password123')
    page.click('button[type="submit"]')
    
    page.wait_for_url("**/login*")
    
    # 2. Login
    page.fill('input[name="email"]', 'e2e1@example.com')
    page.fill('input[name="password"]', 'password123')
    page.click('button[type="submit"]')
    
    page.wait_for_url("**/dashboard*")
    assert "Overview" in page.content() or "Dashboard" in page.title()

def test_investments_page(live_server, page):
    # 3. Another user for investments isolated
    page.goto(f"{live_server}/register")
    page.fill('input[name="email"]', 'e2e2@example.com')
    page.fill('input[name="name"]', 'e2e_user2')
    page.fill('input[name="password"]', 'password123')
    page.fill('input[name="confirm-password"]', 'password123')
    page.click('button[type="submit"]')
    
    page.wait_for_url("**/login*")
    page.fill('input[name="email"]', 'e2e2@example.com')
    page.fill('input[name="password"]', 'password123')
    page.click('button[type="submit"]')
    page.wait_for_url("**/dashboard*")
    
    # 4. Navigate to investments
    page.goto(f"{live_server}/investments")
    page.wait_for_url("**/investments*")
    assert "Investments" in page.title()
