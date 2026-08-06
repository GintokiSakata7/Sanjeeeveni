import React from 'react';
import { UploadCloud, CheckCircle2, FileText, Image as ImageIcon, ShieldCheck } from 'lucide-react';

export default function Step5Documents({ formData, handleFileUpload, uploadingField }) {
  const documentList = [
    {
      field: 'registration_cert_url',
      label: 'Hospital Registration Certificate *',
      type: 'pdf_img',
      required: true,
      desc: 'Official Clinical Establishment Registration PDF or Image'
    },
    {
      field: 'govt_license_label',
      fieldKey: 'govt_license_url',
      label: 'Government Health License *',
      type: 'pdf_img',
      required: true,
      desc: 'State Government Health Dept License Certificate'
    },
    {
      fieldKey: 'pan_url',
      label: 'PAN Card (Hospital / Trust / Entity) *',
      type: 'pdf_img',
      required: true,
      desc: 'Government issued Permanent Account Number document'
    },
    {
      fieldKey: 'exterior_image_url',
      label: 'Hospital Exterior Building Photo *',
      type: 'img',
      required: true,
      desc: 'Front entrance / building exterior photo showing hospital signage'
    },
    {
      fieldKey: 'logo_url',
      label: 'Hospital Logo Image *',
      type: 'img',
      required: true,
      desc: 'High resolution hospital emblem or logo PNG/JPG'
    },
    {
      fieldKey: 'nabh_cert_url',
      label: 'NABH Certificate (Optional)',
      type: 'pdf_img',
      required: false,
      desc: 'Required if NABH Accreditation was selected in Step 1'
    },
    {
      fieldKey: 'gst_url',
      label: 'GST Certificate (Optional)',
      type: 'pdf_img',
      required: false,
      desc: 'GST tax registration document'
    }
  ];

  return (
    <div className="step-card">
      <div className="step-card-header">
        <UploadCloud className="step-icon text-indigo-400" size={24} />
        <div>
          <h3>Step 5: Verification Documents & Media Upload</h3>
          <p>Upload official certificates and hospital imagery for verification and trust compliance</p>
        </div>
      </div>

      <div className="doc-upload-grid">
        {documentList.map((doc) => {
          const fieldName = doc.fieldKey || doc.field;
          const currentUrl = formData[fieldName];
          const isUploading = uploadingField === fieldName;

          return (
            <div key={fieldName} className={`doc-upload-card ${currentUrl ? 'uploaded' : ''}`}>
              <div className="doc-info">
                <div className="doc-title-row">
                  {doc.type === 'img' ? (
                    <ImageIcon size={18} className="text-purple-400" />
                  ) : (
                    <FileText size={18} className="text-cyan-400" />
                  )}
                  <h5>{doc.label}</h5>
                </div>
                <p>{doc.desc}</p>
              </div>

              {/* Upload Dropzone */}
              <div className="upload-dropzone">
                {currentUrl ? (
                  <div className="uploaded-file-preview">
                    <CheckCircle2 size={20} className="text-emerald-400" />
                    <span className="file-url-text truncate">{currentUrl}</span>
                    <label className="reupload-btn">
                      Change
                      <input
                        type="file"
                        accept="image/*,application/pdf"
                        onChange={(e) => {
                          if (e.target.files && e.target.files[0]) {
                            handleFileUpload(fieldName, e.target.files[0]);
                          }
                        }}
                      />
                    </label>
                  </div>
                ) : (
                  <label className="upload-input-label">
                    {isUploading ? (
                      <span className="uploading-text">Uploading to Supabase Storage...</span>
                    ) : (
                      <>
                        <UploadCloud size={20} className="text-slate-400" />
                        <span>Choose File or Drag & Drop</span>
                        <span className="file-types-sub">PDF, PNG, JPG (Max 10MB)</span>
                      </>
                    )}
                    <input
                      type="file"
                      disabled={isUploading}
                      accept="image/*,application/pdf"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          handleFileUpload(fieldName, e.target.files[0]);
                        }
                      }}
                    />
                  </label>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
