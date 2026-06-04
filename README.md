# ApexPOS - Point of Sale (POS) Enterprise System

A high-performance, modern Point of Sale (POS) system designed with **Vue 3 (Vite + Pinia)** on the frontend, **Flask (Python 3.11)** on the backend, and powered by **PostgreSQL** (persistent transactional storage) and **Redis** (session caching, suspended checkouts, and event publishing).

---

## Tech Stack Overview

- **Frontend**: Vue.js 3, Vue Router, Pinia (State Management), Axios.
- **Backend**: Flask, Flask-SQLAlchemy (ORM), Flask-Migrate (Alembic Migrations), Flask-JWT-Extended (JWT Token Authentication), Flask-Cors.
- **Databases**: PostgreSQL (Relational DB for products, users, customers, sales ledger) + Redis (In-memory store for holding suspended orders/carts, API cache, and Pub/Sub).
- **Environment**: Containerized using Docker & Docker Compose.

---

## Directory Structure

```text
D:/ERP/POS/
├── README.md                    # Project documentation
├── docker-compose.yml           # Local orchestration for dev services
├── backend/                     # Python Flask backend
│   ├── run.py                   # Dev server entrypoint
│   ├── seed.py                  # Database table seeding script
│   ├── requirements.txt         # Python package dependencies
│   ├── Dockerfile               # Backend container containerization
│   ├── app/                     # Flask MVC source code
│   │   ├── config.py            # Global environmental config
│   │   ├── extensions.py        # Extensions bindings (SQLAlchemy, Redis, JWT)
│   │   ├── models/              # PostgreSQL tables schemas
│   │   ├── routes/              # Blueprint endpoints (REST controllers)
│   │   └── services/            # Business layer (Checkout transaction pipeline)
│   └── tests/                   # Python unittest module suite
└── frontend/                    # Vue SPA frontend
    ├── package.json             # NPM package scripts & dependencies
    ├── vite.config.js           # Vite builder rules & API Proxy rules
    ├── Dockerfile               # Frontend container containerization
    └── src/                     # Vue assets, store definitions, routing, and views
```

---

## Quick Start (Using Docker Compose)

The easiest way to start the entire system (Database, Cache, Backend, and Frontend) is using Docker Compose:

1. **Build and start the containers**:
   ```bash
   docker-compose up --build -d
   ```

2. **Seed the database**:
   Once the containers are up and running, seed the PostgreSQL database with default products, categories, loyalty customers, and Cashier accounts:
   ```bash
   docker-compose exec backend python seed.py
   ```

3. **Access the applications**:
   - **Frontend (POS Terminal)**: Open [http://localhost:5173](http://localhost:5173) in your browser.
   - **Backend API Docs/Health Check**: Visit [http://localhost:5000/health](http://localhost:5000/health).

4. **Default Login Credentials**:
   - **Username**: `admin`
   - **Password**: `securepassword`

---

## Local Development (Without Docker)

If you prefer to run services natively on your host computer:

### 1. Database & Cache Services
Ensure you have **PostgreSQL** running on port `5432` and **Redis** running on port `6379`.
- Create a Postgres database named `pos_db`.

### 2. Run the Backend API
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python seed.py
python run.py
```
*The backend API will run on `http://127.0.0.1:5000`.*

### 3. Run the Frontend Vue SPA
```bash
cd frontend
npm install
npm run dev
```
*The frontend dev server will start on `http://localhost:5173` and proxy requests under `/api` to the backend.*
