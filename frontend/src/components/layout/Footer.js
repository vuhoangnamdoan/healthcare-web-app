import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFacebook, faLinkedin } from '@fortawesome/free-brands-svg-icons';

const Footer = () => {
  return (
    <footer className="footer bg-dark text-light py-4 position-relative" style={{ zIndex: 1000 }}>
      <Container fluid className="px-5">
        <Row>
          <Col md={4}>
            <p>
              <span className="me-3">About Us</span>
              <span className="me-3">Policy</span>
              <span>Terms of Use</span>
            </p>
            <p>2025 Hongnam Group. All rights reserved</p>
          </Col>
          <Col md={4} className="d-flex flex-column align-items-center">
            <p>Hongnam Hospital</p>
            <p>Building 1: Hanoi, Vietnam</p>
            <p>Building 2: Melbourne, Australia</p>
            <p>hongnam@hospital.com</p>
          </Col>
          <Col md={4} className="d-flex align-items-center justify-content-end gap-4">
            <button className="btn btn-link text-light hover-grow" style={{ textDecoration: 'none' }}>
              <FontAwesomeIcon icon={faFacebook} size="lg" />
            </button>
            <button className="btn btn-link text-light hover-grow" style={{ textDecoration: 'none' }}>
              <FontAwesomeIcon icon={faLinkedin} size="lg" />
            </button>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;