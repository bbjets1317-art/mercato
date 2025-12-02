import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api } from '../services/api';

function CircularScore({ score }) {
  const radius = 90;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  
  return (
    <div className="relative inline-flex items-center justify-center">
      <svg className="transform -rotate-90" width="240" height="240">
        <circle
          cx="120"
          cy="120"
          r={radius}
          stroke="rgba(212, 196, 168, 0.1)"
          strokeWidth="16"
          fill="none"
        />
        <circle
          cx="120"
          cy="120"
          r={radius}
          stroke="#d4c4a8"
          strokeWidth="16"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          strokeLinecap="round"
          className="transition-all duration-1000"
        />
      </svg>
      <div className="absolute text-center">
        <div className="text-7xl font-light text-white mb-2">{score.toFixed(1)}</div>
        <div className="text-sm text-[#d4c4a8] opacity-70 tracking-[0.2em] uppercase">Portfolio Score</div>
      </div>
    </div>
  );
}

function PortfolioPage() {
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTicker, setSearchTicker] = useState('');
  const [editingStock, setEditingStock] = useState(null);
  const [editShares, setEditShares] = useState('');

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  useEffect(() => {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      navigate('/login');
      return;
    }
    loadPortfolio();
  }, []);

  const loadPortfolio = async () => {
    try {
      const userId = localStorage.getItem('user_id');
      const data = await api.getPortfolio(userId);
      setPortfolio(data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading portfolio:', error);
      setPortfolio([]);
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTicker.trim()) {
      navigate(`/stock/${searchTicker.toUpperCase()}`);
    }
  };

  const handleEdit = (stock) => {
    setEditingStock(stock.ticker);
    setEditShares(stock.shares);
  };

  const handleSaveEdit = async (ticker) => {
    const userId = localStorage.getItem('user_id');
    const newShares = parseFloat(editShares);
    
    if (isNaN(newShares) || newShares <= 0) {
      alert('Please enter a valid number');
      return;
    }

    try {
      await api.updatePortfolio(userId, ticker, newShares);
      setEditingStock(null);
      loadPortfolio();
    } catch (error) {
      alert('Failed to update shares');
    }
  };

  const handleRemove = async (ticker) => {
    if (!confirm(`⚠️ Are you sure you want to remove ${ticker} from your portfolio?`)) {
      return;
    }

    const userId = localStorage.getItem('user_id');
    try {
      await api.removeFromPortfolio(userId, ticker);
      loadPortfolio();
    } catch (error) {
      alert('Failed to remove stock');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#060824] via-[#0a0d3a] to-[#0e1249] flex items-center justify-center">
        <div className="text-[#d4c4a8] text-xl tracking-[0.2em] uppercase">Loading...</div>
      </div>
    );
  }

  const portfolioScore = portfolio.length > 0 
    ? portfolio.reduce((sum, stock) => sum + parseFloat(stock.final_score), 0) / portfolio.length 
    : 0;

  const totalValue = portfolio.reduce((sum, stock) => {
    return sum + (parseFloat(stock.shares) * parseFloat(stock.current_price || 0));
  }, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#060824] via-[#0a0d3a] to-[#0e1249]">
      {/* Background Pattern */}
      <div className="fixed inset-0 opacity-3 pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(200, 180, 150, 0.1) 1px, transparent 0)',
          backgroundSize: '40px 40px'
        }} />
      </div>

      {/* Header */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-[#060824] bg-opacity-90 border-b border-[#d4c4a8] border-opacity-10">
        <div className="container mx-auto px-8 py-5 flex items-center justify-between">
          <div className="flex items-center space-x-4" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            <img src="/mercato-logo.png" alt="Mercato" className="h-11" />
            <span className="text-xl font-light tracking-[0.3em] text-[#d4c4a8]">MERCATO</span>
          </div>
          <nav className="flex gap-8 items-center">
            <button onClick={() => navigate('/stocks')} className="text-[#d4c4a8] hover:text-white transition text-sm tracking-[0.2em] uppercase">
              Leaderboard
            </button>
            <button onClick={() => navigate('/portfolio')} className="text-white text-sm tracking-[0.2em] uppercase font-semibold">
              Portfolio
            </button>
            <button onClick={() => navigate('/login')} className="text-[#d4c4a8] hover:text-white transition text-sm tracking-[0.2em] uppercase">
              {localStorage.getItem('email') || 'Login'}
            </button>
          </nav>
        </div>
      </nav>

      <div className="container mx-auto px-8 py-16 relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-16">
          <motion.div initial="hidden" animate="visible" variants={fadeIn}>
            <h1 className="text-6xl font-light text-white tracking-wide">My Portfolio</h1>
            <div className="w-32 h-px bg-gradient-to-r from-[#d4c4a8] to-transparent mt-6 opacity-40" />
          </motion.div>
          
          <motion.form
            onSubmit={handleSearch}
            className="flex gap-3"
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ delay: 0.2 }}
          >
            <input
              type="text"
              value={searchTicker}
              onChange={(e) => setSearchTicker(e.target.value)}
              placeholder="Search ticker..."
              className="px-6 py-3 bg-[#0a0d3a] bg-opacity-50 backdrop-blur-sm border border-[#d4c4a8] border-opacity-20 rounded text-white placeholder-[#d4c4a8] placeholder-opacity-30 focus:border-opacity-60 focus:outline-none transition w-64"
            />
            <button 
              type="submit"
              className="bg-[#d4c4a8] text-[#060824] px-8 py-3 text-sm tracking-[0.2em] uppercase font-semibold hover:bg-[#e8e0cf] transition-all"
            >
              Search
            </button>
          </motion.form>
        </div>

        {/* Score Display */}
        <motion.div
          className="bg-[#0a0d3a] bg-opacity-30 backdrop-blur-xl border border-[#d4c4a8] border-opacity-10 p-16 mb-12"
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center justify-center gap-32">
            <div>
              <CircularScore score={portfolioScore} />
              <p className="text-[#d4c4a8] opacity-50 text-sm text-center mt-6 tracking-[0.15em] uppercase">{portfolio.length} Holdings</p>
            </div>
            
            <div className="text-center">
              <div className="text-7xl font-light text-white mb-3">
                ${totalValue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
              </div>
              <div className="text-sm text-[#d4c4a8] opacity-70 tracking-[0.2em] uppercase">Total Value</div>
            </div>
          </div>
        </motion.div>

        {/* Holdings */}
        {portfolio.length === 0 ? (
          <motion.div
            className="bg-[#0a0d3a] bg-opacity-30 backdrop-blur-xl border border-[#d4c4a8] border-opacity-10 p-24 text-center"
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ delay: 0.6 }}
          >
            <p className="text-white text-2xl mb-8 font-light">Your portfolio is empty</p>
            <button 
              onClick={() => navigate('/stocks')}
              className="bg-[#d4c4a8] text-[#060824] px-12 py-4 text-sm tracking-[0.2em] uppercase font-semibold hover:bg-[#e8e0cf] transition-all"
            >
              Browse Stocks
            </button>
          </motion.div>
        ) : (
          <div className="space-y-4">
            {portfolio.map((stock, index) => {
              const value = parseFloat(stock.shares) * parseFloat(stock.current_price || 0);
              const priceChange = parseFloat(stock.price_change_pct || 0);
              const isPositive = priceChange >= 0;
              
              return (
                <motion.div
                  key={stock.ticker}
                  className="bg-[#0a0d3a] bg-opacity-30 backdrop-blur-xl border border-[#d4c4a8] border-opacity-10 p-8 hover:border-opacity-25 transition-all group"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="flex items-center gap-8">
                    <img 
                      src={`https://financialmodelingprep.com/image-stock/${stock.ticker}.png`}
                      alt={stock.ticker}
                      className="h-16 w-16 object-contain opacity-80 group-hover:opacity-100 transition"
                      onError={(e) => { e.target.style.display = 'none' }}
                    />

                    <div className="flex-1">
                      <h3 
                        className="text-3xl font-semibold text-white cursor-pointer hover:text-[#d4c4a8] transition tracking-wide mb-1"
                        onClick={() => navigate(`/stock/${stock.ticker}`)}
                      >
                        {stock.ticker}
                      </h3>
                      <p className="text-[#d4c4a8] opacity-60 truncate">{stock.name}</p>
                    </div>

                    <div className="text-center px-8">
                      <div className="text-4xl font-light text-white mb-1">{parseFloat(stock.final_score).toFixed(1)}</div>
                      <div className="text-xs text-[#d4c4a8] opacity-50 tracking-[0.15em] uppercase">Score</div>
                    </div>

                    <div className="text-center px-8">
                      <div className={`text-3xl font-semibold mb-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                        {isPositive ? '▲' : '▼'} {Math.abs(priceChange).toFixed(2)}%
                      </div>
                      <div className="text-sm text-[#d4c4a8] opacity-60">${parseFloat(stock.current_price || 0).toFixed(2)}</div>
                    </div>

                    <div className="text-center px-8">
                      {editingStock === stock.ticker ? (
                        <input
                          type="text"
                          value={editShares}
                          onChange={(e) => setEditShares(e.target.value)}
                          className="w-28 px-3 py-2 bg-[#060824] bg-opacity-50 border-2 border-[#d4c4a8] rounded text-white text-center font-semibold text-xl focus:outline-none"
                          autoFocus
                          onBlur={() => handleSaveEdit(stock.ticker)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSaveEdit(stock.ticker);
                            if (e.key === 'Escape') setEditingStock(null);
                          }}
                        />
                      ) : (
                        <div className="text-2xl font-light text-white mb-1">{parseFloat(stock.shares).toFixed(2)}</div>
                      )}
                      <div className="text-xs text-[#d4c4a8] opacity-50 tracking-[0.15em] uppercase">Shares</div>
                    </div>

                    <div className="text-center px-8">
                      <div className="text-2xl font-light text-white mb-1">${value.toFixed(2)}</div>
                      <div className="text-xs text-[#d4c4a8] opacity-50 tracking-[0.15em] uppercase">Value</div>
                    </div>

                    <div className="flex gap-3">
                      <button
                        onClick={() => handleEdit(stock)}
                        className="text-[#d4c4a8] hover:text-white transition p-2"
                        title="Edit shares"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>

                      <button
                        onClick={() => handleRemove(stock.ticker)}
                        className="text-red-400 hover:text-red-300 transition p-2"
                        title="Remove"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default PortfolioPage;
