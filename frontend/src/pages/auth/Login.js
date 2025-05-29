import React, { useState, useContext } from 'react';
import { Form, Button, Alert, Container, Row, Col, Card, Spinner } from 'react-bootstrap';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();
    const location = useLocation();

    const successMessage = location.state?.message;
    const from = location.state?.from?.pathname || '/';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        try {
            await login(email, password);
            navigate(from, { replace: true });
        } catch (err) {
            setError('Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh', paddingY: '2rem' }}>
            <Row className="w-100" style={{ maxWidth: '400px' }}>
                <Col>
                    <Card>
                        <Card.Body>
                            <div className="text-center mb-4">
                                <h3>Hong Nam Healthcare</h3>
                                <p className="text-muted">Sign in to your account</p>
                            </div>
                            
                            {successMessage && (
                                <Alert variant="success" className="mb-3">
                                    {successMessage}
                                </Alert>
                            )}
                            
                            {error && (
                                <Alert variant="danger" className="mb-3">
                                    {error}
                                </Alert>
                            )}
                            
                            <Form onSubmit={handleSubmit}>
                                <Form.Group className="mb-3" controlId="email">
                                    <Form.Label>Email Address</Form.Label>
                                    <Form.Control
                                        type="email"
                                        placeholder="Enter your email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        autoFocus
                                        disabled={loading}
                                    />
                                </Form.Group>
                                
                                <Form.Group className="mb-3" controlId="password">
                                    <Form.Label>Password</Form.Label>
                                    <Form.Control
                                        type="password"
                                        placeholder="Enter your password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        disabled={loading}
                                    />
                                </Form.Group>
                                
                                <Button 
                                    variant="primary" 
                                    type="submit" 
                                    className="w-100"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <Spinner
                                                as="span"
                                                animation="border"
                                                size="sm"
                                                role="status"
                                                aria-hidden="true"
                                                className="me-2"
                                            />
                                            Signing in...
                                        </>
                                    ) : (
                                        'Sign In'
                                    )}
                                </Button>
                            </Form>
                            
                            <hr className="my-4" />
                            
                            <div className="text-center">
                                <p className="mb-2">Don't have an account?</p>
                                <Link to="/auth/register" className="btn btn-outline-primary w-100">
                                    Register as Patient
                                </Link>
                            </div>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default Login;