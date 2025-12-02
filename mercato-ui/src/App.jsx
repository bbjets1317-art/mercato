import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import HomePage from './pages/HomePage'
import StockDetailPage from './pages/StockDetailPage'
import PortfolioPage from './pages/PortfolioPage'
import LoginPage from './pages/LoginPage'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/stocks" element={<HomePage />} />
        <Route path="/stock/:ticker" element={<StockDetailPage />} />
        <Route path="/portfolio" element={<PortfolioPage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
