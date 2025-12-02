import axios from 'axios';

const API_BASE_URL = 'https://enlarge-webcams-showing-levels.trycloudflare.com';

export const api = {
  getLeaderboard: async (limit = 500) => {
    const response = await axios.get(`${API_BASE_URL}/leaderboard?limit=${limit}`);
    return response.data;
  },

  getStock: async (ticker) => {
    const response = await axios.get(`${API_BASE_URL}/stock/${ticker}`);
    return response.data;
  },

  getPortfolio: async (userId) => {
    const response = await axios.get(`${API_BASE_URL}/portfolio/${userId}`);
    return response.data;
  },

  addToPortfolio: async (userId, ticker, shares) => {
    const response = await axios.post(`${API_BASE_URL}/portfolio/${userId}/${ticker}`, {
      shares
    });
    return response.data;
  },

  updatePortfolio: async (userId, ticker, shares) => {
    const response = await axios.put(`${API_BASE_URL}/portfolio/${userId}/${ticker}`, {
      shares
    });
    return response.data;
  },

  removeFromPortfolio: async (userId, ticker) => {
    const response = await axios.delete(`${API_BASE_URL}/portfolio/${userId}/${ticker}`);
    return response.data;
  }
};
