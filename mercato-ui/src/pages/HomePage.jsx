import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api } from '../services/api';

function HomePage() {
  const navigate = useNavigate();
  const [stocks, setStocks] = useState([]);
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSector, setSelectedSector] = useState('All');
  const [loadingProgress, setLoadingProgress] = useState(0);

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  useEffect(() => {
    loadStocks();
  }, []);

  useEffect(() => {
    if (selectedSector === 'All') {
      setFilteredStocks(stocks);
    } else {
      setFilteredStocks(stocks.filter(stock => stock.sector === selectedSector));
    }
  }, [selectedSector, stocks]);

  const loadStocks = async () => {
    try {
      // Progress simulation
      const progressInterval = setInterval(() => {
        setLoadingProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 5;
        });
      }, 800);

      const data = await api.getLeaderboard(500);
      
      clearInterval(progressInterval);
      setLoadingProgress(100);
      
      setTimeout(() => {
        setStocks(data);
        setFilteredStocks(data);
        setLoading(false);
      }, 300);
    } catch (error) {
      console.error('Error loading leaderboard:', error);
      setLoading(false);
    }
  };

  const sectors = ['All', ...new Set(stocks.map(s => s.sector))];
  const topStocks = filteredStocks.slice(0, 100);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#060824] via-[#0a0d3a] to-[#0e1249] flex flex-col items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <div className="text-[#d4c4a8] text-2xl tracking-[0.3em] uppercase mb-8">
            Loading Market Data
          </div>
          <div className="w-96 h-2 bg-[#0a0d3a] bg-opacity-50 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-[#d4c4a8]"
              style={{ width: `${loadingProgress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <div className="text-[#d4c4a8] text-sm opacity-50 mt-4 tracking-[0.2em]">
            Fetching live prices for 500+ stocks...
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#060824] via-[#0a0d3a] to-[#0e1249]">
      {/* Background Pattern */}
      <div className="fixed inset-0 opacity-3 pointer-events-none">
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(200, 180, 150, 0.1) 1px, transparent 0)',
          backgroundSize: '40px 40px'
        }} />
      </div>

      {/* Animated Background Orb */}
      <motion.div
        className="fixed w-[800px] h-[800px] rounded-full blur-3xl pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(200, 180, 150, 0.08) 0%, transparent 70%)',
          top: '10%',
          right: '5%'
        }}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.08, 0.12, 0.08]
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Header */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-[#060824] bg-opacity-90 border-b border-[#d4c4a8] border-opacity-10">
        <div className="container mx-auto px-8 py-5 flex items-center justify-between">
          <div className="flex items-center space-x-4" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            <img src="/mercato-logo.png" alt="Mercato" className="h-11" />
            <span className="text-xl font-light tracking-[0.3em] text-[#d4c4a8]">MERCATO</span>
          </div>
          <nav className="flex gap-8 items-center">
            <button onClick={() => navigate('/stocks')} className="text-white text-sm tracking-[0.2em] uppercase font-semibold">
              Leaderboard
            </button>
            <button onClick={() => navigate('/portfolio')} className="text-[#d4c4a8] hover:text-white transition text-sm tracking-[0.2em] uppercase">
              Portfolio
            </button>
            <button onClick={() => navigate('/login')} className="text-[#d4c4a8] hover:text-white transition text-sm tracking-[0.2em] uppercase">
              {localStorage.getItem('email') || 'Login'}
            </button>
          </nav>
        </div>
      </nav>

      <div className="container mx-auto px-8 py-20 relative z-10">
        {/* Header Section */}
        <motion.div
          className="text-center mb-20"
          initial="hidden"
          animate="visible"
          variants={fadeIn}
        >
          <h1 className="text-7xl font-light text-white mb-6 tracking-tight">Top Performers</h1>
          <div className="w-32 h-px bg-gradient-to-r from-transparent via-[#d4c4a8] to-transparent mx-auto mb-8 opacity-40" />
          <p className="text-[#d4c4a8] tracking-[0.2em] text-sm uppercase opacity-70">
            {filteredStocks.length} Securities • Live Prices • Machine-Scored Weekly
          </p>
        </motion.div>

        {/* Sector Filter */}
        <motion.div
          className="mb-16"
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          transition={{ delay: 0.2 }}
        >
          <div className="flex flex-wrap justify-center gap-3">
            {sectors.map(sector => (
              <motion.button
                key={sector}
                onClick={() => setSelectedSector(sector)}
                className={`px-8 py-3 text-xs tracking-[0.2em] uppercase font-semibold transition-all ${
                  selectedSector === sector
                    ? 'bg-[#d4c4a8] text-[#060824] shadow-2xl scale-105'
                    : 'bg-[#0a0d3a] bg-opacity-40 backdrop-blur-sm border border-[#d4c4a8] border-opacity-15 text-[#d4c4a8] hover:border-opacity-40 hover:bg-opacity-60'
                }`}
                whileHover={{ scale: selectedSector === sector ? 1.05 : 1.03 }}
                whileTap={{ scale: 0.98 }}
              >
                {sector}
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Leaderboard Grid */}
        <div className="grid gap-4 max-w-7xl mx-auto">
          {topStocks.map((stock, index) => {
            const priceChange = parseFloat(stock.price_change_pct || 0);
            const isPositive = priceChange >= 0;
            const currentPrice = parseFloat(stock.current_price || 0);
            
            return (
              <motion.div
                key={stock.ticker}
                className="bg-[#0a0d3a] bg-opacity-40 backdrop-blur-xl border border-[#d4c4a8] border-opacity-10 p-8 hover:border-opacity-30 hover:bg-opacity-60 cursor-pointer transition-all group"
                onClick={() => navigate(`/stock/${stock.ticker}`)}
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.01, duration: 0.3 }}
                whileHover={{ scale: 1.01, transition: { duration: 0.2 } }}
              >
                <div className="flex items-center gap-8">
                  {/* Rank */}
                  <div className="text-5xl font-light text-[#d4c4a8] opacity-30 group-hover:opacity-60 transition w-20 text-center">
                    {index + 1}
                  </div>

                  {/* Logo */}
                  <img 
                    src={`https://financialmodelingprep.com/image-stock/${stock.ticker}.png`}
                    alt={stock.ticker}
                    className="h-14 w-14 object-contain opacity-70 group-hover:opacity-100 transition"
                    onError={(e) => { e.target.style.display = 'none' }}
                  />

                  {/* Ticker & Name */}
                  <div className="flex-1">
                    <h3 className="text-3xl font-semibold text-white mb-1 tracking-wide group-hover:text-[#d4c4a8] transition">
                      {stock.ticker}
                    </h3>
                    <p className="text-[#d4c4a8] opacity-60 group-hover:opacity-80 transition truncate">{stock.name}</p>
                  </div>

                  {/* Price */}
                  <div className="text-center px-6">
                    <div className="text-2xl font-semibold text-white mb-1">
                      ${currentPrice > 0 ? currentPrice.toFixed(2) : '—'}
                    </div>
                    {currentPrice > 0 && (
                      <div className={`text-sm font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                        {isPositive ? '▲' : '▼'} {Math.abs(priceChange).toFixed(2)}%
                      </div>
                    )}
                  </div>

                  {/* Sector */}
                  <div className="text-center px-6">
                    <span className="text-xs tracking-[0.2em] uppercase text-[#d4c4a8] opacity-40 group-hover:opacity-70 transition px-4 py-2 bg-[#d4c4a8] bg-opacity-5 rounded">
                      {stock.sector}
                    </span>
                  </div>

                  {/* Score */}
                  <div className="text-right">
                    <div className="text-6xl font-light text-white group-hover:text-[#d4c4a8] transition">
                      {parseFloat(stock.final_score).toFixed(1)}
                    </div>
                    <div className="text-xs text-[#d4c4a8] opacity-40 tracking-[0.15em] uppercase">Score</div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        <div className="text-center mt-16">
          <p className="text-[#d4c4a8] opacity-30 text-xs tracking-[0.2em] uppercase">
            Showing {topStocks.length} of {filteredStocks.length} securities with live prices
          </p>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
