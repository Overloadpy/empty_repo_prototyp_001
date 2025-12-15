import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Main Dashboard Component
const App = () => {
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [portfolio, setPortfolio] = useState({
    cash: 10000000,
    total_value: 10000000,
    used_margin: 0,
    holdings: [],
    orders: []
  });
  const [watchlist, setWatchlist] = useState([]);
  const [activeTab, setActiveTab] = useState('watchlist');
  const [timeframe, setTimeframe] = useState('1d');

  // Fetch initial data
  useEffect(() => {
    fetchStocks();
    fetchPortfolio();
  }, []);

  const fetchStocks = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/stocks');
      setStocks(response.data.data);
      setWatchlist(response.data.data);
    } catch (error) {
      console.error('Error fetching stocks:', error);
    }
  };

  const fetchPortfolio = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/portfolio');
      setPortfolio(response.data);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    }
  };

  const fetchChartData = async (symbol) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/chart/${symbol}?timeframe=${timeframe}`);
      setChartData(response.data.data);
      setSelectedStock(symbol);
    } catch (error) {
      console.error('Error fetching chart data:', error);
    }
  };

  const executeTrade = async (symbol, action, quantity) => {
    try {
      const response = await axios.post('http://localhost:8000/api/trade', {
        symbol,
        action,
        quantity
      });
      
      setPortfolio(response.data.portfolio);
      fetchStocks(); // Refresh the watchlist
      
      alert(`Successfully executed ${action} order for ${quantity} shares of ${symbol}`);
    } catch (error) {
      console.error('Error executing trade:', error);
      alert(`Error: ${error.response?.data?.detail || 'Failed to execute trade'}`);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  const formatNumber = (num) => {
    if (num >= 10000000) {
      return (num / 10000000).toFixed(2) + ' Cr';
    } else if (num >= 100000) {
      return (num / 100000).toFixed(2) + ' L';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(2) + ' K';
    }
    return num.toFixed(2);
  };

  return (
    <div className="flex flex-col h-screen bg-[#191919] text-[#e0e0e0] overflow-hidden">
      {/* Header */}
      <header className="bg-[#1e222d] p-4 border-b border-[#2a2a2a]">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-6">
            <h1 className="text-xl font-bold">Project Kite-X</h1>
            <div className="flex space-x-4 text-sm">
              <span>Cash: <span className="text-[#00d4aa]">{formatPrice(portfolio.cash)}</span></span>
              <span>Total: <span className="text-[#00d4aa]">{formatPrice(portfolio.total_value)}</span></span>
              <span>Used: <span className="text-[#ff5252]">{formatPrice(portfolio.used_margin)}</span></span>
            </div>
          </div>
          <div className="flex space-x-4">
            <button className="px-3 py-1 bg-[#383838] rounded text-sm hover:bg-[#4a4a4a] transition-colors">
              Connect Broker
            </button>
            <button className="px-3 py-1 bg-[#383838] rounded text-sm hover:bg-[#4a4a4a] transition-colors">
              Settings
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Market Watchlist */}
        <div className="w-1/4 bg-[#1e222d] border-r border-[#2a2a2a] flex flex-col">
          <div className="p-3 border-b border-[#2a2a2a]">
            <h2 className="font-semibold">Market Watch</h2>
          </div>
          
          <div className="flex border-b border-[#2a2a2a]">
            <button 
              className={`flex-1 py-2 text-center text-sm ${activeTab === 'watchlist' ? 'border-b-2 border-[#00d4aa] text-[#00d4aa]' : ''}`}
              onClick={() => setActiveTab('watchlist')}
            >
              Watchlist
            </button>
            <button 
              className={`flex-1 py-2 text-center text-sm ${activeTab === 'gems' ? 'border-b-2 border-[#00d4aa] text-[#00d4aa]' : ''}`}
              onClick={() => setActiveTab('gems')}
            >
              Gems
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            {watchlist.map((stock, index) => (
              <div 
                key={index} 
                className={`p-3 border-b border-[#2a2a2a] cursor-pointer hover:bg-[#383838] transition-colors ${
                  selectedStock === stock.symbol ? 'bg-[#383838]' : ''
                }`}
                onClick={() => fetchChartData(stock.symbol)}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium">{stock.symbol.replace('.NS', '')}</div>
                    <div className="text-xs text-[#9b9b9b]">NSE</div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{formatPrice(stock.current_price)}</div>
                    <div className={`text-xs ${stock.price_change_pct >= 0 ? 'text-[#00d4aa]' : 'text-[#ff5252]'}`}>
                      {stock.price_change_pct >= 0 ? '+' : ''}{stock.price_change_pct.toFixed(2)}%
                    </div>
                  </div>
                </div>
                {stock.is_gem && (
                  <div className="mt-1 text-xs px-2 py-1 bg-[#00d4aa]/20 text-[#00d4aa] rounded inline-block">
                    GEM
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Center Panel - Chart */}
        <div className="w-1/2 bg-[#191919] flex flex-col">
          <div className="p-3 border-b border-[#2a2a2a] flex justify-between items-center">
            <div>
              {selectedStock ? (
                <h2 className="text-lg font-semibold">{selectedStock.replace('.NS', '')} (NSE)</h2>
              ) : (
                <h2 className="text-lg font-semibold">Select a stock to view chart</h2>
              )}
            </div>
            <div className="flex space-x-2">
              {['1m', '5m', '15m', '1h', '1d', '1w', '1M'].map((tf) => (
                <button
                  key={tf}
                  className={`px-2 py-1 text-xs rounded ${
                    timeframe === tf 
                      ? 'bg-[#00d4aa] text-black' 
                      : 'bg-[#383838] hover:bg-[#4a4a4a]'
                  }`}
                  onClick={() => selectedStock && setTimeframe(tf)}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex-1 flex items-center justify-center bg-[#191919]">
            {selectedStock ? (
              <div className="w-full h-full flex flex-col items-center justify-center text-[#9b9b9b]">
                <div className="text-xl mb-2">Chart Visualization</div>
                <div className="text-sm">Selected: {selectedStock}</div>
                <div className="text-sm">Timeframe: {timeframe}</div>
                <div className="mt-4 text-xs text-center px-4">
                  In a real implementation, this would show TradingView charts with candlestick patterns, 
                  technical indicators, and volume profiles.
                </div>
              </div>
            ) : (
              <div className="text-center text-[#9b9b9b]">
                <div className="text-xl mb-2">No Stock Selected</div>
                <div className="text-sm">Select a stock from the watchlist to view its chart</div>
              </div>
            )}
          </div>
          
          {/* Trading Controls */}
          {selectedStock && (
            <div className="p-3 border-t border-[#2a2a2a] bg-[#1e222d]">
              <div className="grid grid-cols-2 gap-4">
                <button 
                  className="py-2 bg-[#00d4aa] text-black font-semibold rounded hover:bg-opacity-90 transition-colors"
                  onClick={() => executeTrade(selectedStock, 'buy', 1)}
                >
                  BUY {selectedStock.replace('.NS', '')}
                </button>
                <button 
                  className="py-2 bg-[#ff5252] text-white font-semibold rounded hover:bg-opacity-90 transition-colors"
                  onClick={() => executeTrade(selectedStock, 'sell', 1)}
                >
                  SELL {selectedStock.replace('.NS', '')}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Portfolio/Orders */}
        <div className="w-1/4 bg-[#1e222d] border-l border-[#2a2a2a] flex flex-col">
          <div className="p-3 border-b border-[#2a2a2a]">
            <h2 className="font-semibold">Portfolio</h2>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            <div className="p-3 border-b border-[#2a2a2a]">
              <div className="text-sm text-[#9b9b9b]">Holdings</div>
              {portfolio.holdings.length === 0 ? (
                <div className="text-xs text-[#9b9b9b] mt-2">No holdings</div>
              ) : (
                portfolio.holdings.map((holding, index) => (
                  <div key={index} className="mt-2 p-2 bg-[#383838] rounded">
                    <div className="flex justify-between">
                      <div className="font-medium">{holding.symbol.replace('.NS', '')}</div>
                      <div className={`text-xs ${holding.pnl >= 0 ? 'text-[#00d4aa]' : 'text-[#ff5252]'}`}>
                        {holding.pnl >= 0 ? '+' : ''}{formatPrice(holding.pnl)}
                      </div>
                    </div>
                    <div className="text-xs text-[#9b9b9b]">
                      Qty: {holding.quantity} | Avg: {formatPrice(holding.avg_price)}
                    </div>
                    <div className="text-xs">
                      LTP: {formatPrice(holding.current_price)} | P&L: {holding.pnl_percent.toFixed(2)}%
                    </div>
                  </div>
                ))
              )}
            </div>
            
            <div className="p-3">
              <div className="text-sm text-[#9b9b9b]">Recent Orders</div>
              {portfolio.orders.length === 0 ? (
                <div className="text-xs text-[#9b9b9b] mt-2">No recent orders</div>
              ) : (
                portfolio.orders.slice(-5).reverse().map((order, index) => (
                  <div key={index} className="mt-2 p-2 bg-[#383838] rounded text-xs">
                    <div className="font-medium">{order.symbol.replace('.NS', '')}</div>
                    <div>{order.action.toUpperCase()} {order.quantity} @ {formatPrice(order.price)}</div>
                    <div className="text-[#9b9b9b]">{new Date(order.timestamp).toLocaleTimeString()}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;