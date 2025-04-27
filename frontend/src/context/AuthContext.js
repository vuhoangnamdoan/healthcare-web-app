import React, { createContext, useState, useEffect } from 'react';
import { loginUser, fetchUserProfile } from '../services/userService';

export const AuthContext = createContext({ user: null, login: async () => {}, logout: () => {} });

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  // Load user if tokens exist
  useEffect(() => {
    const init = async () => {
      try {
        const profile = await fetchUserProfile();
        setUser(profile);
      } catch {
        setUser(null);
      }
    };
    init();
  }, []);

  const login = async (email, password) => {
    const data = await loginUser(email, password);
    localStorage.setItem('accessToken', data.access);
    localStorage.setItem('refreshToken', data.refresh);
    setUser(data.user);
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
