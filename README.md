# LogicGuard

## How to Run

### Prerequisites
- Docker & Docker Compose (Recommended)
- Python 3.10+ (for manual backend)
- Node.js 18+ (for manual frontend)

### Option 1: Docker Compose (Recommended)
This will start the Database, Backend, and Frontend.

```bash
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### 1. Database
You need a PostgreSQL database running. You can use Docker for just the DB:
```bash
docker-compose up db -d
```

#### 2. Backend
Navigate to the `backend` directory:
```bash
cd backend
```

Create a virtual environment and activate it:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Setup Environment Variables:
Copy `.env.example` to `.env` and update if necessary.
```bash
cp .env.example .env
```

Run the server:
```bash
uvicorn app.main:app --reload
```
The backend will be available at `http://localhost:8000`.

#### 3. Frontend
Navigate to the `frontend` directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Run the development server:
```bash
npm run dev
```
The frontend will be available at `http://localhost:3000`.
