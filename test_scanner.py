#!/usr/bin/env python3
"""
Test script to verify the RVOL scanner functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from backend.scanner.rvol_scanner import RVOLScanner

def test_scanner():
    print("Testing RVOL Scanner...")
    
    # Create scanner instance
    scanner = RVOLScanner()
    
    # Test with a few sample stocks
    sample_stocks = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
    
    print("\nTesting individual stocks:")
    for symbol in sample_stocks:
        result = scanner.calculate_rvol(symbol)
        if result:
            print(f"{symbol}: RVOL={result['rvol']:.2f}, "
                  f"Price={result['current_price']:.2f}, "
                  f"Change={result['price_change_pct']:.2f}%")
        else:
            print(f"{symbol}: Could not fetch data")
    
    print(f"\nScanning all Nifty 50 stocks...")
    top_stocks = scanner.get_top_stocks(10)
    
    print("\nTop 10 stocks by RVOL:")
    for i, stock in enumerate(top_stocks, 1):
        status = "GEM" if stock['is_gem'] else ""
        print(f"{i}. {stock['symbol']}: RVOL={stock['rvol']:.2f}, "
              f"Price={stock['current_price']:.2f}, "
              f"Change={stock['price_change_pct']:.2f}%, {status}")

if __name__ == "__main__":
    test_scanner()