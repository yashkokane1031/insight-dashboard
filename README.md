# InSight - Real-Time Analytics Dashboard

![Image](https://github.com/user-attachments/assets/a1a9442f-3d41-4fb7-aa8c-fe885d51c9b3)

> **Production-Grade** real-time analytics platform with WebSocket streaming, ML forecasting, and heavy-load simulation capabilities.

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Authentication** | JWT-based login with bcrypt password hashing |
| ⚡ **WebSocket Real-Time** | Instant data streaming without polling |
| 🤖 **ML Forecasting** | Polynomial regression predictions with anomaly detection |
| 📊 **Live Visualizations** | Chart.js with predicted vs actual overlays |
| 🚀 **Load Tested** | Proven at 1000+ writes/sec with TimescaleDB |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React, TypeScript, Vite, Chart.js, WebSocket API |
| **Backend** | Python, FastAPI, WebSockets, Scikit-Learn |
| **Database** | PostgreSQL + TimescaleDB |
| **DevOps** | Docker Compose |
| **Auth** | JWT, Passlib (bcrypt) |

---

## 🚀 Quick Start

```bash
# 1. Start the database
docker compose up -d

# 2. Start the backend
cd InSight && uvicorn InSight.main:app --reload

# 3. Start the frontend
cd frontend-react && npm run dev

# 4. Generate test data
python simulator.py
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/token` | POST | Login, returns JWT |
| `/data/` | POST | Insert data point (broadcasts to WebSocket) |
| `/data/latest` | GET | Get latest data point |
| `/data/history` | GET | Get last 30 data points |
| `/data/forecast` | GET | ML predictions + anomalies |
| `/ws?token=<jwt>` | WS | Real-time data stream |

---

## 🧪 Load Testing

```bash
python data_generator.py --sensors 1000 --batch-size 100 --duration 60
```

**Results:** Sustained **995+ writes/sec** to TimescaleDB.

---

## 📁 Project Structure

```
InSight/
├── InSight/                    # Backend (FastAPI)
│   ├── main.py                 # API endpoints + WebSocket
│   ├── websocket_manager.py    # Connection manager
│   ├── ml_forecaster.py        # ML predictions
│   ├── models.py               # SQLAlchemy models
│   └── auth.py                 # JWT authentication
├── frontend-react/             # Frontend (React + Vite)
│   └── src/
│       ├── context/
│       │   ├── AuthContext.tsx
│       │   └── WebSocketContext.tsx
│       └── components/
│           ├── LineChart.tsx   # Chart with forecast
│           └── RealtimeValue.tsx
├── data_generator.py           # Heavy load simulator
├── simulator.py                # Basic data simulator
└── docker-compose.yml          # TimescaleDB container
```

---

## 👨‍💻 Author

Built as a hands-on learning experience in full-stack development, system architecture, and real-time data engineering.
