# คู่มือการรันโปรเจกต์ Personal Financial Intelligence System (PFIS)

โปรเจกต์นี้รองรับการรันทั้งแบบ **Docker** (แนะนำเพราะจัดการฐานข้อมูลให้ครบ) และแบบ **Local (Virtual Environment)** สำหรับการพัฒนาครับ

---

## ส่วนที่ 1: การรันผ่าน Docker (วิธีที่ง่ายที่สุด)

วิธีนี้จะเตรียมทั้ง Web Server, MySQL และ MongoDB ให้โดยอัตโนมัติ

1. **เตรียมไฟล์ .env**: ตรวจสอบให้มั่นใจว่ามีไฟล์ `.env` ในโฟลเดอร์หลัก (Root) พร้อมกำหนดค่าต่างๆ เช่น `SECRET_KEY`, `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD` เป็นต้น
2. **รันคำสั่ง Docker Compose**:
   ```bash
   docker-compose up -d --build
   ```
3. **เริ่มต้นฐานข้อมูล MySQL (Migration)**:
   *เฉพาะการรันครั้งแรก* ต้องรันคำสั่งเพื่อสร้าง Table ใน MySQL:
   ```bash
   docker-compose hexec web flask db init
   docker-compose hexec web flask db migrate -m "Initial Migration"
   docker-compose hexec web flask db upgrade
   ```
4. **ใช้งานแอปพลิเคชัน**:
   เปิดบราวเซอร์ไปที่ [http://localhost:5001](http://localhost:5001)

---

## ส่วนที่ 2: การรันแบบ Local (สำหรับพัฒนาโค้ด)

หากต้องการรันบนเครื่องโดยตรง (ต้องรัน MySQL และ MongoDB แยกต่างหาก หรือใช้จาก Docker)

1. **สร้างและเปิดใช้งาน Virtual Environment**:
   ```bash
   # สำหรับ MacOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # สำหรับ Windows
   python -m venv venv
   venv\Scripts\activate
   ```
2. **ติดตั้ง Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **ติดตั้งเบราว์เซอร์สำหรับ Frontend Testing (Playwright)**:
   ```bash
   playwright install chromium
   ```
4. **ตรวจสอบฐานข้อมูล**:
   * ตรวจสอบว่า MySQL และ MongoDB กำลังทำงานอยู่ (สามารถรันเฉพาะ DB ผ่าน Docker ได้ด้วย `docker-compose up -d mysql mongo`)
5. **รันคำสั่งเริ่มต้นฐานข้อมูล (หากยังไม่ได้ทำ)**:
   ```bash
   flask db init
   flask db migrate -m "Initial Migration"
   flask db upgrade
   ```
6. **รันแอปพลิเคชัน**:
   ```bash
   python run.py
   ```
   เปิดบราวเซอร์ไปที่ [http://localhost:5000](http://localhost:5000)

---

## ส่วนที่ 3: การรันหน่วยทดสอบ (Automated Testing)

ในโปรเจกต์นี้มีทั้ง Backend และ Frontend Tests ซึ่งสามารถรันได้ง่ายๆ ดังนี้:

### 1. รันการทดสอบทั้งหมด (Backend + Frontend)
```bash
pytest
```
*หมายเหตุ: ระบบจะใช้ `pytest.ini` ที่ผมตั้งค่าไว้ให้ เพื่อดึง Path โฟลเดอร์ `app` มาใช้งานโดยอัตโนมัติ*

### 2. รันเฉพาะ Backend Tests
```bash
pytest tests/test_auth.py tests/test_investments.py ...
```

### 3. รันเฉพาะ Frontend (E2E) Tests
```bash
pytest tests/test_frontend_e2e.py -v -s
```
*ระบบจะเปิด Browser (Headless) เพื่อจำลองการคลิกใช้งานจริงให้ครับ*

---

## สรุปคำสั่งที่ใช้งานบ่อย (Cheat Sheet)

* **รันแอป (Docker):** `docker-compose up -d`
* **หยุดแอป (Docker):** `docker-compose down`
* **ดู Log (Docker):** `docker-compose logs -f web`
* **รัน Test:** `pytest`
* **ติดตั้ง Lib ใหม่:** `pip install <package-name> && pip freeze > requirements.txt`
