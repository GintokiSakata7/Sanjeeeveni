export const HOSPITAL_TYPES = {
  SMALL: 'SMALL',
  LARGE: 'LARGE'
};

export const HOSPITAL_CATEGORIES = {
  CHC: 'CHC',
  MULTI_SPECIALITY: 'MULTI_SPECIALITY',
  SUPER_SPECIALITY: 'SUPER_SPECIALITY'
};

export const INTEGRATION_MODES = {
  REST_API: 'REST_API',
  HL7_FHIR: 'HL7_FHIR',
  CUSTOM_API: 'CUSTOM_API',
  DASHBOARD: 'DASHBOARD'
};

export const VERIFICATION_STATUS = {
  PENDING_VERIFICATION: 'PENDING_VERIFICATION',
  APPROVED: 'APPROVED',
  REJECTED: 'REJECTED',
  SUSPENDED: 'SUSPENDED'
};

export const INITIAL_REGISTRATION_STATE = {
  // Step 1: Basic Info
  hospital_name: '',
  hospital_type: HOSPITAL_TYPES.SMALL,
  category: HOSPITAL_CATEGORIES.CHC,
  registration_number: '',
  license_number: '',
  has_nabh_accreditation: false,
  nabh_number: '',
  gst_number: '',

  // Step 2: Address & Location
  country: 'India',
  state: 'Telangana',
  district: 'Hyderabad',
  city: 'Hyderabad',
  area: 'Banjara Hills',
  pincode: '500034',
  complete_address: '',
  latitude: 17.4126,
  longitude: 78.4482,

  // Step 3: Hospital Details & Capacity
  total_beds: 50,
  icu_beds: 10,
  has_emergency_dept: true,
  has_trauma_center: false,
  has_blood_bank: false,
  ambulance_count: 2,
  departments: ['Emergency', 'General Medicine', 'ICU'],
  specializations: ['General Physician', 'Cardiology', 'Orthopedics'],

  // Step 4: Administrator
  admin_name: '',
  admin_designation: 'Medical Director',
  admin_email: '',
  admin_mobile: '',
  admin_password: '',
  admin_confirm_password: '',

  // Step 5: Verification Documents
  registration_cert_url: '',
  govt_license_url: '',
  nabh_cert_url: '',
  pan_url: '',
  gst_url: '',
  exterior_image_url: '',
  logo_url: '',

  // Step 6: Integration
  integration_mode: INTEGRATION_MODES.DASHBOARD,
  base_url: '',
  callback_url: '',
  api_doc_url: '',
  tech_contact_name: '',
  tech_contact_email: ''
};
