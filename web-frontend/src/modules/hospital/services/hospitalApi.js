import { fetchWithFallback } from '../../../services/apiClient';

const API_ROUTE_PREFIX = '/api/v1/hospital';

const formatErrorDetail = (detail, fallbackMsg) => {
  if (!detail) return fallbackMsg;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => {
      const fieldPath = d.loc ? d.loc.filter(x => x !== 'body').join(' ➔ ') : 'Field';
      return `${fieldPath}: ${d.msg}`;
    }).join(' | ');
  }
  if (typeof detail === 'object') {
    return JSON.stringify(detail);
  }
  return fallbackMsg;
};

export const registerHospital = async (formData) => {
  // Transform flat frontend state into nested schema expected by FastAPI backend
  const payload = {
    basic_info: {
      hospital_name: formData.hospital_name || 'Hospital',
      hospital_type: formData.hospital_type || 'SMALL',
      category: formData.category || 'CHC',
      registration_number: formData.registration_number || 'REG-PENDING',
      license_number: formData.license_number || 'LIC-PENDING',
      has_nabh_accreditation: Boolean(formData.has_nabh_accreditation),
      nabh_number: formData.has_nabh_accreditation ? formData.nabh_number : null,
      gst_number: formData.gst_number || null
    },
    address: {
      country: formData.country || 'India',
      state: formData.state || 'Telangana',
      district: formData.district || 'Hyderabad',
      city: formData.city || 'Hyderabad',
      area: formData.area || 'Hyderabad',
      pincode: formData.pincode || '500001',
      complete_address: formData.complete_address || 'Hyderabad, Telangana',
      latitude: parseFloat(formData.latitude) || 17.4126,
      longitude: parseFloat(formData.longitude) || 78.4482
    },
    capacity: {
      total_beds: parseInt(formData.total_beds) || 0,
      icu_beds: parseInt(formData.icu_beds) || 0,
      has_emergency_dept: Boolean(formData.has_emergency_dept),
      has_trauma_center: Boolean(formData.has_trauma_center),
      has_blood_bank: Boolean(formData.has_blood_bank),
      ambulance_count: parseInt(formData.ambulance_count) || 0,
      departments: formData.departments || [],
      specializations: formData.specializations || []
    },
    administrator: {
      name: formData.admin_name || 'Hospital Admin',
      designation: formData.admin_designation || 'Administrator',
      email: formData.admin_email || 'admin@hospital.com',
      mobile: formData.admin_mobile || '+919999999999',
      password: formData.admin_password || 'Password123!'
    },
    documents: {
      registration_cert_url: formData.registration_cert_url || '',
      govt_license_url: formData.govt_license_url || '',
      nabh_cert_url: formData.nabh_cert_url || null,
      pan_url: formData.pan_url || '',
      gst_url: formData.gst_url || null,
      exterior_image_url: formData.exterior_image_url || '',
      logo_url: formData.logo_url || ''
    },
    integration: {
      integration_mode: formData.hospital_type === 'SMALL' ? 'DASHBOARD' : formData.integration_mode || 'DASHBOARD',
      base_url: formData.base_url || null,
      callback_url: formData.callback_url || null,
      api_doc_url: formData.api_doc_url || null,
      tech_contact_name: formData.tech_contact_name || null,
      tech_contact_email: formData.tech_contact_email || null
    }
  };

  const response = await fetchWithFallback(`${API_ROUTE_PREFIX}/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(formatErrorDetail(data.detail, 'Failed to submit hospital registration.'));
  }

  return data;
};

export const loginHospital = async (email, password) => {
  const response = await fetchWithFallback(`${API_ROUTE_PREFIX}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(formatErrorDetail(data.detail, 'Invalid email or password.'));
  }

  return data;
};

export const uploadDocument = async (file) => {
  const body = new FormData();
  body.append('file', file);

  const response = await fetchWithFallback(`${API_ROUTE_PREFIX}/upload-doc`, {
    method: 'POST',
    body
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(formatErrorDetail(data.detail, 'File upload failed.'));
  }

  return data.url;
};

export const checkVerificationStatus = async (hospitalId) => {
  const response = await fetchWithFallback(`${API_ROUTE_PREFIX}/verification-status/${hospitalId}`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(formatErrorDetail(data.detail, 'Unable to fetch status.'));
  }
  return data;
};

