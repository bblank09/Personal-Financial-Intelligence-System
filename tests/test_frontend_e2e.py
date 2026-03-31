import pytest

# Skip all tests in this module if playwright is not installed
pytest.importorskip("playwright")

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

    server = ServerThread(app, port)
    server.start()
    time.sleep(1)

    yield f"http://127.0.0.1:{port}"

    server.shutdown()
    server.join()
    with app.app_context():
        db.drop_all()
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance", "e2e_test.db")
    if os.path.exists(db_path):
        os.remove(db_path)

# ─── Helper: Register + Login ────────────────────────────────
def _register_and_login(page, base_url, email, name):
    """Helper to register a new user and log them in."""
    page.goto(f"{base_url}/register")
    page.fill('input[name="email"]', email)
    page.fill('input[name="name"]', name)
    page.fill('input[name="password"]', 'password123')
    page.fill('input[name="confirm-password"]', 'password123')
    page.click('button[type="submit"]')
    page.wait_for_url("**/login*")

    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', 'password123')
    page.click('button[type="submit"]')
    page.wait_for_url("**/")


# ═══════════════════════════════════════════════════════════════
#  1. Authentication Tests (Register / Login / Logout)
# ═══════════════════════════════════════════════════════════════

def test_register_page_renders(live_server, page):
    """ทดสอบว่าหน้าสมัครสมาชิกแสดงผลได้ถูกต้อง"""
    page.goto(f"{live_server}/register")
    assert "Create Account" in page.content()
    assert page.locator('input[name="email"]').is_visible()
    assert page.locator('input[name="name"]').is_visible()
    assert page.locator('input[name="password"]').is_visible()
    assert page.locator('input[name="confirm-password"]').is_visible()

def test_login_page_renders(live_server, page):
    """ทดสอบว่าหน้าเข้าสู่ระบบแสดงผลได้ถูกต้อง"""
    page.goto(f"{live_server}/login")
    assert "Sign In" in page.content()
    assert page.locator('input[name="email"]').is_visible()
    assert page.locator('input[name="password"]').is_visible()

def test_register_and_login_flow(live_server, page):
    """ทดสอบการสมัครสมาชิกแล้วเข้าสู่ระบบสำเร็จ"""
    _register_and_login(page, live_server, "flow1@test.com", "Flow User")
    content = page.content()
    assert "Financial Insights" in content or "Dashboard" in content

def test_login_wrong_password(live_server, page):
    """ทดสอบว่าเข้าสู่ระบบด้วยรหัสผ่านผิดจะไม่ redirect"""
    page.goto(f"{live_server}/register")
    page.fill('input[name="email"]', "wrongpw@test.com")
    page.fill('input[name="name"]', "Wrong PW")
    page.fill('input[name="password"]', "password123")
    page.fill('input[name="confirm-password"]', "password123")
    page.click('button[type="submit"]')
    page.wait_for_url("**/login*")

    page.fill('input[name="email"]', "wrongpw@test.com")
    page.fill('input[name="password"]', "WRONGPASSWORD")
    page.click('button[type="submit"]')

    # Should stay on login page
    page.wait_for_timeout(2000)
    assert "/login" in page.url or "Sign In" in page.content()

def test_register_duplicate_email(live_server, page):
    """ทดสอบว่าสมัครด้วย email ซ้ำจะยังอยู่หน้า register"""
    page.goto(f"{live_server}/register")
    page.fill('input[name="email"]', "flow1@test.com")  # already registered above
    page.fill('input[name="name"]', "Dup User")
    page.fill('input[name="password"]', "password123")
    page.fill('input[name="confirm-password"]', "password123")
    page.click('button[type="submit"]')

    page.wait_for_timeout(2000)
    assert "/register" in page.url or "Create Account" in page.content()


# ═══════════════════════════════════════════════════════════════
#  2. Dashboard Tests
# ═══════════════════════════════════════════════════════════════

def test_dashboard_renders_cards(live_server, page):
    """ทดสอบว่า Dashboard แสดง Summary Cards ครบ (Income, Expense, Saving Rate, Health Score)"""
    _register_and_login(page, live_server, "dash1@test.com", "Dash User")

    assert page.locator("#dash-income").is_visible()
    assert page.locator("#dash-expense").is_visible()
    assert page.locator("#dash-saving-rate").is_visible()
    assert page.locator("#dash-health-score").is_visible()

def test_dashboard_sidebar_navigation(live_server, page):
    """ทดสอบว่า Sidebar มีลิงก์ไปทุกหน้า"""
    _register_and_login(page, live_server, "nav1@test.com", "Nav User")

    assert page.locator('a[href="/"]').first.is_visible()
    assert page.locator('a[href="/transactions"]').first.is_visible()
    assert page.locator('a[href="/investments"]').first.is_visible()
    assert page.locator('a[href="/analytics"]').first.is_visible()

def test_dashboard_has_charts(live_server, page):
    """ทดสอบว่า Dashboard มี Canvas สำหรับกราฟ"""
    _register_and_login(page, live_server, "chart1@test.com", "Chart User")

    assert page.locator("#cashflowChart").is_visible() or page.locator("#cashflowChart").count() > 0
    assert page.locator("#expenseChart").count() > 0

def test_dashboard_smart_insights(live_server, page):
    """ทดสอบว่า Dashboard มีส่วน Smart Insights"""
    _register_and_login(page, live_server, "insight1@test.com", "Insight User")

    assert page.locator("#dash-recommendations").count() > 0
    assert "Smart Insights" in page.content()


# ═══════════════════════════════════════════════════════════════
#  3. Transactions Page Tests
# ═══════════════════════════════════════════════════════════════

def test_transactions_page_renders(live_server, page):
    """ทดสอบว่าหน้า Transactions แสดงผลพร้อมตาราง, filter, ปุ่ม Add"""
    _register_and_login(page, live_server, "tx1@test.com", "TX User")
    page.goto(f"{live_server}/transactions")

    assert "Transactions" in page.content()
    assert page.locator("#transactionTableBody").count() > 0
    assert page.locator("#monthFilter").is_visible()
    assert page.locator("#typeFilter").is_visible()

def test_transactions_add_modal(live_server, page):
    """ทดสอบว่าปุ่ม Add Transaction เปิด Modal ได้"""
    _register_and_login(page, live_server, "tx2@test.com", "TX Modal")
    page.goto(f"{live_server}/transactions")

    page.click("text=Add Transaction")
    page.wait_for_timeout(500)

    assert page.locator("#txModal").is_visible()
    assert page.locator("#txType").is_visible()
    assert page.locator("#txAmount").is_visible()
    assert page.locator("#txCategory").is_visible()
    assert page.locator("#txDate").is_visible()


# ═══════════════════════════════════════════════════════════════
#  4. Investments Page Tests
# ═══════════════════════════════════════════════════════════════

def test_investments_page_renders(live_server, page):
    """ทดสอบว่าหน้า Investments แสดง Summary Cards, ตาราง Portfolio, ตาราง Transaction History"""
    _register_and_login(page, live_server, "inv1@test.com", "Inv User")
    page.goto(f"{live_server}/investments")

    assert "Investments" in page.content()
    assert page.locator("#totalInvestmentCard").count() > 0
    assert page.locator("#portfolioValueCard").count() > 0
    assert page.locator("#profitCard").count() > 0
    assert page.locator("#portfolioTableBody").count() > 0
    assert page.locator("#investmentTableBody").count() > 0

def test_investments_add_modal(live_server, page):
    """ทดสอบว่าปุ่ม Add Investment เปิด Modal ได้"""
    _register_and_login(page, live_server, "inv2@test.com", "Inv Modal")
    page.goto(f"{live_server}/investments")

    page.click("text=Add Investment")
    page.wait_for_timeout(500)

    modal = page.locator("#investmentModal")
    assert "opacity-0" not in (modal.get_attribute("class") or "")
    assert page.locator("#invSymbol").is_visible()
    assert page.locator("#invName").is_visible()
    assert page.locator("#invQuantity").is_visible()
    assert page.locator("#invPrice").is_visible()
    assert page.locator("#invDate").is_visible()

def test_investments_has_charts(live_server, page):
    """ทดสอบว่าหน้า Investments มี Canvas สำหรับกราฟ Allocation & Performance"""
    _register_and_login(page, live_server, "inv3@test.com", "Inv Chart")
    page.goto(f"{live_server}/investments")

    assert page.locator("#portfolioChart").count() > 0
    assert page.locator("#performanceChart").count() > 0


# ═══════════════════════════════════════════════════════════════
#  5. Analytics (Forecasting) Page Tests
# ═══════════════════════════════════════════════════════════════

def test_analytics_page_renders(live_server, page):
    """ทดสอบว่าหน้า Analytics แสดงผลพร้อมหัวข้อ Financial Forecasting"""
    _register_and_login(page, live_server, "ana1@test.com", "Ana User")
    page.goto(f"{live_server}/analytics")

    assert "Financial Forecasting" in page.content()

def test_analytics_has_forecast_elements(live_server, page):
    """ทดสอบว่า Analytics มี element สำหรับ Forecast Cards"""
    _register_and_login(page, live_server, "ana2@test.com", "Ana Elem")
    page.goto(f"{live_server}/analytics")

    assert page.locator("#forecastingSection").count() > 0
    assert page.locator("#monthlyForecastCard").count() > 0
    assert page.locator("#balanceProjectionCard").count() > 0
    assert page.locator("#investmentProjectionCard").count() > 0


# ═══════════════════════════════════════════════════════════════
#  6. Page Protection (Unauthenticated Access)
# ═══════════════════════════════════════════════════════════════

def test_unauthenticated_dashboard_redirect(live_server, page):
    """ทดสอบว่าเข้าหน้า Dashboard โดยไม่ login จะไม่เห็น Dashboard"""
    page.goto(f"{live_server}/")
    content = page.content()
    # Should see login page or no dashboard content
    assert "Sign In" in content or "login" in page.url

def test_unauthenticated_transactions_redirect(live_server, page):
    """ทดสอบว่าเข้าหน้า Transactions โดยไม่ login จะถูกป้องกัน"""
    page.goto(f"{live_server}/transactions")
    content = page.content()
    assert "Sign In" in content or "login" in page.url
