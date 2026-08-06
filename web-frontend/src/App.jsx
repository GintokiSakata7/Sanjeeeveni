import React, { useState } from 'react';
import CitizenSosPage from './pages/CitizenSosPage';
import HospitalLoginPage from './modules/auth/pages/HospitalLoginPage';
import HospitalRegistrationPage from './modules/hospital/pages/HospitalRegistrationPage';
import AdminLoginPage from './modules/admin/pages/AdminLoginPage';
import AdminDashboardPage from './modules/admin/pages/AdminDashboardPage';

export default function App() {
  // Navigation View State: 'CITIZEN' | 'HOSPITAL_LOGIN' | 'HOSPITAL_REGISTRATION' | 'ADMIN_LOGIN' | 'ADMIN_DASHBOARD'
  const [currentView, setCurrentView] = useState('CITIZEN');
  const [selectedLang, setSelectedLang] = useState('auto');
  const [adminUser, setAdminUser] = useState(() => {
    try {
      const saved = localStorage.getItem('sanjeevani_admin_user');
      return saved ? JSON.parse(saved) : null;

    } catch (e) {
      return null;
    }
  });

  const handleAdminLoginSuccess = (userData) => {
    setAdminUser(userData);
    setCurrentView('ADMIN_DASHBOARD');
  };

  const handleAdminLogout = () => {
    localStorage.removeItem('sanjeevani_admin_token');
    localStorage.removeItem('sanjeevani_admin_user');
    setAdminUser(null);
    setCurrentView('CITIZEN');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      {currentView === 'CITIZEN' && (
        <CitizenSosPage
          selectedLang={selectedLang}
          setSelectedLang={setSelectedLang}
          onOpenHospitalLogin={() => setCurrentView('HOSPITAL_LOGIN')}
          onOpenAdminLogin={() => setCurrentView(adminUser ? 'ADMIN_DASHBOARD' : 'ADMIN_LOGIN')}
        />
      )}

      {currentView === 'HOSPITAL_LOGIN' && (
        <HospitalLoginPage
          onBackToCitizen={() => setCurrentView('CITIZEN')}
          onStartRegistration={() => setCurrentView('HOSPITAL_REGISTRATION')}
        />
      )}

      {currentView === 'HOSPITAL_REGISTRATION' && (
        <HospitalRegistrationPage
          onBackToCitizen={() => setCurrentView('CITIZEN')}
          onOpenLoginModal={() => setCurrentView('HOSPITAL_LOGIN')}
        />
      )}

      {currentView === 'ADMIN_LOGIN' && (
        <AdminLoginPage
          onAdminLoginSuccess={handleAdminLoginSuccess}
          onBackToCitizen={() => setCurrentView('CITIZEN')}
        />
      )}

      {currentView === 'ADMIN_DASHBOARD' && (
        <AdminDashboardPage
          adminUser={adminUser}
          onLogout={handleAdminLogout}
          onBackToCitizen={() => setCurrentView('CITIZEN')}
        />
      )}
    </div>
  );
}
