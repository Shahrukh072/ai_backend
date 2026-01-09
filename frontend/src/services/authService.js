import api from './api';

export const authService = {
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  login: async (credentials) => {
    try {
      const response = await api.post('/api/auth/login', credentials);
      // TODO: Switch to HttpOnly cookies instead of localStorage for token storage
      // For now, rely on server to set HttpOnly cookie and don't store in localStorage
      // if (response.data.access_token) {
      //   localStorage.setItem('token', response.data.access_token);
      // }
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  loginWithGoogle: async (googleToken) => {
    try {
      const response = await api.post('/api/auth/google', { token: googleToken });
      // TODO: Switch to HttpOnly cookies instead of localStorage for token storage
      // For now, rely on server to set HttpOnly cookie and don't store in localStorage
      // if (response.data.access_token) {
      //   localStorage.setItem('token', response.data.access_token);
      // }
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getCurrentUser: async () => {
    try {
      const response = await api.get('/api/auth/me');
      // Persist user data
      if (response.data) {
        localStorage.setItem('user', JSON.stringify(response.data));
      }
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};

