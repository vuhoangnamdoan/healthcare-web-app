import React, { useState } from 'react';
import { Form, Button, Alert, Container, Row, Col, Card } from 'react-bootstrap';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser } from '../services/userService';

const Register = () => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await registerUser({
        first_name: firstName,
        last_name: lastName,
        email,
        password,
        password2,
        phone_number: phoneNumber,
        date_of_birth: dateOfBirth
      });
      navigate('/login');
    } catch (err) {
      const data = err.response?.data;
      setError(typeof data === 'string' ? data : JSON.stringify(data));
    }
  };

  return (
    <Container className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
      <Row className="w-100" style={{ maxWidth: '500px' }}>
        <Col>
          <Card>
            <Card.Body>
              <h3 className="mb-4 text-center">Register</h3>
              {error && <Alert variant="danger">{error}</Alert>}
              <Form onSubmit={handleSubmit}>
                <Row>
                  <Col>
                    <Form.Group className="mb-3" controlId="firstName">
                      <Form.Label>First Name</Form.Label>
                      <Form.Control type="text" value={firstName} onChange={e => setFirstName(e.target.value)} required />
                    </Form.Group>
                  </Col>
                  <Col>
                    <Form.Group className="mb-3" controlId="lastName">
                      <Form.Label>Last Name</Form.Label>
                      <Form.Control type="text" value={lastName} onChange={e => setLastName(e.target.value)} required />
                    </Form.Group>
                  </Col>
                </Row>
                <Form.Group className="mb-3" controlId="email">
                  <Form.Label>Email</Form.Label>
                  <Form.Control type="email" value={email} onChange={e => setEmail(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3" controlId="password">
                  <Form.Label>Password</Form.Label>
                  <Form.Control type="password" value={password} onChange={e => setPassword(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3" controlId="password2">
                  <Form.Label>Confirm Password</Form.Label>
                  <Form.Control type="password" value={password2} onChange={e => setPassword2(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3" controlId="phoneNumber">
                  <Form.Label>Phone Number</Form.Label>
                  <Form.Control type="tel" value={phoneNumber} onChange={e => setPhoneNumber(e.target.value)} />
                </Form.Group>
                <Form.Group className="mb-4" controlId="dateOfBirth">
                  <Form.Label>Date of Birth</Form.Label>
                  <Form.Control type="date" value={dateOfBirth} onChange={e => setDateOfBirth(e.target.value)} />
                </Form.Group>
                <Button variant="primary" type="submit" className="w-100">Register</Button>
              </Form>
              <div className="mt-3 text-center">
                Already have an account? <Link to="/login">Login</Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Register;
