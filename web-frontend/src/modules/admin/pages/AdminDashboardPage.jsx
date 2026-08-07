import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Building2,
  CheckCircle2,
  XCircle,
  Clock,
  Search,
  Filter,
  Eye,
  LogOut,
  Sparkles,
  ShieldCheck,
  MapPin,
  BedDouble,
  FileText,
  UserCheck,
  AlertTriangle,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  X,
  RefreshCw,
  Send
} from 'lucide-react';
import { getApiUrl } from '../../../config';

import { fetchWithFallback } from '../../../services/apiClient';

export default function AdminDashboardPage({ adminUser, onLogout, onBackToCitizen }) {
  const [stats, setStats] = useState({
    total_hospitals: 0,
    pending_count: 0,
    approved_count: 0,
    rejected_count: 0,
    total_beds: 0,
    total_icu_beds: 0
  });

  const [hospitals, setHospitals] = useState([]);
  const [activeTab, setActiveTab] = useState('PENDING'); // PENDING | APPROVED | REJECTED | ALL
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedHospital, setSelectedHospital] = useState(null);
  const [processingId, setProcessingId] = useState(null);

  // Custom Toast Notification State
  const [toast, setToast] = useState({ show: false, type: 'success', title: '', message: '' });

  // Custom Rejection Modal State
  const [rejectionTarget, setRejectionTarget] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');

  const triggerToast = (type, title, message) => {
    setToast({ show: true, type, title, message });
    setTimeout(() => {
      setToast((prev) => ({ ...prev, show: false }));
    }, 4500);
  };

  // Fetch telemetry stats & hospital list
  const fetchData = async (silent = false) => {
    if (!silent) setIsLoading(true);
    try {
      const [statsRes, hospRes] = await Promise.all([
        fetchWithFallback('/api/v1/admin/stats'),
        fetchWithFallback('/api/v1/admin/hospitals')
      ]);

      if (statsRes.ok) {
        const sData = await statsRes.json();
        setStats(sData);
      }

      if (hospRes.ok) {
        const hData = await hospRes.json();
        setHospitals(hData.hospitals || []);
      }
    } catch (err) {
      console.warn('Failed to load admin telemetry data:', err);
    } finally {
      if (!silent) setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData(); // initial loud fetch
    const intervalId = setInterval(() => {
      fetchData(true); // silent background fetch
    }, 5000);
    return () => clearInterval(intervalId);
  }, []);

  // Handle Approve / Reject Actions
  const handleVerifyAction = async (hospitalId, status, notes = '') => {
    setProcessingId(hospitalId);
    try {
      const response = await fetchWithFallback(`/api/v1/admin/verify-hospital/${hospitalId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: status,
          notes: notes || `Application marked as ${status} by Central Admin.`
        })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update hospital status');
      }

      const isApprove = status === 'APPROVED';
      triggerToast(
        isApprove ? 'success' : 'error',
        isApprove ? 'Hospital Approved Successfully' : 'Application Rejected',
        data.message || `Hospital status set to ${status}.`
      );

      setSelectedHospital(null);
      setRejectionTarget(null);
      setRejectionReason('');
      fetchData();
    } catch (err) {
      triggerToast('error', 'Action Failed', err.message);
    } finally {
      setProcessingId(null);
    }
  };

  // Filtered Hospital List
  const filteredHospitals = hospitals.filter((h) => {
    const statusVal = h.status || '';
    if (activeTab === 'PENDING' && statusVal !== 'PENDING_VERIFICATION') return false;
    if (activeTab === 'APPROVED' && statusVal !== 'APPROVED') return false;
    if (activeTab === 'REJECTED' && statusVal !== 'REJECTED') return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const nameMatch = (h.name || '').toLowerCase().includes(q);
      const regMatch = (h.registration_number || '').toLowerCase().includes(q);
      const cityMatch = (h.address?.city || '').toLowerCase().includes(q);
      return nameMatch || regMatch || cityMatch;
    }
    return true;
  });

  return (
    <div className="admin-dash-root font-sans">
      {/* Toast Alert Banner */}
      {toast.show && (
        <div className={`toast-banner font-sans ${toast.type}`}>
          <div className="toast-icon">
            {toast.type === 'success' ? (
              <CheckCircle2 size={20} className="text-emerald-400" />
            ) : (
              <AlertTriangle size={20} className="text-red-400" />
            )}
          </div>
          <div className="toast-content">
            <h4>{toast.title}</h4>
            <p>{toast.message}</p>
          </div>
          <button
            type="button"
            className="toast-close"
            onClick={() => setToast((prev) => ({ ...prev, show: false }))}
          >
            <X size={16} />
          </button>
        </div>
      )}

      {/* Executive Top Navigation Header */}
      <header className="admin-header-bar font-sans">
        <div className="admin-brand font-sans">
          <div className="brand-badge-icon">
            <ShieldCheck size={24} className="text-amber-400" />
          </div>
          <div>
            <h2>Sanjeevani Central Authority</h2>
            <p>State Healthcare Verification & Emergency Telemetry Operations</p>
          </div>
        </div>

        <div className="admin-header-controls font-sans">
          <div className="admin-user-pill">
            <UserCheck size={14} className="text-cyan-400" />
            <span>{adminUser?.email || 'admin@sanjeevani.com'}</span>
          </div>

          <button
            type="button"
            className="btn-admin-icon"
            onClick={fetchData}
            title="Refresh Telemetry Data"
          >
            <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
            <span>Sync Data</span>
          </button>

          <button
            type="button"
            className="btn-admin-logout"
            onClick={onLogout}
          >
            <LogOut size={14} />
            <span>Sign Out</span>
          </button>
        </div>
      </header>

      {/* Main Admin Dashboard Container */}
      <div className="admin-dash-container font-sans">
        {/* Metric KPI Cards Grid */}
        <div className="admin-kpi-grid">
          <div className="admin-kpi-card">
            <div className="kpi-head">
              <span>Total Facilities</span>
              <Building2 size={20} className="text-cyan-400" />
            </div>
            <div className="kpi-value">{stats.total_hospitals}</div>
            <span className="kpi-sub">Network Providers</span>
          </div>

          <div className="admin-kpi-card warning">
            <div className="kpi-head">
              <span>Pending Review</span>
              <Clock size={20} className="text-amber-400" />
            </div>
            <div className="kpi-value text-amber-400">{stats.pending_verifications}</div>
            <span className="kpi-sub text-amber-300">Awaiting Action</span>
          </div>

          <div className="admin-kpi-card success">
            <div className="kpi-head">
              <span>Approved & Active</span>
              <CheckCircle2 size={20} className="text-emerald-400" />
            </div>
            <div className="kpi-value text-emerald-400">{stats.approved_hospitals}</div>
            <span className="kpi-sub text-emerald-300">Dispatch Ready</span>
          </div>

          <div className="admin-kpi-card">
            <div className="kpi-head">
              <span>ICU Capacity</span>
              <BedDouble size={20} className="text-purple-400" />
            </div>
            <div className="kpi-value text-purple-400 font-mono">
              {stats.total_icu_beds} <small>/ {stats.total_beds} Total</small>
            </div>
            <span className="kpi-sub">Active Emergency Beds</span>
          </div>
        </div>

        {/* Tab Navigation & Search Toolbar */}
        <div className="admin-toolbar font-sans">
          <div className="admin-tabs font-sans">
            <button
              type="button"
              className={`admin-tab-btn ${activeTab === 'PENDING' ? 'active-pending' : ''}`}
              onClick={() => setActiveTab('PENDING')}
            >
              ⏳ Pending Verification ({stats.pending_verifications})
            </button>

            <button
              type="button"
              className={`admin-tab-btn ${activeTab === 'APPROVED' ? 'active-approved' : ''}`}
              onClick={() => setActiveTab('APPROVED')}
            >
              ✅ Approved Network ({stats.approved_hospitals})
            </button>

            <button
              type="button"
              className={`admin-tab-btn ${activeTab === 'REJECTED' ? 'active-rejected' : ''}`}
              onClick={() => setActiveTab('REJECTED')}
            >
              ❌ Rejected ({stats.rejected_hospitals})
            </button>

            <button
              type="button"
              className={`admin-tab-btn ${activeTab === 'ALL' ? 'active-all' : ''}`}
              onClick={() => setActiveTab('ALL')}
            >
              🌐 All Facilities ({stats.total_hospitals})
            </button>
          </div>

          <div className="admin-search-box">
            <Search size={16} className="search-icon" />
            <input
              type="text"
              placeholder="Search hospital name, reg #, city..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Hospital Verification List View */}
        {isLoading ? (
          <div className="admin-empty-state">
            <div className="spinner"></div>
            <p>Loading Sanjeevani Telemetry Records...</p>
          </div>
        ) : filteredHospitals.length === 0 ? (
          <div className="admin-empty-state">
            <Building2 size={44} className="empty-icon text-slate-500" />
            <h4>No Hospital Records Match Your Filter</h4>
            <p>Try selecting a different tab or clear search query.</p>
          </div>
        ) : (
          <div className="admin-hosp-list">
            {filteredHospitals.map((h) => (
              <div key={h.id} className="admin-hosp-card">
                {/* Hospital Core Info */}
                <div className="hosp-info-col">
                  <div className="hosp-title-row">
                    <h3>{h.name}</h3>
                    <span className={`status-badge ${h.status}`}>
                      {h.status}
                    </span>
                    <span className="mode-badge">
                      {h.hospital_type === 'SMALL' ? 'Sanjeevani Integrated Portal' : 'External HIS API Mode'}
                    </span>
                  </div>

                  <div className="hosp-meta-row font-mono">
                    <span>Reg #: <strong>{h.registration_number}</strong></span>
                    <span>License #: <strong>{h.license_number}</strong></span>
                    <span>Category: <strong>{h.category}</strong></span>
                  </div>

                  <div className="hosp-address-row">
                    <MapPin size={14} className="text-cyan-400 shrink-0" />
                    <span>{h.address?.complete_address || `${h.address?.area || ''}, ${h.address?.city || ''}, ${h.address?.state || ''}`}</span>
                  </div>

                  {/* Bed & Infrastructure Badges */}
                  <div className="hosp-pills-row">
                    <span className="pill-item">
                      🛏️ Total Beds: <strong>{h.capacity?.total_beds || 0}</strong>
                    </span>
                    <span className="pill-item purple">
                      🏥 ICU Beds: <strong>{h.capacity?.icu_beds || 0}</strong>
                    </span>
                    <span className="pill-item emerald">
                      🚑 Ambulances: <strong>{h.capacity?.ambulance_count || 0}</strong>
                    </span>
                  </div>
                </div>

                {/* Administrator & Action Buttons */}
                <div className="hosp-action-col font-sans">
                  <div className="admin-contact-box">
                    <span className="label">Administrator Contact</span>
                    <strong>{h.administrator?.name || 'Admin'}</strong>
                    <span className="email font-mono">{h.administrator?.email || 'N/A'}</span>
                  </div>

                  <div className="action-buttons-row">
                    <button
                      type="button"
                      className="btn-review"
                      onClick={() => setSelectedHospital(h)}
                    >
                      <FileText size={14} /> Review Details
                    </button>

                    {h.status === 'PENDING_VERIFICATION' && (
                      <>
                        <button
                          type="button"
                          className="btn-approve"
                          disabled={processingId === h.id}
                          onClick={() => handleVerifyAction(h.id, 'APPROVED')}
                        >
                          <Check size={14} /> Approve
                        </button>

                        <button
                          type="button"
                          className="btn-reject"
                          disabled={processingId === h.id}
                          onClick={() => {
                            setRejectionTarget({ hospitalId: h.id, hospitalName: h.name });
                            setRejectionReason('');
                          }}
                        >
                          <X size={14} /> Reject
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Custom Rejection Reason Modal */}
      {rejectionTarget && (
        <div className="admin-modal-overlay">
          <div className="admin-modal-box rejection-modal-box font-sans">
            <div className="modal-header-row">
              <div>
                <h3 className="text-red-400 flex items-center gap-2">
                  <AlertTriangle size={20} /> Reject Registration Request
                </h3>
                <p className="text-slate-400 text-xs mt-1">
                  Target Facility: <strong className="text-white">{rejectionTarget.hospitalName}</strong>
                </p>
              </div>
              <button
                type="button"
                className="btn-close-modal"
                onClick={() => setRejectionTarget(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body-space">
              <label className="text-xs font-extrabold text-slate-300 block mb-2">
                Administrative Rejection Audit Reason *
              </label>
              <textarea
                className="rejection-textarea font-sans"
                placeholder="Specify compliance issue or missing document rationale (e.g. NABH accreditation certificate unreadable or license expired)..."
                rows={4}
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
              />
            </div>

            <div className="modal-footer-row">
              <button
                type="button"
                className="btn-close-secondary"
                onClick={() => setRejectionTarget(null)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn-reject flex items-center gap-2 px-5 py-2.5"
                disabled={processingId === rejectionTarget.hospitalId}
                onClick={() => handleVerifyAction(rejectionTarget.hospitalId, 'REJECTED', rejectionReason)}
              >
                <Send size={14} /> Confirm Rejection Notice
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Hospital Full Audit Review Modal */}
      {selectedHospital && (
        <div className="admin-modal-overlay">
          <div className="admin-modal-box font-sans">
            {/* Modal Header */}
            <div className="modal-header-row">
              <div>
                <div className="modal-title-flex">
                  <h3>{selectedHospital.name}</h3>
                  <span className="modal-id-tag">ID: {selectedHospital.id}</span>
                </div>
                <p>Full Administrative Submission Audit Packet</p>
              </div>

              <button
                type="button"
                className="btn-close-modal"
                onClick={() => setSelectedHospital(null)}
              >
                <X size={18} />
              </button>
            </div>

            {/* Audit Content Grid */}
            <div className="modal-body-grid">
              {/* Section 1: Basic Info */}
              <div className="audit-section-box">
                <h4>1. Registration & Classification</h4>
                <p>Registration #: <strong className="font-mono">{selectedHospital.registration_number}</strong></p>
                <p>License #: <strong className="font-mono">{selectedHospital.license_number}</strong></p>
                <p>Category: <strong>{selectedHospital.category}</strong></p>
                <p>NABH Accredited: <strong className="text-emerald-400">{selectedHospital.has_nabh_accreditation ? 'YES (Verified)' : 'NO'}</strong></p>
              </div>

              {/* Section 2: Address & Location */}
              <div className="audit-section-box">
                <h4>2. Physical Location</h4>
                <p>Address: <strong>{selectedHospital.address?.complete_address}</strong></p>
                <p>City / State: <strong>{selectedHospital.address?.city}, {selectedHospital.address?.state} - {selectedHospital.address?.pincode}</strong></p>
                <p>GPS Coordinates: <strong className="font-mono text-cyan-400">{selectedHospital.address?.latitude}, {selectedHospital.address?.longitude}</strong></p>
              </div>

              {/* Section 3: Infrastructure */}
              <div className="audit-section-box">
                <h4>3. Capacity & Emergency Infrastructure</h4>
                <p>Total Beds: <strong>{selectedHospital.capacity?.total_beds}</strong></p>
                <p>ICU Beds: <strong className="text-purple-300">{selectedHospital.capacity?.icu_beds}</strong></p>
                <p>24/7 Emergency: <strong className="text-emerald-400">{selectedHospital.capacity?.has_emergency_dept ? 'YES' : 'NO'}</strong></p>
                <p>Trauma Center: <strong className="text-emerald-400">{selectedHospital.capacity?.has_trauma_center ? 'YES' : 'NO'}</strong></p>
              </div>

              {/* Section 4: Admin Details */}
              <div className="audit-section-box">
                <h4>4. Administrator Contact</h4>
                <p>Name: <strong>{selectedHospital.administrator?.name}</strong></p>
                <p>Designation: <strong>{selectedHospital.administrator?.designation}</strong></p>
                <p>Email: <strong className="font-mono">{selectedHospital.administrator?.email}</strong></p>
                <p>Mobile: <strong className="font-mono">{selectedHospital.administrator?.mobile}</strong></p>
              </div>
            </div>

            {/* Section 5: Documents Links */}
            <div className="audit-docs-box">
              <h4>5. Uploaded Verification Documents</h4>
              <div className="docs-links-grid">
                {selectedHospital.documents?.registration_cert_url && (
                  <a
                    href={selectedHospital.documents.registration_cert_url}
                    target="_blank"
                    rel="noreferrer"
                    className="doc-link-item"
                  >
                    <ExternalLink size={14} /> Registration Cert
                  </a>
                )}
                {selectedHospital.documents?.govt_license_url && (
                  <a
                    href={selectedHospital.documents.govt_license_url}
                    target="_blank"
                    rel="noreferrer"
                    className="doc-link-item"
                  >
                    <ExternalLink size={14} /> Govt License
                  </a>
                )}
                {selectedHospital.documents?.pan_url && (
                  <a
                    href={selectedHospital.documents.pan_url}
                    target="_blank"
                    rel="noreferrer"
                    className="doc-link-item"
                  >
                    <ExternalLink size={14} /> PAN Document
                  </a>
                )}
                {selectedHospital.documents?.exterior_image_url && (
                  <a
                    href={selectedHospital.documents.exterior_image_url}
                    target="_blank"
                    rel="noreferrer"
                    className="doc-link-item"
                  >
                    <ExternalLink size={14} /> Exterior Photo
                  </a>
                )}
              </div>
            </div>

            {/* Modal Actions */}
            <div className="modal-footer-row">
              <button
                type="button"
                className="btn-close-secondary"
                onClick={() => setSelectedHospital(null)}
              >
                Close Audit View
              </button>

              {selectedHospital.status === 'PENDING_VERIFICATION' && (
                <>
                  <button
                    type="button"
                    className="btn-approve"
                    onClick={() => handleVerifyAction(selectedHospital.id, 'APPROVED')}
                  >
                    <Check size={16} /> Approve Hospital Application
                  </button>

                  <button
                    type="button"
                    className="btn-reject"
                    onClick={() => {
                      setRejectionTarget({ hospitalId: selectedHospital.id, hospitalName: selectedHospital.name });
                      setRejectionReason('');
                      setSelectedHospital(null);
                    }}
                  >
                    <X size={16} /> Reject Application
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
