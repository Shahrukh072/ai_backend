import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      authService
        .getCurrentUser()
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials) => {
    try {
      const data = await authService.login(credentials);
      const userData = await authService.getCurrentUser();
      setUser(userData);
      return data;
    } catch (error) {
      // Rollback token on error
      authService.logout();
      setUser(null);
      throw error;
    }
  };

  const register = async (userData) => {
    // Validate input
    if (!userData.email || !userData.password) {
      throw new Error('Email and password are required');
    }
    
    try {
      await authService.register(userData);
      // Auto-login after registration
      try {
        await login({ email: userData.email, password: userData.password });
      } catch (loginError) {
        // Registration succeeded but login failed
        throw new Error('Registration successful, but automatic login failed. Please sign in manually.');
      }
    } catch (error) {
      throw error;
    }
  };

  const loginWithGoogle = async (googleToken) => {
    try {
      const data = await authService.loginWithGoogle(googleToken);
      const userData = await authService.getCurrentUser();
      setUser(userData);
      return data;
    } catch (error) {
      // Rollback token on error
      authService.logout();
      setUser(null);
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loginWithGoogle, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

