import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';

// Import pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Dashboard from './pages/common/Dashboard';
import PatientDashboard from './pages/patient/PatientDashboard';
import DoctorDashboard from './pages/doctor/DoctorDashboard';

import AppointmentBrowser from './pages/patient/AppointmentBrowser';
import MyAppointments from './pages/patient/MyAppointments';
import ProfileEdit from './pages/patient/ProfileEdit';

// Doctor pages
import AppointmentSlots from './pages/doctor/AppointmentSlots';
import DoctorProfile from './pages/doctor/DoctorProfile';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          {/* ✅ Add Navbar component */}
          <Navbar />
          <Routes>
            {/* Public routes */}
            <Route path="/auth/login" element={<Login />} />
            <Route path="/auth/register" element={<Register />} />
            
            {/* Protected routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            
            {/* Patient routes */}
            <Route path="/patient/dashboard" element={
              <ProtectedRoute>
                <PatientDashboard />
              </ProtectedRoute>
            } />
            {/* Patient feature routes */}
            <Route path="/patient/appointments/browse" element={
              <ProtectedRoute>
                <AppointmentBrowser />
              </ProtectedRoute>
            } />
            <Route path="/patient/appointments" element={
              <ProtectedRoute>
                <MyAppointments />
              </ProtectedRoute>
            } />
            <Route path="/patient/profile" element={
              <ProtectedRoute>
                <ProfileEdit />
              </ProtectedRoute>
            } />
            

            {/* Doctor routes */}
            <Route path="/doctor/dashboard" element={
              <ProtectedRoute>
                <DoctorDashboard />
              </ProtectedRoute>
            } />
            <Route path="/doctor/appointment-slots" element={
              <ProtectedRoute>
                <AppointmentSlots />
              </ProtectedRoute>
            } />
            <Route path="/doctor/profile" element={
              <ProtectedRoute>
                <DoctorProfile />
              </ProtectedRoute>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;