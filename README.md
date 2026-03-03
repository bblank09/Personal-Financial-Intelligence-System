# Personal Financial Intelligence System for University Students

A production-grade financial web application for university students to track income and expenses, manage investments, and monitor financial health via AI-driven recommendations. Built with Python Flask, MySQL, MongoDB, and Tailwind CSS.

## Features
- **User Authentication:** Registration, secure login, password hashing.
- **Transaction Management:** Add, filter, edit, and soft-delete incomes/expenses.
- **Investment Tracking:** Monitor personal asset portfolio.
- **Financial Analytics Engine:** Real-time financial health score (0-100), risk levels, and smart recommendations based on spending ratio.
- **Polyglot Persistence Layer:** Uses SQLAlchemy with MySQL for transactional logic and PyMongo with MongoDB for complex financial summaries.

## Core Tech Stack
* **Backend:** Flask, Flask-SQLAlchemy, Werkzeug, PyTest
* **Databases:** MySQL 8.0 (ORM), MongoDB 6.0 (NoSQL Analytics Cache)
* **Frontend:** HTML, Tailwind CSS (via CDN), vanilla JS, Chart.js
* **DevOps:** Docker, Docker Compose

## Repository Structure Overview
Following clean architecture principles:
* `/app/routes` - Presentation API Endpoints
* `/app/services` - Business Logic Core
* `/app/models` - MySQL Entities
* `/app/mongo` - MongoDB Data Layer Layer

## Installation and Run Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd personal-financial-intelligence-system
```

### 2. Start Services via Docker Compose
This application uses Docker and Docker Compose to easily spin up the Flask web server alongside isolated MySQL and MongoDB containers hooked to an internal network.

```bash
docker-compose up -d --build
```
*Note: Wait a minute for the databases to fully initialize.*

### 3. Initialize MySQL Database Migrations
Run the initial DB creation from within your web container structure:
```bash
docker-compose exec web flask db init
docker-compose exec web flask db migrate -m "Initial Migration"
docker-compose exec web flask db upgrade
```

### 4. Access the App
Go to: [http://localhost:5001](http://localhost:5001)

## Architecture Style
Implemented using **Clean Architecture** patterns separating Route layers → Services Layers → Database Models effectively for maximum scalability. MongoDB integration works asynchronously on financial transactions caching.
# Personal-Financial-Intelligence-System
