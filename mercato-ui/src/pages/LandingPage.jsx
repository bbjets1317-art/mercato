import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

function LandingPage() {
  const navigate = useNavigate();
  const [selectedFeature, setSelectedFeature] = useState(null);
  const [showPillars, setShowPillars] = useState(false);

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const pillars = [
    {
      name: "Financial Health",
      description: "Balance sheet strength, liquidity ratios, and debt management",
      metrics: "Current Ratio • Debt-to-Equity • Working Capital",
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    },
    {
      name: "Profitability",
      description: "Earnings power, margin efficiency, and return on capital",
      metrics: "ROE • Operating Margin • Net Profit Margin",
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
        </svg>
      )
    },
    {
      name: "Growth",
      description: "Revenue expansion, earnings growth, and market share gains",
      metrics: "Revenue Growth • EPS Growth • Market Cap Trends",
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
        </svg>
      )
    },
    {
      name: "Momentum",
      description: "Price action, trading volume, and technical strength",
      metrics: "Price Trends • Relative Strength • Volume Analysis",
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-3 2.148 2.148A12.061 12.061 0 0116.5 7.605" />
        </svg>
      )
    },
    {
      name: "Safety",
      description: "Risk management, volatility analysis, and downside protection",
      metrics: "Beta • Volatility • Sharpe Ratio",
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
        </svg>
      )
    }
  ];

  const features = [
    {
      title: "Five Pillars of Analysis",
      subtitle: "Financial Health • Profitability • Growth • Momentum • Safety",
      description: "Our proprietary algorithm examines every stock through five fundamental lenses. Each pillar represents decades of financial wisdom, distilled into a singular, actionable score.",
      details: "We analyze balance sheets, income statements, cash flows, and market data to provide a comprehensive view. No stone is left unturned in our pursuit of investment clarity."
    },
    {
      title: "Machine Intelligence",
      subtitle: "Trained on Market Fundamentals",
      description: "Six independent machine learning models work in concert, each specialized in a distinct aspect of financial analysis. The result: objective, data-driven insights free from human bias.",
      details: "Our models are continuously refined using the latest market data, ensuring your analysis stays ahead of the curve. What would take an analyst days, we deliver in seconds."
    },
    {
      title: "Portfolio Mastery",
      subtitle: "Track • Analyze • Optimize",
      description: "Build your portfolio with precision. Monitor score evolution over time. Understand not just what you own, but why you own it.",
      details: "Real-time updates, historical tracking, and comprehensive analytics give you institutional-grade portfolio management in an elegantly simple interface."
    }
  ];

  return (
    <div className="min-h-screen bg-[#060824]">
      {/* Hero Section */}
      <motion.section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-[#060824] via-[#0a0d3a] to-[#0e1249]">
        {/* Premium Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(200, 180, 150, 0.15) 1px, transparent 0)',
            backgroundSize: '40px 40px'
          }} />
        </div>

        {/* Animated Gradient Orbs */}
        <motion.div
          className="absolute w-[800px] h-[800px] rounded-full blur-3xl"
          style={{
            background: 'radial-gradient(circle, rgba(200, 180, 150, 0.15) 0%, transparent 70%)',
            top: '-20%',
            left: '-20%'
          }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.15, 0.25, 0.15]
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        <motion.div
          className="absolute w-[600px] h-[600px] rounded-full blur-3xl"
          style={{
            background: 'radial-gradient(circle, rgba(139, 115, 85, 0.12) 0%, transparent 70%)',
            bottom: '-15%',
            right: '-15%'
          }}
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.12, 0.18, 0.12]
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />

        {/* Decorative Logo Elements */}
        <img 
          src="/mercato-logo.png" 
          alt="" 
          className="absolute top-32 left-12 h-32 opacity-5 rotate-12"
        />
        <img 
          src="/mercato-logo.png" 
          alt="" 
          className="absolute bottom-32 right-12 h-40 opacity-5 -rotate-12"
        />

        {/* Header - Fixed at top */}
        <motion.nav 
          className="fixed top-0 w-full z-50 backdrop-blur-lg bg-[#060824] bg-opacity-90 border-b border-[#d4c4a8] border-opacity-10"
          initial={{ y: -100 }}
          animate={{ y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="container mx-auto px-8 py-5 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <img src="/mercato-logo.png" alt="Mercato" className="h-11" />
              <span className="text-xl font-light tracking-[0.3em] text-[#d4c4a8]">MERCATO</span>
            </div>
            <div className="flex gap-8 items-center">
              <button
                onClick={() => navigate('/login')}
                className="text-[#d4c4a8] hover:text-white transition text-sm tracking-[0.2em] uppercase"
              >
                Sign In
              </button>
              <button
                onClick={() => navigate('/login')}
                className="bg-[#d4c4a8] text-[#060824] hover:bg-[#e8e0cf] transition px-8 py-2.5 text-sm tracking-[0.2em] uppercase font-semibold shadow-lg"
              >
                Begin
              </button>
            </div>
          </div>
        </motion.nav>

        {/* Hero Content - Added more top padding to clear header */}
        <div className="relative z-10 container mx-auto px-8 text-center pt-40">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ duration: 1, delay: 0.3 }}
          >
            <h1 className="text-8xl font-light text-white mb-4 tracking-tight leading-tight drop-shadow-2xl">
              Investment Intelligence,
              <br />
              <span className="font-normal text-[#d4c4a8]">Refined.</span>
            </h1>
          </motion.div>

          <motion.div
            className="w-32 h-px bg-gradient-to-r from-transparent via-[#d4c4a8] to-transparent mx-auto my-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.6 }}
            transition={{ duration: 1, delay: 0.8 }}
          />

          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ duration: 1, delay: 0.5 }}
            className="mb-8"
          >
            <p className="text-5xl text-white font-light tracking-[0.25em] mb-4 drop-shadow-2xl">
              MARKETS MADE SIMPLE
            </p>
            <p className="text-2xl text-[#d4c4a8] font-light tracking-[0.2em] drop-shadow-lg">
              Quantitative Scoring, Refined
            </p>
          </motion.div>

          <motion.p
            className="text-lg text-white opacity-70 mb-16 max-w-2xl mx-auto font-light tracking-wide leading-relaxed drop-shadow-md"
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ duration: 1, delay: 0.7 }}
          >
            Six machine learning models distill market complexity into singular, actionable insights.
          </motion.p>

          <motion.div
            className="flex gap-6 justify-center mb-12"
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ duration: 1, delay: 0.9 }}
          >
            <motion.button
              onClick={() => navigate('/login')}
              className="bg-[#d4c4a8] text-[#060824] px-14 py-5 text-lg font-bold tracking-[0.15em] uppercase hover:bg-[#e8e0cf] transition-all shadow-2xl"
              whileHover={{ scale: 1.03, boxShadow: "0 25px 50px -12px rgba(212, 196, 168, 0.6)" }}
              whileTap={{ scale: 0.98 }}
            >
              Enter Mercato
            </motion.button>
            <motion.button
              onClick={() => navigate('/stocks')}
              className="border-2 border-[#d4c4a8] border-opacity-60 text-white px-14 py-5 text-lg font-semibold tracking-[0.15em] uppercase hover:bg-[#d4c4a8] hover:bg-opacity-10 hover:border-opacity-100 transition-all backdrop-blur-sm"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
            >
              View Analysis
            </motion.button>
          </motion.div>

          {/* Five Pillars CTA */}
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ duration: 1, delay: 1.1 }}
            className="mb-24"
          >
            <button
              onClick={() => setShowPillars(!showPillars)}
              className="text-[#d4c4a8] hover:text-white transition text-sm tracking-[0.2em] uppercase flex items-center gap-2 mx-auto border border-[#d4c4a8] border-opacity-30 hover:border-opacity-60 px-8 py-3 backdrop-blur-sm"
            >
              <span>Explore The Five Pillars</span>
              <motion.svg 
                className="w-4 h-4" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                viewBox="0 0 24 24"
                animate={{ rotate: showPillars ? 180 : 0 }}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
              </motion.svg>
            </button>
          </motion.div>

          {/* Pillars Expandable Section */}
          <AnimatePresence>
            {showPillars && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-24"
              >
                <div className="grid grid-cols-5 gap-4 max-w-6xl mx-auto">
                  {pillars.map((pillar, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-[#0e1249] bg-opacity-50 backdrop-blur-md border border-[#d4c4a8] border-opacity-20 p-6 hover:border-opacity-40 transition-all"
                    >
                      <div className="text-[#d4c4a8] opacity-40 mb-4">{pillar.icon}</div>
                      <h4 className="text-white font-semibold mb-2 tracking-wide">{pillar.name}</h4>
                      <p className="text-[#d4c4a8] text-xs opacity-70 mb-3 leading-relaxed">{pillar.description}</p>
                      <p className="text-[#d4c4a8] text-xs opacity-40 leading-relaxed">{pillar.metrics}</p>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <motion.div
            className="flex justify-center gap-24 text-white"
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ duration: 1, delay: 1.3 }}
          >
            <div className="text-center">
              <div className="text-6xl font-light mb-2 text-[#d4c4a8] drop-shadow-lg">550+</div>
              <div className="text-xs tracking-[0.2em] uppercase opacity-60">Securities</div>
            </div>
            <div className="w-px bg-[#d4c4a8] opacity-20" />
            <div className="text-center">
              <div className="text-6xl font-light mb-2 text-[#d4c4a8] drop-shadow-lg">Five</div>
              <div className="text-xs tracking-[0.2em] uppercase opacity-60">Pillars</div>
            </div>
            <div className="w-px bg-[#d4c4a8] opacity-20" />
            <div className="text-center">
              <div className="text-6xl font-light mb-2 text-[#d4c4a8] drop-shadow-lg">Weekly</div>
              <div className="text-xs tracking-[0.2em] uppercase opacity-60">Updates</div>
            </div>
          </motion.div>
        </div>

        {/* Scroll Indicator */}
        <motion.div
          className="absolute bottom-12 left-1/2 transform -translate-x-1/2"
          animate={{ y: [0, 12, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="w-6 h-10 border-2 border-[#d4c4a8] border-opacity-30 rounded-full p-1">
            <motion.div 
              className="w-1.5 h-1.5 bg-[#d4c4a8] bg-opacity-60 rounded-full mx-auto"
              animate={{ y: [0, 20, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </div>
        </motion.div>
      </motion.section>

      {/* Features Section */}
      <section className="py-32 bg-gradient-to-b from-[#0e1249] to-[#060824]">
        <div className="container mx-auto px-8">
          <motion.div
            className="text-center mb-20"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
          >
            <h2 className="text-6xl font-light text-white mb-4">The Mercato Method</h2>
            <div className="w-32 h-px bg-gradient-to-r from-transparent via-[#d4c4a8] to-transparent mx-auto mt-8 opacity-40" />
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                className="group cursor-pointer"
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeIn}
                transition={{ delay: index * 0.15 }}
                onClick={() => setSelectedFeature(selectedFeature === index ? null : index)}
              >
                <div className="bg-[#0a0d3a] bg-opacity-50 backdrop-blur-sm p-12 h-full border border-[#d4c4a8] border-opacity-15 hover:border-opacity-35 hover:bg-opacity-70 transition-all duration-500 shadow-xl">
                  <div className="mb-8">
                    <svg className="w-14 h-14 text-[#d4c4a8] opacity-40 group-hover:opacity-80 transition-opacity duration-500" fill="none" stroke="currentColor" strokeWidth="1" viewBox="0 0 24 24">
                      {index === 0 && <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />}
                      {index === 1 && <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />}
                      {index === 2 && <path strokeLinecap="round" strokeLinejoin="round" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />}
                    </svg>
                  </div>
                  
                  <h3 className="text-2xl font-light text-white mb-3 tracking-wide">{feature.title}</h3>
                  <p className="text-xs tracking-[0.15em] uppercase text-[#d4c4a8] opacity-50 mb-6">{feature.subtitle}</p>
                  
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: selectedFeature === index ? 'auto' : 0 }}
                    className="overflow-hidden"
                  >
                    <p className="text-white opacity-70 leading-relaxed mb-4">{feature.description}</p>
                    <p className="text-[#d4c4a8] opacity-50 text-sm leading-relaxed">{feature.details}</p>
                  </motion.div>
                  
                  {selectedFeature !== index && (
                    <p className="text-white opacity-70 leading-relaxed">{feature.description}</p>
                  )}
                  
                  <div className="mt-6 flex items-center text-[#d4c4a8] opacity-40 group-hover:opacity-80 transition-opacity text-sm tracking-[0.1em]">
                    <span className="uppercase">{selectedFeature === index ? 'Less' : 'Learn More'}</span>
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 bg-gradient-to-b from-[#060824] via-[#0a0d3a] to-[#060824] relative overflow-hidden">
        <div className="absolute inset-0 opacity-3">
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-gradient-to-br from-[#d4c4a8] to-transparent blur-3xl" />
        </div>
        
        <div className="container mx-auto px-8 text-center relative z-10">
          <motion.h2
            className="text-7xl font-light text-white mb-6 drop-shadow-2xl"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
          >
            Begin Your Journey
          </motion.h2>
          
          <motion.div
            className="w-32 h-px bg-gradient-to-r from-transparent via-[#d4c4a8] to-transparent mx-auto my-12"
            initial={{ width: 0, opacity: 0 }}
            whileInView={{ width: 128, opacity: 0.5 }}
            viewport={{ once: true }}
            transition={{ duration: 1 }}
          />

          <motion.p
            className="text-xl text-white opacity-70 mb-16 max-w-2xl mx-auto font-light leading-relaxed drop-shadow-lg"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
            transition={{ delay: 0.2 }}
          >
            Join the select few who refuse to invest in the dark.
          </motion.p>
          
          <motion.button
            onClick={() => navigate('/login')}
            className="bg-[#d4c4a8] text-[#060824] px-20 py-7 text-xl font-bold tracking-[0.2em] uppercase hover:bg-[#e8e0cf] transition-all shadow-2xl"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeIn}
            transition={{ delay: 0.4 }}
            whileHover={{ scale: 1.03, boxShadow: "0 25px 50px -12px rgba(212, 196, 168, 0.7)" }}
            whileTap={{ scale: 0.98 }}
          >
            Enter Mercato
          </motion.button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#040616] py-12 border-t border-[#d4c4a8] border-opacity-10">
        <div className="container mx-auto px-8 text-center">
          <p className="text-[#d4c4a8] opacity-30 text-xs tracking-[0.2em]">© MMXXV MERCATO • MARKETS MADE SIMPLE</p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
