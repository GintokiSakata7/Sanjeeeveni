import React, { useState, useEffect } from 'react';
import {
  Building2,
  Users,
  Stethoscope,
  Ambulance,
  Car,
  KeyRound,
  Plus,
  Search,
  Trash2,
  Edit,
  CheckCircle2,
  Clock,
  AlertCircle,
  LogOut,
  Sparkles,
  Copy,
  Check,
  X,
  Phone,
  Mail,
  ShieldCheck,
  Eye,
  EyeOff,
  Lock,
  Activity
} from 'lucide-react';
import {
  PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts';
import { getApiUrl } from '../../../config';

import IncomingSOSAlert from '../components/IncomingSOSAlert';
import { fetchWithFallback } from '../../../services/apiClient';

export default function HospitalPortalDashboard({ hospitalSession, onLogout, onBackToCitizen }) {
  const hospitalId = hospitalSession?.hospital_id || 'HOSP-DEFAULT';
  const hospitalName = hospitalSession?.hospital_name || 'Hospital Command Center';

  const [activeTab, setActiveTab] = useState('OVERVIEW'); // OVERVIEW | DOCTORS | AMBULANCES | DRIVERS | CREDENTIALS
  const [stats, setStats] = useState({
    total_doctors: 0,
    available_doctors: 0,
    in_surgery_doctors: 0,
    on_leave_doctors: 0,
    total_drivers: 0,
    available_drivers: 0,
    total_ambulances: 0,
    available_ambulances: 0,
    dispatched_ambulances: 0
  });

  const [doctors, setDoctors] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [ambulances, setAmbulances] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Password visibility states
  const [showDoctorPwd, setShowDoctorPwd] = useState(false);
  const [showDriverPwd, setShowDriverPwd] = useState(false);

  // SOS Routing State
  const [incomingSOS, setIncomingSOS] = useState(null);
  const [activeSOSList, setActiveSOSList] = useState([]);
  const [sosSubmitting, setSosSubmitting] = useState(false);
  // Track IDs we've already accepted/rejected so the poll can't flash them back
  const handledSOSIds = React.useRef(new Set());

  // Poll for incoming SOS Requests every 3 seconds
  useEffect(() => {
    if (!hospitalId || hospitalId === 'HOSP-DEFAULT') return;

    const pollSOS = async () => {
      try {
        const resPending = await fetchWithFallback(`/api/v1/routing/pending/${hospitalId}`);
        if (resPending.ok) {
          const requests = await resPending.json();
          // Filter out any SOS we've already handled in this session
          const unhandled = (requests || []).filter(r => !handledSOSIds.current.has(r.id));
          if (unhandled.length > 0) {
            setIncomingSOS(prev => {
              // Don't reset if it's the same one (prevents flicker)
              if (prev && prev.id === unhandled[0].id) return prev;
              return unhandled[0];
            });
          } else {
            setIncomingSOS(null);
          }
        }
        
        const resActive = await fetchWithFallback(`/api/v1/routing/active/${hospitalId}`);
        if (resActive.ok) {
           const activeCases = await resActive.json();
           setActiveSOSList(activeCases || []);
        }
      } catch (err) {
        // Silently fail polling
      }
    };

    const intervalId = setInterval(pollSOS, 3000);
    pollSOS(); // initial check

    return () => clearInterval(intervalId);
  }, [hospitalId]);

  const handleRespondToSOS = async (sosId, status, driverId = null, doctorId = null) => {
    if (sosSubmitting) return;
    setSosSubmitting(true);
    // Immediately lock this SOS ID so the poll won't re-show it
    handledSOSIds.current.add(sosId);
    setIncomingSOS(null);
    try {
      const payload = { status };
      const res = await fetchWithFallback(`/api/v1/routing/respond/${sosId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        
        // Handle clash resolution logic returned from backend
        if (data.status === 'REJECTED' && status === 'ACCEPTED') {
          triggerToast(data.message || 'SOS request was taken by a closer hospital.', 'error');
          loadData();
          setSosSubmitting(false);
          return;
        }

        if (status === 'ACCEPTED' && driverId) {
           await fetchWithFallback(`/api/v1/routing/assign-driver/${sosId}`, {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({ driver_id: driverId })
           });
        }
        if (status === 'ACCEPTED' && doctorId) {
           await fetchWithFallback(`/api/v1/routing/assign-doctor/${sosId}`, {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({ doctor_id: doctorId })
           });
        }
        triggerToast(`SOS Emergency ${status}`, status === 'ACCEPTED' ? 'success' : 'error');
        // Refresh doctor/driver counts so statuses update immediately
        loadData();
      } else {
        // On failure, remove from handled set so it can be retried
        handledSOSIds.current.delete(sosId);
        triggerToast('Failed to respond to SOS', 'error');
      }
    } catch (err) {
      handledSOSIds.current.delete(sosId);
      triggerToast('Network error responding to SOS', 'error');
    } finally {
      setSosSubmitting(false);
    }
  };

  // Toast Notification State
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const triggerToast = (msg, type = 'success') => {
    setToast({ show: true, message: msg, type });
    setTimeout(() => setToast((prev) => ({ ...prev, show: false })), 3500);
  };

  // Copy helper
  const [copiedField, setCopiedField] = useState(null);
  const handleCopy = (text, fieldName) => {
    navigator.clipboard.writeText(text);
    setCopiedField(fieldName);
    setTimeout(() => setCopiedField(null), 2000);
  };

  // Modal States
  const [showDoctorModal, setShowDoctorModal] = useState(false);
  const [showDriverModal, setShowDriverModal] = useState(false);
  const [showAmbulanceModal, setShowAmbulanceModal] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);

  // Form States
  const [doctorForm, setDoctorForm] = useState({
    name: '',
    specialization: 'General Medicine',
    contact_number: '',
    email: '',
    password: 'DocPassword123!',
    status: 'Available',
    shift_start: '08:00',
    shift_end: '16:00',
    shift_timing: '08:00 AM - 04:00 PM'
  });

  const [driverForm, setDriverForm] = useState({
    name: '',
    contact_number: '',
    license_number: '',
    email: '',
    password: 'DriverPassword123!',
    status: 'Available',
    shift_start: '08:00',
    shift_end: '16:00',
    shift_timing: '08:00 AM - 04:00 PM'
  });


  const [ambulanceForm, setAmbulanceForm] = useState({
    vehicle_registration: '',
    vehicle_type: 'Basic',
    assigned_driver_id: '',
    assigned_driver_name: '',
    status: 'Available'
  });

  // Fetch Telemetry & Entity Data
  const loadData = async (silent = false) => {
    if (!silent) setIsLoading(true);
    try {
      const [statsRes, docRes, drvRes, ambRes] = await Promise.all([
        fetchWithFallback(`/api/v1/hms/overview-stats/${hospitalId}`),
        fetchWithFallback(`/api/v1/hms/doctors/${hospitalId}`),
        fetchWithFallback(`/api/v1/hms/drivers/${hospitalId}`),
        fetchWithFallback(`/api/v1/hms/ambulances/${hospitalId}`)
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (docRes.ok) setDoctors(await docRes.json());
      if (drvRes.ok) setDrivers(await drvRes.json());
      if (ambRes.ok) setAmbulances(await ambRes.json());
    } catch (err) {
      console.warn('HMS Data sync note:', err);
    } finally {
      if (!silent) setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const intervalId = setInterval(() => {
      loadData(true);
    }, 5000);
    return () => clearInterval(intervalId);
  }, [hospitalId]);

  // Create Handlers
  const handleAddDoctor = async (e) => {
    e.preventDefault();
    try {
      // Strip internal-only time picker fields before sending to backend
      const { shift_start, shift_end, ...doctorPayload } = doctorForm;
      const res = await fetchWithFallback('/api/v1/hms/doctors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...doctorPayload, hospital_id: hospitalId })
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        let errMsg = 'Failed to create doctor';
        if (Array.isArray(errBody?.detail)) {
          errMsg = errBody.detail.map(e => e.msg || JSON.stringify(e)).join('; ');
        } else if (typeof errBody?.detail === 'string') {
          errMsg = errBody.detail;
        }
        throw new Error(errMsg);
      }
      triggerToast(`Dr. ${doctorForm.name} added to roster!`);
      setShowDoctorModal(false);
      setDoctorForm({ name: '', specialization: 'General Medicine', contact_number: '', email: '', password: 'DocPassword123!', status: 'Available', shift_start: '08:00', shift_end: '16:00', shift_timing: '08:00 AM - 04:00 PM' });
      loadData();
    } catch (err) {
      triggerToast(err.message, 'error');
    }
  };

  const handleAddDriver = async (e) => {
    e.preventDefault();
    try {
      // Strip internal-only time picker fields, and null out optional empty strings
      const { shift_start, shift_end, ...driverPayload } = driverForm;
      if (!driverPayload.email) driverPayload.email = null;
      const res = await fetchWithFallback('/api/v1/hms/drivers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...driverPayload, hospital_id: hospitalId })
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        let errMsg = 'Failed to create driver';
        if (Array.isArray(errBody?.detail)) {
          errMsg = errBody.detail.map(e => e.msg || JSON.stringify(e)).join('; ');
        } else if (typeof errBody?.detail === 'string') {
          errMsg = errBody.detail;
        }
        throw new Error(errMsg);
      }
      triggerToast(`Driver ${driverForm.name} registered!`);
      setShowDriverModal(false);
      setDriverForm({ name: '', contact_number: '', license_number: '', email: '', password: 'DriverPassword123!', status: 'Available', shift_start: '08:00', shift_end: '16:00', shift_timing: '08:00 AM - 04:00 PM' });
      loadData();
    } catch (err) {
      triggerToast(err.message, 'error');
    }
  };

  const handleAddAmbulance = async (e) => {
    e.preventDefault();
    try {
      const res = await fetchWithFallback('/api/v1/hms/ambulances', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...ambulanceForm, hospital_id: hospitalId })
      });
      if (!res.ok) throw new Error('Failed to register ambulance');
      triggerToast(`Ambulance ${ambulanceForm.vehicle_registration} added to fleet!`);
      setShowAmbulanceModal(false);
      setAmbulanceForm({ vehicle_registration: '', vehicle_type: 'Basic', assigned_driver_id: '', assigned_driver_name: '', status: 'Available' });
      loadData();
    } catch (err) {
      triggerToast(err.message, 'error');
    }
  };

  // Delete Handlers
  const handleDeleteDoctor = async (id, name) => {
    if (!window.confirm(`Delete Dr. ${name} from roster?`)) return;
    try {
      await fetchWithFallback(`/api/v1/hms/doctors/${id}`, { method: 'DELETE' });
      triggerToast(`Dr. ${name} removed`);
      loadData();
    } catch (err) {
      triggerToast(err.message, 'error');
    }
  };

  const handleDeleteDriver = async (id, name) => {
    if (!window.confirm(`Delete driver ${name}?`)) return;
    try {
      await fetchWithFallback(`/api/v1/hms/drivers/${id}`, { method: 'DELETE' });
      triggerToast(`Driver ${name} removed`);
      loadData();
    } catch (err) {
      triggerToast(err.message, 'error');
    }
  };

  const handleDeleteAmbulance = async (id, reg) => {
    if (!window.confirm(`Remove vehicle ${reg}?`)) return;
    try {
      await fetchWithFallback(`/api/v1/hms/ambulances/${id}`, { method: 'DELETE' });
      triggerToast(`Ambulance ${reg} removed`);
      loadData();
    } catch (err) {
      triggerToast(err.message, 'error');
    }
  };

  // Inline Status Update Handlers
  const handleUpdateDoctorStatus = async (doctorId, newStatus, doctorName) => {
    try {
      const res = await fetchWithFallback(`/api/v1/hms/doctors/${doctorId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      if (!res.ok) throw new Error('Failed to update status');
      triggerToast(`Dr. ${doctorName} → ${newStatus}`);
      loadData();
    } catch (err) {
      triggerToast(err.message, 'error');
    }
  };

  const handleUpdateDriverStatus = async (driverId, newStatus, driverName) => {
    try {
      const res = await fetchWithFallback(`/api/v1/hms/drivers/${driverId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      if (!res.ok) throw new Error('Failed to update status');
      triggerToast(`${driverName} → ${newStatus}`);
      loadData();
    } catch (err) {
      triggerToast(err.message, 'error');
    }
  };

  return (
    <div className="hms-portal-root font-sans">
      {/* Toast Notification */}
      {toast.show && (
        <div className={`hms-toast ${toast.type}`}>
          <CheckCircle2 size={18} />
          <span>{toast.message}</span>
        </div>
      )}

      {/* Persistent Left Sidebar Navigation */}
      <aside className="hms-sidebar font-sans">
        <div className="hms-sidebar-brand">
          <div className="brand-icon-box">
            <Building2 size={24} className="text-cyan-400" />
          </div>
          <div className="brand-text">
            <h3>{hospitalName}</h3>
            <span className="hms-badge">Hospital Management</span>
          </div>
        </div>

        <nav className="hms-nav-menu">
          <button
            type="button"
            className={`hms-nav-item ${activeTab === 'OVERVIEW' ? 'active' : ''}`}
            onClick={() => setActiveTab('OVERVIEW')}
          >
            <Sparkles size={18} />
            <span>Overview Dashboard</span>
          </button>

          <button
            type="button"
            className={`hms-nav-item ${activeTab === 'DOCTORS' ? 'active' : ''}`}
            onClick={() => setActiveTab('DOCTORS')}
          >
            <Stethoscope size={18} />
            <span>Doctor Roster ({doctors.length})</span>
          </button>

          <button
            type="button"
            className={`hms-nav-item ${activeTab === 'AMBULANCES' ? 'active' : ''}`}
            onClick={() => setActiveTab('AMBULANCES')}
          >
            <Ambulance size={18} />
            <span>Ambulance Fleet ({ambulances.length})</span>
          </button>

          <button
            type="button"
            className={`hms-nav-item ${activeTab === 'DRIVERS' ? 'active' : ''}`}
            onClick={() => setActiveTab('DRIVERS')}
          >
            <Car size={18} />
            <span>Driver Directory ({drivers.length})</span>
          </button>

          <button
            type="button"
            className={`hms-nav-item ${activeTab === 'CREDENTIALS' ? 'active' : ''}`}
            onClick={() => setActiveTab('CREDENTIALS')}
          >
            <KeyRound size={18} />
            <span>Credentials Manager</span>
          </button>
        </nav>

        <div className="hms-sidebar-footer font-sans">
          <button type="button" className="btn-hms-logout" onClick={onLogout}>
            <LogOut size={16} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="hms-main-content font-sans">
        {/* Top Header Bar */}
        <header className="hms-top-header">
          <div className="header-search">
            <Search size={16} className="search-icon" />
            <input
              type="text"
              placeholder="Search doctors, drivers, ambulances..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="header-actions">
            {activeTab === 'DOCTORS' && (
              <button type="button" className="btn-add-primary" onClick={() => setShowDoctorModal(true)}>
                <Plus size={16} /> Add Doctor
              </button>
            )}
            {activeTab === 'AMBULANCES' && (
              <button type="button" className="btn-add-primary" onClick={() => setShowAmbulanceModal(true)}>
                <Plus size={16} /> Add Ambulance
              </button>
            )}
            {activeTab === 'DRIVERS' && (
              <button type="button" className="btn-add-primary" onClick={() => setShowDriverModal(true)}>
                <Plus size={16} /> Add Driver
              </button>
            )}

            <div className="admin-profile-chip">
              <ShieldCheck size={16} className="text-emerald-400" />
              <span>{hospitalSession?.admin_name || 'Hospital Admin'}</span>
            </div>
          </div>
        </header>

        {/* Dynamic View Panels */}
        <div className="hms-view-body">
          {/* TAB 1: OVERVIEW DASHBOARD */}
          {activeTab === 'OVERVIEW' && (
            <div className="hms-overview-grid">
              <div className="hms-metrics-row">
                <div className="hms-metric-card">
                  <div className="card-head">
                    <span>Doctors Active</span>
                    <Stethoscope size={20} className="text-cyan-400" />
                  </div>
                  <div className="card-value">{stats.available_doctors} <small>/ {stats.total_doctors}</small></div>
                  <span className="card-sub text-emerald-400">● {stats.available_doctors} Available On Duty</span>
                </div>

                <div className="hms-metric-card">
                  <div className="card-head">
                    <span>In Surgery</span>
                    <Clock size={20} className="text-amber-400" />
                  </div>
                  <div className="card-value text-amber-400">{stats.in_surgery_doctors}</div>
                  <span className="card-sub text-amber-300">Active Operation Theatres</span>
                </div>

                <div className="hms-metric-card">
                  <div className="card-head">
                    <span>Ambulance Fleet</span>
                    <Ambulance size={20} className="text-emerald-400" />
                  </div>
                  <div className="card-value text-emerald-400">{stats.available_ambulances} <small>/ {stats.total_ambulances}</small></div>
                  <span className="card-sub text-emerald-300">Ready for Dispatch</span>
                </div>

                <div className="hms-metric-card">
                  <div className="card-head">
                    <span>Active Drivers</span>
                    <Car size={20} className="text-purple-400" />
                  </div>
                  <div className="card-value text-purple-400">{stats.available_drivers} <small>/ {stats.total_drivers}</small></div>
                  <span className="card-sub text-purple-300">Licensed Emergency Personnel</span>
                </div>
              </div>

              {/* ACTIVE EMERGENCIES PANEL */}
              {activeSOSList.length > 0 && (
                 <div className="hms-panel-box mt-6" style={{ border: '1px solid #ef4444', backgroundColor: 'rgba(239, 68, 68, 0.05)' }}>
                    <div className="panel-header" style={{ borderBottom: '1px solid rgba(239, 68, 68, 0.2)' }}>
                      <h4 style={{ color: '#ef4444', display: 'flex', alignItems: 'center', gap: '8px' }}>
                         <Activity size={18} className="animate-pulse" /> Active Emergencies
                      </h4>
                    </div>
                    <div className="panel-list" style={{ gap: '10px', padding: '15px' }}>
                       {activeSOSList.map(sos => (
                          <div key={sos.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#0f1523', padding: '15px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                             <div>
                                <strong style={{ color: '#fff', fontSize: '16px' }}>SOS ID: {sos.id.split('-').pop()}</strong>
                                <p style={{ color: '#94a3b8', fontSize: '13px', margin: '4px 0' }}>Triage: <span style={{ color: '#ef4444' }}>{sos.triage_urgency}</span></p>
                                <p style={{ color: '#cbd5e1', fontSize: '13px', fontStyle: 'italic', margin: 0 }}>"{sos.transcript}"</p>
                                <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
                                  <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', backgroundColor: 'rgba(59, 130, 246, 0.1)', color: '#60a5fa' }}>
                                    Ambulance: {sos.assigned_ambulance_reg || 'N/A'}
                                  </span>
                                  <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', backgroundColor: 'rgba(244, 114, 182, 0.1)', color: '#f472b6' }}>
                                    Doctor: {sos.assigned_doctor_name || 'N/A'}
                                  </span>
                                </div>
                             </div>
                             <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '10px' }}>
                                <span style={{ 
                                   fontSize: '12px', padding: '4px 10px', borderRadius: '4px', fontWeight: 'bold',
                                   backgroundColor: 'rgba(59, 130, 246, 0.2)', 
                                   color: '#60a5fa' 
                                }}>
                                   {sos.status}
                                </span>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                  {(sos.status === 'DOCTOR_ACCEPTED' || sos.doctor_status === 'ACCEPTED') && (
                                     <button className="btn-sec" style={{ fontSize: '12px', padding: '6px 12px', borderColor: '#34d399', color: '#34d399' }} onClick={async () => {
                                        try {
                                           const res = await fetchWithFallback(`/api/v1/routing/initiate-call/${sos.id}`, { method: 'POST' });
                                           if (res.ok) {
                                              triggerToast('📞 Call initiated — patient will be notified', 'success');
                                           } else {
                                              triggerToast('Failed to initiate call', 'error');
                                           }
                                        } catch (err) {
                                           triggerToast('Network error initiating call', 'error');
                                        }
                                     }}>
                                        📞 Contact Doctor
                                     </button>
                                  )}
                                  {(sos.status === 'ACCEPTED' || sos.status === 'DOCTOR_ACCEPTED' || sos.status === 'PENDING') && (
                                     <button className="btn-sec" style={{ fontSize: '12px', padding: '6px 12px', borderColor: '#60a5fa', color: '#60a5fa', backgroundColor: 'rgba(59, 130, 246, 0.1)' }} onClick={async () => {
                                        try {
                                           const res = await fetchWithFallback(`/api/v1/routing/hospital-dispatch/${sos.id}`, { method: 'POST' });
                                           if (res.ok) {
                                              triggerToast('🚑 Ambulance Dispatched', 'success');
                                           } else {
                                              triggerToast('Failed to dispatch ambulance', 'error');
                                           }
                                        } catch (err) {
                                           triggerToast('Network error dispatching', 'error');
                                        }
                                     }}>
                                        🚑 Dispatch Ambulance
                                     </button>
                                  )}
                                  {sos.status === 'DISPATCHED' && (
                                     <button className="btn-sec" style={{ fontSize: '12px', padding: '6px 12px', borderColor: '#f472b6', color: '#f472b6', backgroundColor: 'rgba(244, 114, 182, 0.1)' }} onClick={async () => {
                                        try {
                                           const res = await fetchWithFallback(`/api/v1/routing/hospital-pickup/${sos.id}`, { method: 'POST' });
                                           if (res.ok) {
                                              triggerToast('✅ Patient Picked Up', 'success');
                                           } else {
                                              triggerToast('Failed to mark as picked up', 'error');
                                           }
                                        } catch (err) {
                                           triggerToast('Network error', 'error');
                                        }
                                     }}>
                                        ✅ Mark Picked Up
                                     </button>
                                  )}
                                </div>
                             </div>
                          </div>
                       ))}
                    </div>
                 </div>
              )}

              {/* Roster Previews */}
              <div className="hms-two-col-grid mt-6">
                {/* On Duty Doctors */}
                <div className="hms-panel-box">
                  <div className="panel-header">
                    <h4>👨‍⚕️ Available Doctor Roster & Shift Timings</h4>
                    <button type="button" className="btn-link" onClick={() => setActiveTab('DOCTORS')}>View All</button>
                  </div>
                  <div className="panel-list">
                    {doctors.filter(d => d.status === 'Available').slice(0, 4).map(d => (
                      <div key={d.id} className="panel-list-item">
                        <div>
                          <strong>{d.name}</strong>
                          <span className="sub">{d.specialization} • {d.shift_timing || 'Morning Shift'}</span>
                        </div>
                        <span className="badge-pill available">Available (On Duty)</span>
                      </div>
                    ))}
                    {doctors.filter(d => d.status === 'Available').length === 0 && (
                      <p className="text-slate-500 text-xs py-4 text-center">No doctors currently listed as Available.</p>
                    )}
                  </div>
                </div>

                {/* Ambulances */}
                <div className="hms-panel-box">
                  <div className="panel-header">
                    <h4>🚑 Emergency Vehicle Fleet</h4>
                    <button type="button" className="btn-link" onClick={() => setActiveTab('AMBULANCES')}>View All</button>
                  </div>
                  <div className="panel-list">
                    {ambulances.slice(0, 4).map(a => (
                      <div key={a.id} className="panel-list-item">
                        <div>
                          <strong className="font-mono">{a.vehicle_registration}</strong>
                          <span className="sub">{a.vehicle_type} Life Support</span>
                        </div>
                        <span className={`badge-pill ${a.status.toLowerCase()}`}>{a.status}</span>
                      </div>
                    ))}
                    {ambulances.length === 0 && (
                      <p className="text-slate-500 text-xs py-4 text-center">No ambulance vehicles registered yet.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: DOCTOR MANAGEMENT TABLE */}
          {activeTab === 'DOCTORS' && (
            <div className="hms-table-container">
              <div className="table-header-bar">
                <h3>Doctor Management Roster</h3>
                <button type="button" className="btn-add-primary" onClick={() => setShowDoctorModal(true)}>
                  <Plus size={16} /> Register New Doctor
                </button>
              </div>

              <table className="hms-table">
                <thead>
                  <tr>
                    <th>Doctor Name</th>
                    <th>Specialization</th>
                    <th>Contact Phone</th>
                    <th>Duty Status</th>
                    <th>Shift Timing</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {doctors.filter(d => (d.name || '').toLowerCase().includes(searchQuery.toLowerCase())).map((doc) => (
                    <tr key={doc.id}>
                      <td>
                        <strong>{doc.name}</strong>
                        <span className="block text-xs text-slate-400 font-mono">{doc.email}</span>
                      </td>
                      <td>{doc.specialization}</td>
                      <td className="font-mono">{doc.contact_number}</td>
                      <td>
                        <span className={`badge-pill ${doc.status.toLowerCase().replace(' ', '-')}`}>
                          {doc.status}
                        </span>
                      </td>
                      <td>
                        <select
                          className={`status-inline-select ${doc.status.toLowerCase().replace(/\s/g, '-')}`}
                          value={doc.status}
                          onChange={(e) => handleUpdateDoctorStatus(doc.id, e.target.value, doc.name)}
                        >
                          <option value="Available">✅ Available</option>
                          <option value="In Surgery">🔴 In Surgery</option>
                          <option value="On Leave">🟡 On Leave</option>
                        </select>
                      </td>
                      <td>
                        <span className="text-xs font-mono text-cyan-300 bg-cyan-950/60 border border-cyan-800/80 px-2 py-1 rounded-md">
                          ⏰ {doc.shift_timing || 'Morning Shift (08:00 AM - 04:00 PM)'}
                        </span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="btn-table-del"
                          onClick={() => handleDeleteDoctor(doc.id, doc.name)}
                          title="Remove Doctor"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                  {doctors.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-slate-500">
                        No doctors registered. Click "+ Register New Doctor" to add.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 3: AMBULANCE FLEET TABLE */}
          {activeTab === 'AMBULANCES' && (
            <div className="hms-table-container">
              <div className="table-header-bar">
                <h3>Emergency Ambulance Fleet</h3>
                <button type="button" className="btn-add-primary" onClick={() => setShowAmbulanceModal(true)}>
                  <Plus size={16} /> Add Ambulance Vehicle
                </button>
              </div>

              <table className="hms-table">
                <thead>
                  <tr>
                    <th>Registration #</th>
                    <th>Vehicle Type</th>
                    <th>Assigned Driver</th>
                    <th>Dispatch Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {ambulances.filter(a => (a.vehicle_registration || '').toLowerCase().includes(searchQuery.toLowerCase())).map((amb) => (
                    <tr key={amb.id}>
                      <td><strong className="font-mono">{amb.vehicle_registration}</strong></td>
                      <td>{amb.vehicle_type} Life Support</td>
                      <td>{amb.assigned_driver_name || 'Unassigned'}</td>
                      <td>
                        <span className={`badge-pill ${amb.status.toLowerCase()}`}>
                          {amb.status}
                        </span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="btn-table-del"
                          onClick={() => handleDeleteAmbulance(amb.id, amb.vehicle_registration)}
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                  {ambulances.length === 0 && (
                    <tr>
                      <td colSpan={5} className="text-center py-8 text-slate-500">
                        No ambulance vehicles registered in fleet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 4: DRIVER DIRECTORY TABLE */}
          {activeTab === 'DRIVERS' && (
            <div className="hms-table-container">
              <div className="table-header-bar">
                <h3>Emergency Ambulance Drivers</h3>
                <button type="button" className="btn-add-primary" onClick={() => setShowDriverModal(true)}>
                  <Plus size={16} /> Add Driver
                </button>
              </div>

              <table className="hms-table">
                <thead>
                  <tr>
                    <th>Driver Name</th>
                    <th>License Number</th>
                    <th>Contact Mobile</th>
                    <th>Duty Status</th>
                    <th>Shift Timing</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {drivers.filter(d => (d.name || '').toLowerCase().includes(searchQuery.toLowerCase())).map((drv) => (
                    <tr key={drv.id}>
                      <td><strong>{drv.name}</strong></td>
                      <td className="font-mono">{drv.license_number}</td>
                      <td className="font-mono">{drv.contact_number}</td>
                      <td>
                        <span className={`badge-pill ${drv.status.toLowerCase().replace(' ', '-')}`}>
                          {drv.status}
                        </span>
                      </td>
                      <td>
                        <span className="text-xs font-mono text-cyan-300 bg-cyan-950/60 border border-cyan-800/80 px-2 py-1 rounded-md">
                          ⏰ {drv.shift_timing || 'Morning Shift (08:00 AM - 04:00 PM)'}
                        </span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="btn-table-del"
                          onClick={() => handleDeleteDriver(drv.id, drv.name)}
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                  {drivers.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-slate-500">
                        No drivers registered yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 5: STAFF CREDENTIALS GENERATOR */}
          {activeTab === 'CREDENTIALS' && (
            <div className="hms-credentials-box">
              <h3>🔑 Staff Login Credentials Sharing</h3>
              <p className="sub-desc">Admins generate & share credentials with Doctors and Drivers for mobile & portal access.</p>

              <div className="credentials-grid mt-6">
                {doctors.map(d => (
                  <div key={d.id} className="cred-card">
                    <div className="cred-head">
                      <strong>Dr. {d.name}</strong>
                      <span className="badge-pill available">DOCTOR</span>
                    </div>
                    <p className="font-mono text-xs text-slate-300 mt-2">Email: {d.email}</p>
                    <p className="font-mono text-xs text-amber-300 mt-1">Default Key: DocPassword123!</p>
                    <p className="font-mono text-xs text-cyan-400 mt-1">Shift: {d.shift_timing || 'Morning Shift'}</p>
                  </div>
                ))}
                {drivers.map(drv => (
                  <div key={drv.id} className="cred-card">
                    <div className="cred-head">
                      <strong>{drv.name}</strong>
                      <span className="badge-pill purple">DRIVER</span>
                    </div>
                    <p className="font-mono text-xs text-slate-300 mt-2">License: {drv.license_number}</p>
                    <p className="font-mono text-xs text-amber-300 mt-1">Mobile: {drv.contact_number}</p>
                    <p className="font-mono text-xs text-cyan-400 mt-1">Shift: {drv.shift_timing || 'Morning Shift'}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* CREATE DOCTOR MODAL */}
      {showDoctorModal && (
        <div className="hms-modal-overlay">
          <div className="hms-modal-card">
            <div className="modal-head">
              <h3>👨‍⚕️ Add Doctor to Roster</h3>
              <button type="button" onClick={() => setShowDoctorModal(false)}><X size={18} /></button>
            </div>
            <form onSubmit={handleAddDoctor} className="modal-form">
              <div className="form-field">
                <label>Doctor Full Name *</label>
                <input
                  type="text"
                  placeholder="Dr. Rajesh Verma"
                  value={doctorForm.name}
                  onChange={(e) => setDoctorForm({ ...doctorForm, name: e.target.value })}
                  required
                />
              </div>

              <div className="form-field">
                <label>Medical Specialization *</label>
                <input
                  type="text"
                  placeholder="Cardiology / General Surgery / Emergency Medicine"
                  value={doctorForm.specialization}
                  onChange={(e) => setDoctorForm({ ...doctorForm, specialization: e.target.value })}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="form-field">
                  <label>Contact Mobile *</label>
                  <input
                    type="text"
                    placeholder="+919876543210"
                    value={doctorForm.contact_number}
                    onChange={(e) => setDoctorForm({ ...doctorForm, contact_number: e.target.value })}
                    required
                  />
                </div>
                <div className="form-field">
                  <label>Email Address *</label>
                  <input
                    type="email"
                    placeholder="doctor@hospital.com"
                    value={doctorForm.email}
                    onChange={(e) => setDoctorForm({ ...doctorForm, email: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="form-field">
                <label><Lock size={14} style={{display:'inline',verticalAlign:'middle',marginRight:4}} />Login Password *</label>
                <div style={{position:'relative'}}>
                  <input
                    type={showDoctorPwd ? 'text' : 'password'}
                    placeholder="Set a strong password"
                    value={doctorForm.password}
                    onChange={(e) => setDoctorForm({ ...doctorForm, password: e.target.value })}
                    required
                    minLength={6}
                  />
                  <button
                    type="button"
                    onClick={() => setShowDoctorPwd(!showDoctorPwd)}
                    style={{position:'absolute',right:12,top:'50%',transform:'translateY(-50%)',background:'none',border:'none',cursor:'pointer',color:'#94a3b8',padding:0}}
                    tabIndex={-1}
                  >
                    {showDoctorPwd ? <EyeOff size={16}/> : <Eye size={16}/>}
                  </button>
                </div>
                <span className="text-[10px] text-slate-500 mt-1 block">This password will be used by the doctor to log in to their staff portal / mobile app.</span>
              </div>

              <div className="form-field">
                <label>Duty Status *</label>
                <select
                  value={doctorForm.status}
                  onChange={(e) => setDoctorForm({ ...doctorForm, status: e.target.value })}
                >
                  <option value="Available">Available (On Duty)</option>
                  <option value="In Surgery">In Surgery</option>
                  <option value="On Leave">On Leave</option>
                </select>
              </div>

              {/* Standard Time Selection Module */}
              <div className="form-field">
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-bold text-slate-300">Shift Time Window (Standard Time Picker) *</label>
                  <span className="text-cyan-400 font-mono text-[11px]">
                    ⏰ {doctorForm.shift_timing || `${formatTime12h(doctorForm.shift_start)} - ${formatTime12h(doctorForm.shift_end)}`}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <span className="text-[10px] text-slate-400 block mb-1">Shift Start Time</span>
                    <input
                      type="time"
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 font-mono focus:border-cyan-400 focus:outline-none"
                      value={doctorForm.shift_start || '08:00'}
                      onChange={(e) => {
                        const newStart = e.target.value;
                        const formatted = `${formatTime12h(newStart)} - ${formatTime12h(doctorForm.shift_end || '16:00')}`;
                        setDoctorForm({ ...doctorForm, shift_start: newStart, shift_timing: formatted });
                      }}
                      required
                    />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block mb-1">Shift End Time</span>
                    <input
                      type="time"
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 font-mono focus:border-cyan-400 focus:outline-none"
                      value={doctorForm.shift_end || '16:00'}
                      onChange={(e) => {
                        const newEnd = e.target.value;
                        const formatted = `${formatTime12h(doctorForm.shift_start || '08:00')} - ${formatTime12h(newEnd)}`;
                        setDoctorForm({ ...doctorForm, shift_end: newEnd, shift_timing: formatted });
                      }}
                      required
                    />
                  </div>
                </div>

                <div className="flex flex-wrap gap-1 mt-2 font-sans">
                  <button type="button" className="text-[10px] bg-slate-800 hover:bg-slate-700 text-cyan-400 px-2 py-0.5 rounded border border-slate-700" onClick={() => setDoctorForm({ ...doctorForm, shift_start: '08:00', shift_end: '16:00', shift_timing: '08:00 AM - 04:00 PM' })}>Morning (08:00-16:00)</button>
                  <button type="button" className="text-[10px] bg-slate-800 hover:bg-slate-700 text-cyan-400 px-2 py-0.5 rounded border border-slate-700" onClick={() => setDoctorForm({ ...doctorForm, shift_start: '16:00', shift_end: '00:00', shift_timing: '04:00 PM - 12:00 AM' })}>Evening (16:00-00:00)</button>
                  <button type="button" className="text-[10px] bg-slate-800 hover:bg-slate-700 text-cyan-400 px-2 py-0.5 rounded border border-slate-700" onClick={() => setDoctorForm({ ...doctorForm, shift_start: '00:00', shift_end: '08:00', shift_timing: '12:00 AM - 08:00 AM' })}>Night (00:00-08:00)</button>
                  <button type="button" className="text-[10px] bg-slate-800 hover:bg-slate-700 text-emerald-400 px-2 py-0.5 rounded border border-slate-700" onClick={() => setDoctorForm({ ...doctorForm, shift_timing: '24x7 Emergency Duty' })}>24x7 Emergency</button>
                </div>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-sec" onClick={() => setShowDoctorModal(false)}>Cancel</button>
                <button type="submit" className="btn-add-primary">Create Doctor Record</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CREATE DRIVER MODAL */}
      {showDriverModal && (
        <div className="hms-modal-overlay">
          <div className="hms-modal-card">
            <div className="modal-head">
              <h3>🚘 Add Ambulance Driver</h3>
              <button type="button" onClick={() => setShowDriverModal(false)}><X size={18} /></button>
            </div>
            <form onSubmit={handleAddDriver} className="modal-form">
              <div className="form-field">
                <label>Driver Full Name *</label>
                <input
                  type="text"
                  placeholder="Ramesh Kumar"
                  value={driverForm.name}
                  onChange={(e) => setDriverForm({ ...driverForm, name: e.target.value })}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="form-field">
                  <label>Contact Mobile *</label>
                  <input
                    type="text"
                    placeholder="+919876543210"
                    value={driverForm.contact_number}
                    onChange={(e) => setDriverForm({ ...driverForm, contact_number: e.target.value })}
                    required
                  />
                </div>
                <div className="form-field">
                  <label>Driving License # *</label>
                  <input
                    type="text"
                    placeholder="DL-1420110012345"
                    value={driverForm.license_number}
                    onChange={(e) => setDriverForm({ ...driverForm, license_number: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="form-field">
                <label><Lock size={14} style={{display:'inline',verticalAlign:'middle',marginRight:4}} />Login Password *</label>
                <div style={{position:'relative'}}>
                  <input
                    type={showDriverPwd ? 'text' : 'password'}
                    placeholder="Set a strong password"
                    value={driverForm.password}
                    onChange={(e) => setDriverForm({ ...driverForm, password: e.target.value })}
                    required
                    minLength={6}
                  />
                  <button
                    type="button"
                    onClick={() => setShowDriverPwd(!showDriverPwd)}
                    style={{position:'absolute',right:12,top:'50%',transform:'translateY(-50%)',background:'none',border:'none',cursor:'pointer',color:'#94a3b8',padding:0}}
                    tabIndex={-1}
                  >
                    {showDriverPwd ? <EyeOff size={16}/> : <Eye size={16}/>}
                  </button>
                </div>
                <span className="text-[10px] text-slate-500 mt-1 block">This password will be used by the driver to log in to their mobile app.</span>
              </div>

              <div className="form-field">
                <label>Duty Status *</label>
                <select
                  value={driverForm.status}
                  onChange={(e) => setDriverForm({ ...driverForm, status: e.target.value })}
                >
                  <option value="Available">Available (On Duty)</option>
                  <option value="Dispatched">Dispatched</option>
                  <option value="Off Duty">Off Duty</option>
                </select>
              </div>

              {/* Standard Time Selection Module for Driver */}
              <div className="form-field">
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-bold text-slate-300">Shift Time Window (Standard Time Picker) *</label>
                  <span className="text-cyan-400 font-mono text-[11px]">
                    ⏰ {driverForm.shift_timing || `${formatTime12h(driverForm.shift_start)} - ${formatTime12h(driverForm.shift_end)}`}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <span className="text-[10px] text-slate-400 block mb-1">Shift Start Time</span>
                    <input
                      type="time"
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 font-mono focus:border-cyan-400 focus:outline-none"
                      value={driverForm.shift_start || '08:00'}
                      onChange={(e) => {
                        const newStart = e.target.value;
                        const formatted = `${formatTime12h(newStart)} - ${formatTime12h(driverForm.shift_end || '16:00')}`;
                        setDriverForm({ ...driverForm, shift_start: newStart, shift_timing: formatted });
                      }}
                      required
                    />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block mb-1">Shift End Time</span>
                    <input
                      type="time"
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 font-mono focus:border-cyan-400 focus:outline-none"
                      value={driverForm.shift_end || '16:00'}
                      onChange={(e) => {
                        const newEnd = e.target.value;
                        const formatted = `${formatTime12h(driverForm.shift_start || '08:00')} - ${formatTime12h(newEnd)}`;
                        setDriverForm({ ...driverForm, shift_end: newEnd, shift_timing: formatted });
                      }}
                      required
                    />
                  </div>
                </div>

                <div className="flex flex-wrap gap-1 mt-2 font-sans">
                  <button type="button" className="text-[10px] bg-slate-800 hover:bg-slate-700 text-cyan-400 px-2 py-0.5 rounded border border-slate-700" onClick={() => setDriverForm({ ...driverForm, shift_start: '08:00', shift_end: '16:00', shift_timing: '08:00 AM - 04:00 PM' })}>Morning (08:00-16:00)</button>
                  <button type="button" className="text-[10px] bg-slate-800 hover:bg-slate-700 text-cyan-400 px-2 py-0.5 rounded border border-slate-700" onClick={() => setDriverForm({ ...driverForm, shift_start: '16:00', shift_end: '00:00', shift_timing: '04:00 PM - 12:00 AM' })}>Evening (16:00-00:00)</button>
                  <button type="button" className="text-[10px] bg-slate-800 hover:bg-slate-700 text-cyan-400 px-2 py-0.5 rounded border border-slate-700" onClick={() => setDriverForm({ ...driverForm, shift_start: '00:00', shift_end: '08:00', shift_timing: '12:00 AM - 08:00 AM' })}>Night (00:00-08:00)</button>
                  <button type="button" className="text-[10px] bg-slate-800 hover:bg-slate-700 text-emerald-400 px-2 py-0.5 rounded border border-slate-700" onClick={() => setDriverForm({ ...driverForm, shift_timing: '24x7 Emergency Duty' })}>24x7 Emergency</button>
                </div>
              </div>



              <div className="modal-actions">
                <button type="button" className="btn-sec" onClick={() => setShowDriverModal(false)}>Cancel</button>
                <button type="submit" className="btn-add-primary">Create Driver Record</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CREATE AMBULANCE MODAL */}
      {showAmbulanceModal && (
        <div className="hms-modal-overlay">
          <div className="hms-modal-card">
            <div className="modal-head">
              <h3>🚑 Register Ambulance Vehicle</h3>
              <button type="button" onClick={() => setShowAmbulanceModal(false)}><X size={18} /></button>
            </div>
            <form onSubmit={handleAddAmbulance} className="modal-form">
              <div className="form-field">
                <label>Vehicle Registration Number *</label>
                <input
                  type="text"
                  placeholder="TS 09 EA 4004"
                  value={ambulanceForm.vehicle_registration}
                  onChange={(e) => setAmbulanceForm({ ...ambulanceForm, vehicle_registration: e.target.value })}
                  required
                />
              </div>

              <div className="form-field">
                <label>Vehicle Type *</label>
                <select
                  value={ambulanceForm.vehicle_type}
                  onChange={(e) => setAmbulanceForm({ ...ambulanceForm, vehicle_type: e.target.value })}
                >
                  <option value="Basic">Basic Life Support (BLS)</option>
                  <option value="Advanced">Advanced Life Support (ALS)</option>
                </select>
              </div>

              <div className="form-field">
                <label>Assign Driver</label>
                <select
                  value={ambulanceForm.assigned_driver_id}
                  onChange={(e) => {
                    const drv = drivers.find(d => d.id === e.target.value);
                    setAmbulanceForm({
                      ...ambulanceForm,
                      assigned_driver_id: e.target.value,
                      assigned_driver_name: drv ? drv.name : ''
                    });
                  }}
                >
                  <option value="">-- Unassigned --</option>
                  {drivers.map(d => (
                    <option key={d.id} value={d.id}>{d.name} ({d.contact_number})</option>
                  ))}
                </select>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-sec" onClick={() => setShowAmbulanceModal(false)}>Cancel</button>
                <button type="submit" className="btn-add-primary">Add Ambulance to Fleet</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* SOS EMERGENCY ALERT MODAL */}
      <IncomingSOSAlert
        sosRequest={incomingSOS}
        availableDrivers={drivers.filter(d => d.status === 'Available')}
        availableDoctors={doctors.filter(d => d.status === 'Available')}
        isSubmitting={sosSubmitting}
        onAccept={(id, driverId, doctorId) => handleRespondToSOS(id, 'ACCEPTED', driverId, doctorId)}
        onReject={(id) => handleRespondToSOS(id, 'REJECTED')}
      />
    </div>
  );
}
