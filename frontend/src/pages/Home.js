import React from 'react';
import Layout from '../components/layout/Layout';

const Home = () => (
  <Layout>
    <div style={{
      position: 'relative',
      height: 'calc(100vh - 120px)',
      backgroundImage: "url('https://source.unsplash.com/1600x900/?hospital')",
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }}>
      <div style={{
        position: 'absolute',
        top: '50%',
        right: '5%',
        transform: 'translateY(-50%)',
        backgroundColor: 'rgba(255,255,255,0.8)',
        padding: '20px',
        maxWidth: '400px'
      }}>
        <p>Welcome to Hongnam Hospital. We provide high-quality healthcare services to our community. Stay tuned for more updates.</p>
      </div>
    </div>
  </Layout>
);

export default Home;