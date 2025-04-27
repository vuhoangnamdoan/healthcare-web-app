import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Spinner, Form, InputGroup } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { getDoctors } from '../services/doctorService';
import Layout from '../components/layout/Layout';

const DoctorList = () => {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [specializations, setSpecializations] = useState([]);

  useEffect(() => {
    const fetchDoctors = async () => {
      try {
        setLoading(true);
        const data = await getDoctors();
        setDoctors(data);
        
        // Extract unique specializations for filter
        const uniqueSpecializations = [...new Set(data.map(doctor => 
          doctor.doctor_profile?.specialization
        ).filter(Boolean))];
        
        setSpecializations(uniqueSpecializations);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching doctors:', err);
        setError('Failed to load doctors. Please try again later.');
        setLoading(false);
      }
    };

    fetchDoctors();
  }, []);

  // Filter doctors based on search term and specialization
  const filteredDoctors = doctors.filter(doctor => {
    const fullName = `${doctor.first_name} ${doctor.last_name}`.toLowerCase();
    const doctorSpecialization = doctor.doctor_profile?.specialization || '';
    
    const matchesSearch = searchTerm === '' || 
      fullName.includes(searchTerm.toLowerCase()) ||
      doctorSpecialization.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSpecialization = specialization === '' || 
      doctorSpecialization === specialization;
    
    return matchesSearch && matchesSpecialization;
  });

  if (loading) {
    return (
      <Layout>
        <Container className="mt-5 text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </Container>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <Container className="mt-5">
          <div className="alert alert-danger">{error}</div>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container className="mt-4">
        <h2 className="mb-4">Available Doctors</h2>
        
        <Row className="mb-4">
          <Col md={6}>
            <InputGroup>
              <Form.Control
                placeholder="Search by name or specialization"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <Button 
                  variant="outline-secondary"
                  onClick={() => setSearchTerm('')}
                >
                  Clear
                </Button>
              )}
            </InputGroup>
          </Col>
          <Col md={6}>
            <Form.Select
              value={specialization}
              onChange={(e) => setSpecialization(e.target.value)}
            >
              <option value="">All Specializations</option>
              {specializations.map((spec, index) => (
                <option key={index} value={spec}>{spec}</option>
              ))}
            </Form.Select>
          </Col>
        </Row>
        
        {filteredDoctors.length === 0 ? (
          <div className="alert alert-info">No doctors match your search criteria.</div>
        ) : (
          <Row>
            {filteredDoctors.map((doctor) => (
              <Col key={doctor.id} md={6} lg={4} className="mb-4">
                <Card className="h-100 shadow-sm">
                  <Card.Body>
                    <Card.Title>{doctor.first_name} {doctor.last_name}</Card.Title>
                    
                    {doctor.doctor_profile && (
                      <>
                        <div className="mb-2 text-muted">
                          <strong>Specialization:</strong> {doctor.doctor_profile.specialization}
                        </div>
                        <div className="mb-2">
                          <strong>Experience:</strong> {doctor.doctor_profile.years_of_experience} years
                        </div>
                        <div className="mb-3">
                          <strong>Doctor ID:</strong> {doctor.doctor_profile.doctor_id}
                        </div>
                      </>
                    )}
                    
                    <Link to={`/book-appointment/${doctor.doctor_profile?.doctor_id || doctor.id}`}>
                      <Button variant="primary" className="w-100">Book Appointment</Button>
                    </Link>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Container>
    </Layout>
  );
};

export default DoctorList;