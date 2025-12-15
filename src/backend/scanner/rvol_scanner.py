import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RVOLScanner:
    def __init__(self):
        # Nifty 50 stocks
        self.nifty_50_symbols = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
            'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'BAJFINANCE.NS',
            'AXISBANK.NS', 'LT.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'WIPRO.NS',
            'HDFC.NS', 'KOTAKBANK.NS', 'NESTLEIND.NS', 'TITAN.NS', 'ULTRACEMCO.NS',
            'M&M.NS', 'ONGC.NS', 'POWERGRID.NS', 'TECHM.NS', 'BRITANNIA.NS',
            'JSWSTEEL.NS', 'GRASIM.NS', 'ADANIPORTS.NS', 'HEROMOTOCO.NS', 'COALINDIA.NS',
            'UPL.NS', 'IOC.NS', 'HINDALCO.NS', 'SUNPHARMA.NS', 'DRREDDY.NS',
            'TATAMOTORS.NS', 'TATASTEEL.NS', 'EICHERMOT.NS', 'CIPLA.NS', 'BPCL.NS',
            'SHREECEM.NS', 'DIVISLAB.NS', 'HCLTECH.NS', 'NTPC.NS', 'BAJAJFINSV.NS',
            'INDUSINDBK.NS', 'BAJAJ-AUTO.NS', 'HDFCLIFE.NS', 'SBILIFE.NS', 'APOLLOHOSP.NS',
            'VEDL.NS'
        ]
    
    def calculate_rvol(self, symbol):
        """
        Calculate Relative Volume (RVOL) for a given stock symbol
        RVOL = (Average Volume of Last 10 Days) / (Average Volume of Last 91 Days)
        """
        try:
            # Fetch stock data for the last 100 days to have enough data
            stock = yf.Ticker(symbol)
            hist = stock.history(period="100d")
            
            if len(hist) < 91:
                logger.warning(f"Not enough data for {symbol}")
                return None
            
            # Get the last 10 days volume
            last_10_days_vol = hist['Volume'].tail(10).mean()
            
            # Get the last 91 days volume (excluding today to avoid overlap)
            last_91_days_vol = hist['Volume'].tail(91).mean()
            
            # Calculate RVOL
            rvol = last_10_days_vol / last_91_days_vol if last_91_days_vol != 0 else 0
            
            # Get current price data
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            price_change_pct = ((current_price - prev_close) / prev_close) * 100
            
            return {
                'symbol': symbol,
                'rvol': float(rvol),
                'current_price': float(current_price),
                'price_change_pct': float(price_change_pct),
                'volume': int(hist['Volume'].iloc[-1]),
                'high': float(hist['High'].iloc[-1]),
                'low': float(hist['Low'].iloc[-1]),
                'open': float(hist['Open'].iloc[-1])
            }
        except Exception as e:
            logger.error(f"Error processing {symbol}: {str(e)}")
            return None
    
    def scan_stocks(self):
        """
        Scan all Nifty 50 stocks for RVOL signals
        Returns stocks with RVOL > 2.0 and price change between -1% and +2%
        """
        results = []
        
        for symbol in self.nifty_50_symbols:
            stock_data = self.calculate_rvol(symbol)
            if stock_data:
                # Check if RVOL > 2.0 and price change is between -1% and +2%
                if (stock_data['rvol'] > 2.0 and 
                    -1.0 <= stock_data['price_change_pct'] <= 2.0):
                    
                    stock_data['is_gem'] = True
                    results.append(stock_data)
                else:
                    stock_data['is_gem'] = False
                    results.append(stock_data)
        
        # Sort by RVOL in descending order, with gems at the top
        results.sort(key=lambda x: (x['is_gem'], x['rvol']), reverse=True)
        
        return results
    
    def get_top_stocks(self, count=20):
        """
        Get top N stocks based on RVOL and other criteria
        """
        all_results = self.scan_stocks()
        return all_results[:count]

# Example usage
if __name__ == "__main__":
    scanner = RVOLScanner()
    gem_stocks = scanner.get_top_stocks(10)
    
    print("Top stocks with high relative volume:")
    for stock in gem_stocks:
        status = "GEM" if stock['is_gem'] else ""
        print(f"{stock['symbol']}: RVOL={stock['rvol']:.2f}, "
              f"Price={stock['current_price']:.2f}, "
              f"Change={stock['price_change_pct']:.2f}%, {status}")