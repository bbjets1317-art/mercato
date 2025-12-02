import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api } from '../services/api';
import { supabase } from '../services/supabase';

function LoginPage() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        // Login with Supabase
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password
        });

        if (error) throw error;

        // Store user info
        localStorage.setItem('user_id', data.user.id);
        localStorage.setItem('email', data.user.email);
        localStorage.setItem('token', data.session.access_token);

        navigate('/portfolio');
      } else {
        // Signup with Supabase
        const { data, error } = await supabase.auth.signUp({
          email,
          password
        });

        if (error) throw error;

        // Store user info
        localStorage.setItem('user_id', data.user.id);
        localStorage.setItem('email', data.user.email);
        localStorage.setItem('token', data.session.access_token);

        navigate('/portfolio');
      }
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user_id');
    localStorage.removeItem('email');
    localStorage.removeItem('token');
    supabase.auth.signOut();
    navigate('/');
  };

  const isLoggedIn = localStorage.getItem('user_id');

  if (isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#060824] via-[#0a0d3a] to-[#0e1249]">
        {/* Header */}
        <nav className="backdrop-blur-lg bg-[#060824] bg-opacity-90 border-b border-[#d4c4a8] border-opacity-10">
          <div className="container mx-auto px-8 py-5 flex items-center justify-between">
            <div className="flex items-center space-x-4" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
              <img src="/mercato-logo.png" alt="Mercato" className="h-11" />
              <span className="text-xl font-light tracking-[0.3em] text-[#d4c4a8]">MERCATO</span>
            </div>
            <div className="flex gap-8 items-center">
              <button onClick={() => navigate('/stocks')} className="text-[#d4c4a8] hover:text-white transition text-sm tracking-[0.2em] uppercase">
                Leaderboard
              </button>
              <button onClick={() => navigate('/portfolio')} className="text-[#d4c4a8] hover:text-white transition text-sm tracking-[0.2em] uppercase">
                Portfolio
              </button>
            </div>
          </div>
        </nav>

        {/* Account Info */}
        <div className="container mx-auto px-8 py-24">
          <motion.div
            className="max-w-2xl mx-auto bg-[#0a0d3a] bg-opacity-50 backdrop-blur-xl border border-[#d4c4a8] border-opacity-20 p-16 text-center"
            initial="hidden"
            animate="visible"
            variants={fadeIn}
          >
            <div className="mb-8">
              <div className="w-24 h-24 bg-[#d4c4a8] bg-opacity-20 rounded-full mx-auto flex items-center justify-center mb-6">
                <svg className="w-12 h-12 text-[#d4c4a8]" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                </svg>
              </div>
              <h1 className="text-4xl font-light text-white mb-2 tracking-wide">Your Account</h1>
              <div className="w-24 h-px bg-gradient-to-r from-transparent via-[#d4c4a8] to-transparent mx-auto my-6 opacity-40" />
            </div>

            <div className="mb-8 space-y-4">
              <div className="bg-[#060824] bg-opacity-50 p-6 rounded border border-[#d4c4a8] border-opacity-10">
                <div className="text-xs tracking-[0.2em] uppercase text-[#d4c4a8] opacity-50 mb-2">Email</div>
                <div className="text-lg text-white font-light">{localStorage.getItem('email')}</div>
              </div>
              <div className="bg-[#060824] bg-opacity-50 p-6 rounded border border-[#d4c4a8] border-opacity-10">
                <div className="text-xs tracking-[0.2em] uppercase text-[#d4c4a8] opacity-50 mb-2">Status</div>
                <div className="text-lg text-white font-light">Active Member</div>
              </div>
            </div>

            <div className="flex gap-4 justify-center">
              <button
                onClick={() => navigate('/portfolio')}
                className="bg-[#d4c4a8] text-[#060824] px-10 py-3 text-sm tracking-[0.15em] uppercase font-semibold hover:bg-[#e8e0cf] transition-all"
              >
                View Portfolio
              </button>
              <button
                onClick={handleLogout}
                className="border border-[#d4c4a8] border-opacity-40 text-[#d4c4a8] px-10 py-3 text-sm tracking-[0.15em] uppercase font-semibold hover:border-opacity-100 hover:bg-[#d4c4a8] hover:bg-opacity-10 transition-all"
              >
                Sign Out
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#060824] via-[#0a0d3a] to-[#0e1249] relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(200, 180, 150, 0.15) 1px, transparent 0)',
          backgroundSize: '40px 40px'
        }} />
      </div>

      {/* Animated Orb */}
      <motion.div
        className="absolute w-[600px] h-[600px] rounded-full blur-3xl"
        style={{
          background: 'radial-gradient(circle, rgba(200, 180, 150, 0.12) 0%, transparent 70%)',
          top: '20%',
          right: '10%'
        }}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.12, 0.18, 0.12]
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Header */}
      <nav className="backdrop-blur-lg bg-[#060824] bg-opacity-90 border-b border-[#d4c4a8] border-opacity-10">
        <div className="container mx-auto px-8 py-5 flex items-center justify-between">
          <div className="flex items-center space-x-4" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            <img src="/mercato-logo.png" alt="Mercato" className="h-11" />
            <span className="text-xl font-light tracking-[0.3em] text-[#d4c4a8]">MERCATO</span>
          </div>
        </div>
      </nav>

      {/* Login/Signup Form */}
      <div className="container mx-auto px-8 py-24 relative z-10">
        <motion.div
          className="max-w-md mx-auto"
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          transition={{ duration: 0.8 }}
        >
          <div className="text-center mb-12">
            <h1 className="text-5xl font-light text-white mb-4 tracking-wide">
              {isLogin ? 'Welcome Back' : 'Begin Your Journey'}
            </h1>
            <div className="w-24 h-px bg-gradient-to-r from-transparent via-[#d4c4a8] to-transparent mx-auto opacity-40" />
          </div>

          <div className="bg-[#0a0d3a] bg-opacity-50 backdrop-blur-xl border border-[#d4c4a8] border-opacity-20 p-12">
            {/* Toggle Buttons */}
            <div className="flex gap-2 mb-8 bg-[#060824] bg-opacity-50 p-1 rounded">
              <button
                onClick={() => setIsLogin(true)}
                className={`flex-1 py-3 text-sm tracking-[0.15em] uppercase font-semibold transition-all ${
                  isLogin 
                    ? 'bg-[#d4c4a8] text-[#060824]' 
                    : 'text-[#d4c4a8] hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => setIsLogin(false)}
                className={`flex-1 py-3 text-sm tracking-[0.15em] uppercase font-semibold transition-all ${
                  !isLogin 
                    ? 'bg-[#d4c4a8] text-[#060824]' 
                    : 'text-[#d4c4a8] hover:text-white'
                }`}
              >
                Sign Up
              </button>
            </div>

            {error && (
              <motion.div
                className="mb-6 p-4 bg-red-500 bg-opacity-10 border border-red-500 border-opacity-30 rounded text-red-400 text-sm"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {error}
              </motion.div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-xs tracking-[0.2em] uppercase text-[#d4c4a8] opacity-70 mb-3">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-[#060824] bg-opacity-50 border border-[#d4c4a8] border-opacity-20 rounded text-white placeholder-[#d4c4a8] placeholder-opacity-30 focus:border-opacity-60 focus:outline-none transition"
                  placeholder="your@email.com"
                />
              </div>

              <div>
                <label className="block text-xs tracking-[0.2em] uppercase text-[#d4c4a8] opacity-70 mb-3">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full px-4 py-3 bg-[#060824] bg-opacity-50 border border-[#d4c4a8] border-opacity-20 rounded text-white placeholder-[#d4c4a8] placeholder-opacity-30 focus:border-opacity-60 focus:outline-none transition"
                  placeholder="••••••••"
                />
                {!isLogin && (
                  <p className="text-xs text-[#d4c4a8] opacity-40 mt-2">Minimum 8 characters</p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#d4c4a8] text-[#060824] py-4 text-sm tracking-[0.2em] uppercase font-bold hover:bg-[#e8e0cf] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                {loading ? 'Processing...' : isLogin ? 'Enter Mercato' : 'Create Account'}
              </button>
            </form>

            <div className="mt-8 text-center">
              <button
                onClick={() => navigate('/stocks')}
                className="text-[#d4c4a8] text-sm tracking-[0.1em] hover:text-white transition"
              >
                Continue as guest →
              </button>
            </div>
          </div>

          <p className="text-center text-[#d4c4a8] opacity-40 text-xs mt-8 tracking-wide">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-[#d4c4a8] hover:text-white transition underline"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </motion.div>
      </div>
    </div>
  );
}

export default LoginPage;
