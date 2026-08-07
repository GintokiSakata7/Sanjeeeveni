import React, { useState } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import CitizenSosPage from './pages/CitizenSosPage';
import HospitalLoginPage from './modules/auth/pages/HospitalLoginPage';
import HospitalRegistrationPage from './modules/hospital/pages/HospitalRegistrationPage';
import HospitalPortalDashboard from './modules/hospital/dashboard/HospitalPortalDashboard';
import AdminLoginPage from './modules/admin/pages/AdminLoginPage';
import AdminDashboardPage from './modules/admin/pages/AdminDashboardPage';

export default function App() {
  const navigate = useNavigate();
  const [selectedLang, setSelectedLang] = useState('auto');

  const [hospitalSession, setHospitalSession] = useState(() => {
    try {
      const saved = localStorage.getItem('sanjeevani_hospital_session');
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      return null;
    }
  });

  const [adminUser, setAdminUser] = useState(() => {
    try {
      const saved = localStorage.getItem('sanjeevani_admin_user');
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      return null;
    }
  });

  const handleHospitalLoginSuccess = (sessionData) => {
    setHospitalSession(sessionData);
    localStorage.setItem('sanjeevani_hospital_session', JSON.stringify(sessionData));
    navigate('/hospital/dashboard');
  };

  const handleHospitalLogout = () => {
    localStorage.removeItem('sanjeevani_hospital_session');
    setHospitalSession(null);
    navigate('/');
  };

  const handleAdminLoginSuccess = (userData) => {
    setAdminUser(userData);
    navigate('/admin/dashboard');
  };

  const handleAdminLogout = () => {
    localStorage.removeItem('sanjeevani_admin_token');
    localStorage.removeItem('sanjeevani_admin_user');
    setAdminUser(null);
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      <Routes>
        <Route 
          path="/" 
          element={
            <CitizenSosPage
              selectedLang={selectedLang}
              setSelectedLang={setSelectedLang}
              onOpenHospitalLogin={() => navigate(hospitalSession ? '/hospital/dashboard' : '/hospital/login')}
              onOpenAdminLogin={() => navigate(adminUser ? '/admin/dashboard' : '/admin/login')}
            />
          } 
        />

        <Route 
          path="/hospital/login" 
          element={
            <HospitalLoginPage
              onBackToCitizen={() => navigate('/')}
              onStartRegistration={() => navigate('/hospital/register')}
              onHospitalLoginSuccess={handleHospitalLoginSuccess}
            />
          } 
        />

        <Route 
          path="/hospital/register" 
          element={
            <HospitalRegistrationPage
              onBackToCitizen={() => navigate('/')}
              onOpenLoginModal={() => navigate('/hospital/login')}
            />
          } 
        />

        <Route 
          path="/hospital/dashboard" 
          element={
            hospitalSession ? (
              <HospitalPortalDashboard
                hospitalSession={hospitalSession}
                onLogout={handleHospitalLogout}
                onBackToCitizen={() => navigate('/')}
              />
            ) : (
              <Navigate to="/hospital/login" replace />
            )
          } 
        />

        <Route 
          path="/admin/login" 
          element={
            <AdminLoginPage
              onAdminLoginSuccess={handleAdminLoginSuccess}
              onBackToCitizen={() => navigate('/')}
            />
          } 
        />

        <Route 
          path="/admin/dashboard" 
          element={
            adminUser ? (
              <AdminDashboardPage
                adminUser={adminUser}
                onLogout={handleAdminLogout}
                onBackToCitizen={() => navigate('/')}
              />
            ) : (
              <Navigate to="/admin/login" replace />
            )
          } 
        />
        
        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
