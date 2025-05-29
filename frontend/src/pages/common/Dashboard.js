import React, { useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { Spinner, Container } from 'react-bootstrap';

const Dashboard = () => {
    const { user, loading } = useContext(AuthContext);
    const navigate = useNavigate();

    useEffect(() => {
        if (!loading && user) {
            // Route based on user role
            if (user.role === 'patient') {
                navigate('/patient/dashboard');
            } else if (user.role === 'doctor') {
                navigate('/doctor/dashboard');
            } else {
                navigate('/auth/login');
            }
        } else if (!loading && !user) {
            navigate('/auth/login');
        }
    }, [user, loading, navigate]);

    if (loading) {
        return (
        <Container className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
            <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
            </Spinner>
        </Container>
        );
    }

    return null;
};

export default Dashboard;