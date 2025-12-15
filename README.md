# Project Kite-X

A pixel-perfect clone of the Zerodha Kite trading platform with advanced algorithmic scanning capabilities for the Indian Stock Market (NSE/BSE).

## Features
- Real-time stock data visualization
- Advanced RVOL (Relative Volume) scanner
- Paper trading functionality
- Interactive charts with multiple timeframes
- Dark mode financial dashboard

## Tech Stack
- Frontend: React.js (Vite) with Tailwind CSS
- Backend: Python FastAPI
- Data: yfinance for market data
- Charts: TradingView Lightweight Charts

## Folder Structure
```
/workspace/
├── README.md
├── package.json
├── vite.config.js
└── src/
    ├── frontend/
    │   ├── index.html
    │   ├── main.jsx
    │   └── App.jsx
    ├── backend/
    │   ├── main.py
    │   ├── requirements.txt
    │   └── scanner/
    │       └── rvol_scanner.py
    ├── components/
    ├── utils/
    └── public/
```

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
```bash
cd /workspace/src/backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend server:
```bash
python main.py
```

The backend will start on http://localhost:8000

### Frontend Setup
1. From the workspace root, install Node.js dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will start on http://localhost:3000

## Core Features

### RVOL Scanner Algorithm
The system implements a Relative Volume scanner that:
- Calculates RVOL = (Average Volume of Last 10 Days) / (Average Volume of Last 91 Days)
- Identifies "Gem" stocks with RVOL > 2.0 and price change between -1% and +2%
- Updates the watchlist to show high-volume stocks at the top

### Paper Trading System
- Initial balance of ₹10,000,000 (1 Crore INR)
- Buy/Sell functionality with real-time portfolio tracking
- Profit/Loss calculation based on current market prices

### Indian Market Focus
- Uses Nifty 50 stocks with .NS suffix (e.g., RELIANCE.NS, HDFCBANK.NS)
- Fetches real-time data using yfinance
- Optimized for NSE market hours