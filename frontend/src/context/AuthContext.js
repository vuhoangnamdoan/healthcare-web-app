import React, { createContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Check if user is logged in on app start
    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            // Verify token and get user profile
            authAPI.getProfile()
                .then(response => {
                    const userData = {
                        user_id: response.data.user.user_id,
                        email: response.data.user.email,
                        first_name: response.data.user.first_name,
                        last_name: response.data.user.last_name,
                        role: response.data.user.role,
                        // Store the complete profile data
                        profile: response.data.profile,
                        fullProfileData: response.data
                    };
                    setUser(userData);
                })
                .catch(() => {
                    // Token invalid, clear storage
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('refreshToken');
                })
                .finally(() => {
                    setLoading(false);
                });
        } else {
            setLoading(false);
        }
    }, []);

    const login = async (email, password) => {
        try {
            console.log('🔍 DEBUG: AuthContext - Starting login...'); // Add debug log
            
            // Call your backend login endpoint
            const response = await authAPI.login({ email, password });
            
            console.log('✅ DEBUG: Token response:', response.data); // Add debug log

            const { access, refresh } = response.data;
            
            // Store tokens
            localStorage.setItem('accessToken', access);
            localStorage.setItem('refreshToken', refresh);
            
            // Get user profile separately
            const profileResponse = await authAPI.getProfile();
            
            const userData = {
                user_id: profileResponse.data.user.user_id,
                email: profileResponse.data.user.email,
                first_name: profileResponse.data.user.first_name,
                last_name: profileResponse.data.user.last_name,
                role: profileResponse.data.user.role,
                // Store the complete profile data
                profile: profileResponse.data.profile,
                fullProfileData: profileResponse.data
            };

            setUser(userData);
            
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        setUser(null);
    };

    const value = {
        user,
        login,
        logout,
        loading
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};