import React, { useState } from 'react';
import { Form, Button, Alert, Container, Row, Col, Card, Spinner } from 'react-bootstrap';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../../services/api';

const Register = () => {
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [dateOfBirth, setDateOfBirth] = useState('');
    const [address, setAddress] = useState('');
    const [identityId, setIdentityId] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        try {
            await authAPI.register({
                first_name: firstName,
                last_name: lastName,
                email,
                password,
                password2,
                phone: phoneNumber,
                dob: dateOfBirth,
                address1: address,
                city: "Default City",
                state: "Default State",
                zip_code: "00000",
                identity_id: identityId
            });
            
            navigate('/auth/login', {
                state: { message: 'Registration successful! Please login.' }
            });
        } catch (err) {
            const data = err.response?.data;
            if (data) {
                if (typeof data === 'string') {
                    setError(data);
                } else if (data.detail) {
                    setError(data.detail);
                } else {
                    const errorMessages = Object.entries(data)
                        .map(([field, messages]) => {
                            const messageArray = Array.isArray(messages) ? messages : [messages];
                            return `${field}: ${messageArray.join(', ')}`;
                        })
                        .join('\n');
                    setError(errorMessages);
                }
            } else {
                setError('Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh', paddingY: '2rem' }}>
            <Row className="w-100" style={{ maxWidth: '500px' }}>
                <Col>
                    <Card>
                        <Card.Body>
                            <h3 className="mb-4 text-center">Patient Registration</h3>
                            
                            {error && (
                                <Alert variant="danger" style={{ whiteSpace: 'pre-line' }}>
                                    {error}
                                </Alert>
                            )}
                            
                            <Form onSubmit={handleSubmit}>
                                <Row>
                                    <Col md={6}>
                                        <Form.Group className="mb-3" controlId="firstName">
                                            <Form.Label>First Name</Form.Label>
                                            <Form.Control 
                                                type="text" 
                                                value={firstName} 
                                                onChange={e => setFirstName(e.target.value)} 
                                                required 
                                                disabled={loading}
                                            />
                                        </Form.Group>
                                    </Col>
                                    <Col md={6}>
                                        <Form.Group className="mb-3" controlId="lastName">
                                            <Form.Label>Last Name</Form.Label>
                                            <Form.Control 
                                                type="text" 
                                                value={lastName} 
                                                onChange={e => setLastName(e.target.value)} 
                                                required 
                                                disabled={loading}
                                            />
                                        </Form.Group>
                                    </Col>
                                </Row>

                                <Form.Group className="mb-3" controlId="email">
                                    <Form.Label>Email Address</Form.Label>
                                    <Form.Control 
                                        type="email" 
                                        value={email} 
                                        onChange={e => setEmail(e.target.value)} 
                                        required 
                                        disabled={loading}
                                    />
                                </Form.Group>

                                <Form.Group className="mb-3" controlId="password">
                                    <Form.Label>Password</Form.Label>
                                    <Form.Control 
                                        type="password" 
                                        value={password} 
                                        onChange={e => setPassword(e.target.value)} 
                                        required 
                                        disabled={loading}
                                    />
                                </Form.Group>

                                <Form.Group className="mb-3" controlId="password2">
                                    <Form.Label>Confirm Password</Form.Label>
                                    <Form.Control 
                                        type="password" 
                                        value={password2} 
                                        onChange={e => setPassword2(e.target.value)} 
                                        required 
                                        disabled={loading}
                                    />
                                </Form.Group>

                                <Form.Group className="mb-3" controlId="phoneNumber">
                                    <Form.Label>Phone Number</Form.Label>
                                    <Form.Control 
                                        type="tel" 
                                        value={phoneNumber} 
                                        onChange={e => setPhoneNumber(e.target.value)} 
                                        required
                                        disabled={loading}
                                    />
                                </Form.Group>

                                <Form.Group className="mb-3" controlId="dateOfBirth">
                                    <Form.Label>Date of Birth</Form.Label>
                                    <Form.Control 
                                        type="date" 
                                        value={dateOfBirth} 
                                        onChange={e => setDateOfBirth(e.target.value)} 
                                        required
                                        disabled={loading}
                                    />
                                </Form.Group>

                                <Form.Group className="mb-3" controlId="address">
                                    <Form.Label>Address</Form.Label>
                                    <Form.Control 
                                        as="textarea"
                                        rows={2}
                                        value={address} 
                                        onChange={e => setAddress(e.target.value)} 
                                        placeholder="Enter your full address"
                                        required
                                        disabled={loading}
                                    />
                                </Form.Group>

                                <Form.Group className="mb-4" controlId="identityId">
                                    <Form.Label>Identity ID</Form.Label>
                                    <Form.Control 
                                        type="text" 
                                        value={identityId} 
                                        onChange={e => setIdentityId(e.target.value)} 
                                        placeholder="Enter your national ID or passport number"
                                        required
                                        disabled={loading}
                                    />
                                    <Form.Text className="text-muted">
                                        Enter your national ID, passport number, or other government-issued ID
                                    </Form.Text>
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
                                            Registering...
                                        </>
                                    ) : (
                                        'Register'
                                    )}
                                </Button>
                            </Form>
                            
                            <div className="mt-3 text-center">
                                Already have an account? <Link to="/auth/login">Login</Link>
                            </div>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default Register;