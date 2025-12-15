from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from scanner.rvol_scanner import RVOLScanner

app = FastAPI(title="Project Kite-X API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global scanner instance
scanner = RVOLScanner()

# Mock portfolio for paper trading
portfolio = {
    "cash": 10000000,  # ₹1 Crore
    "holdings": {},
    "orders": [],
    "total_value": 10000000
}

@app.get("/")
def read_root():
    return {"message": "Project Kite-X Backend API", "version": "1.0.0"}

@app.get("/api/stocks")
async def get_stocks():
    """Get all scanned stocks with RVOL data"""
    try:
        stocks = scanner.get_top_stocks(50)
        return {"data": stocks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stocks: {str(e)}")

@app.get("/api/stocks/gems")
async def get_gem_stocks():
    """Get only gem stocks (high RVOL)"""
    try:
        all_stocks = scanner.get_top_stocks(50)
        gem_stocks = [stock for stock in all_stocks if stock['is_gem']]
        return {"data": gem_stocks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching gem stocks: {str(e)}")

@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio details"""
    global portfolio
    
    # Calculate total value based on current prices
    total_value = portfolio["cash"]
    holdings_data = []
    
    for symbol, holding in portfolio["holdings"].items():
        # Get current price for the stock
        stock_data = scanner.calculate_rvol(symbol)
        if stock_data:
            current_value = holding["quantity"] * stock_data["current_price"]
            pnl = (stock_data["current_price"] - holding["avg_price"]) * holding["quantity"]
            total_value += current_value
            
            holdings_data.append({
                "symbol": symbol,
                "quantity": holding["quantity"],
                "avg_price": holding["avg_price"],
                "current_price": stock_data["current_price"],
                "current_value": current_value,
                "pnl": pnl,
                "pnl_percent": ((stock_data["current_price"] - holding["avg_price"]) / holding["avg_price"]) * 100
            })
    
    portfolio["total_value"] = total_value
    
    return {
        "cash": portfolio["cash"],
        "total_value": portfolio["total_value"],
        "used_margin": total_value - portfolio["cash"],
        "holdings": holdings_data,
        "orders": portfolio["orders"]
    }

@app.post("/api/trade")
async def execute_trade(symbol: str, action: str, quantity: int):
    """Execute buy/sell trade"""
    global portfolio
    
    if action.lower() not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Action must be 'buy' or 'sell'")
    
    # Get current price for the stock
    stock_data = scanner.calculate_rvol(symbol)
    if not stock_data:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    
    current_price = stock_data["current_price"]
    total_cost = current_price * quantity
    
    if action.lower() == "buy":
        if total_cost > portfolio["cash"]:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Update portfolio
        if symbol in portfolio["holdings"]:
            # Average down/up
            existing_holding = portfolio["holdings"][symbol]
            total_qty = existing_holding["quantity"] + quantity
            avg_price = ((existing_holding["avg_price"] * existing_holding["quantity"]) + total_cost) / total_qty
            portfolio["holdings"][symbol] = {
                "quantity": total_qty,
                "avg_price": avg_price
            }
        else:
            portfolio["holdings"][symbol] = {
                "quantity": quantity,
                "avg_price": current_price
            }
        
        portfolio["cash"] -= total_cost
        
    elif action.lower() == "sell":
        if symbol not in portfolio["holdings"] or portfolio["holdings"][symbol]["quantity"] < quantity:
            raise HTTPException(status_code=400, detail="Insufficient shares to sell")
        
        # Update portfolio
        holding = portfolio["holdings"][symbol]
        remaining_qty = holding["quantity"] - quantity
        
        if remaining_qty == 0:
            del portfolio["holdings"][symbol]
        else:
            portfolio["holdings"][symbol]["quantity"] = remaining_qty
        
        portfolio["cash"] += total_cost
    
    # Record the order
    order = {
        "id": len(portfolio["orders"]) + 1,
        "symbol": symbol,
        "action": action.lower(),
        "quantity": quantity,
        "price": current_price,
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    }
    portfolio["orders"].append(order)
    
    return {
        "message": f"Successfully executed {action} order",
        "order": order,
        "portfolio": await get_portfolio()
    }

@app.get("/api/chart/{symbol}")
async def get_chart_data(symbol: str, timeframe: str = "1d"):
    """Get chart data for a specific stock"""
    try:
        import yfinance as yf
        
        period_map = {
            "1d": "1d",
            "5d": "5d", 
            "1mo": "1mo",
            "3mo": "3mo",
            "6mo": "6mo",
            "1y": "1y",
            "2y": "2y",
            "5y": "5y",
            "10y": "10y",
            "max": "max"
        }
        
        valid_timeframes = {
            "1min": "1m",
            "5min": "5m", 
            "15min": "15m",
            "30min": "30m",
            "1h": "1h",
            "1d": "1d",
            "5d": "5d",
            "1wk": "1wk",
            "1mo": "1mo",
            "3mo": "3mo"
        }
        
        # Map our custom timeframes to yfinance
        yf_period = valid_timeframes.get(timeframe, "1mo")
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=yf_period)
        
        # Convert to the format expected by frontend
        chart_data = []
        for idx, row in hist.iterrows():
            chart_data.append({
                "time": idx.strftime('%Y-%m-%d %H:%M:%S'),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {"symbol": symbol, "timeframe": timeframe, "data": chart_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chart data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)