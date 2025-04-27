import React from 'react';
import { Container } from 'react-bootstrap';
import Header from './Header';
import Footer from './Footer';
import Sidebar from './Sidebar';

const Layout = ({ children }) => {
  return (
    <>
      <Header />
      <Sidebar />
      <main style={{ marginTop: '70px', marginLeft: '200px', marginBottom: '80px' }}>
        <Container className="py-4">
          {children}
        </Container>
      </main>
      <Footer />
    </>
  );
};

export default Layout;