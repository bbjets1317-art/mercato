import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';

function StockDetailPage() {
  const { ticker } = useParams();
  const navigate = useNavigate();
  const [stock, setStock] = useState(null);
  const [loading, setLoading] = useState(true);
  const [shares, setShares] = useState('1');
  const [adding, setAdding] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    loadStock();
  }, [ticker]);

  const loadStock = async () => {
    try {
      const data = await api.getStockScore(ticker);
      setStock(data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading stock:', error);
      setLoading(false);
    }
  };

  const handleAddToPortfolio = async () => {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      alert('Please login first');
      navigate('/login');
      return;
    }

    const shareCount = parseFloat(shares);
    if (isNaN(shareCount) || shareCount <= 0) {
      alert('Please enter a valid number of shares');
      return;
    }

    setAdding(true);
    try {
      await api.addToPortfolio(userId, ticker, shareCount);
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (error) {
      console.error('Error adding to portfolio:', error);
      alert('Failed to add to portfolio. Make sure you are logged in.');
    }
    setAdding(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-cream flex items-center justify-center">
        <div className="text-navy text-xl">Loading {ticker}...</div>
      </div>
    );
  }

  if (!stock) {
    return (
      <div className="min-h-screen bg-cream flex items-center justify-center">
        <div className="text-navy text-xl">Stock not found</div>
      </div>
    );
  }

  const safetyScore = 100 - parseFloat(stock.risk_score);

  const categories = [
    { name: 'Financial Health', score: parseFloat(stock.financial_score), color: '#059669' },
    { name: 'Profitability', score: parseFloat(stock.profitability_score), color: '#2563eb' },
    { name: 'Growth', score: parseFloat(stock.growth_score), color: '#7c3aed' },
    { name: 'Momentum', score: parseFloat(stock.momentum_score), color: '#dc2626' },
    { name: 'Safety', score: safetyScore, color: '#ea580c' }
  ];

  const finalScore = parseFloat(stock.final_score);
  const highestCategory = categories.reduce((max, cat) => cat.score > max.score ? cat : max);

  return (
    <div className="min-h-screen bg-cream">
      {showSuccess && (
        <div className="fixed top-4 right-4 bg-green-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 animate-fade-in">
          <div className="flex items-center gap-3">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <div>
              <div className="font-bold">Added to Portfolio!</div>
              <div className="text-sm">{shares} shares of {ticker}</div>
            </div>
          </div>
        </div>
      )}

      <header className="bg-navy text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <img src="/mercato-logo.png" alt="Mercato" className="h-12" />
              <h1 className="text-2xl font-bold">Mercato</h1>
            </div>
            <nav className="flex space-x-6">
              <button onClick={() => navigate('/stocks')} className="hover:text-cream">
                Leaderboard
              </button>
              <button onClick={() => navigate('/portfolio')} className="hover:text-cream">
                Portfolio
              </button>
              <button onClick={() => navigate('/login')} className="hover:text-cream">
                Login
              </button>
            </nav>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <button 
          onClick={() => navigate('/stocks')}
          className="text-navy mb-6 hover:underline text-lg"
        >
          ← Back to Leaderboard
        </button>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <img 
                src={`https://financialmodelingprep.com/image-stock/${ticker}.png`}
                alt={ticker}
                className="h-16 w-16 object-contain"
                onError={(e) => { e.target.style.display = 'none' }}
              />
              <div>
                <h1 className="text-4xl font-bold text-navy">{ticker}</h1>
                <p className="text-navy opacity-75">
                  Updated: {new Date(stock.score_date).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="text-center">
              <div className="text-6xl font-bold text-navy">{finalScore.toFixed(1)}</div>
              <div className="text-navy text-lg">Overall Score</div>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-navy font-semibold mb-2">Number of Shares</label>
              <input
                type="text"
                value={shares}
                onChange={(e) => setShares(e.target.value)}
                placeholder="e.g. 10 or 5.5"
                className="w-full px-4 py-3 border-2 border-navy rounded-lg text-navy font-semibold"
              />
            </div>
            <div className="flex-1 flex items-end">
              <button 
                onClick={handleAddToPortfolio}
                disabled={adding}
                className="w-full bg-navy text-white py-3 rounded-lg font-semibold hover:opacity-90 transition disabled:opacity-50"
              >
                {adding ? 'Adding...' : 'Add to Portfolio'}
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-navy mb-6">Category Breakdown</h2>
          
          <div className="space-y-5">
            {categories.map((category) => (
              <div key={category.name} className="cursor-pointer hover:bg-cream p-3 rounded-lg transition">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-navy font-semibold text-lg">{category.name}</span>
                  <span className="text-navy text-xl font-bold">{category.score.toFixed(1)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div 
                    className="h-4 rounded-full transition-all duration-500"
                    style={{ 
                      width: `${category.score}%`,
                      backgroundColor: category.color
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 p-5 bg-cream rounded-lg border-l-4 border-navy">
            <h3 className="text-navy font-bold text-lg mb-3">AI Analysis</h3>
            <p className="text-navy leading-relaxed">
              {ticker} scored <strong>{finalScore.toFixed(1)}/100</strong>. 
              {finalScore >= 75 && " This stock demonstrates strong fundamentals across multiple categories."}
              {finalScore >= 60 && finalScore < 75 && " This stock shows solid performance with balanced metrics."}
              {finalScore < 60 && " This stock shows mixed signals and may warrant closer evaluation."}
              {" "}
              The standout category is <strong>{highestCategory.name.toLowerCase()}</strong> ({highestCategory.score.toFixed(1)}/100).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StockDetailPage;
