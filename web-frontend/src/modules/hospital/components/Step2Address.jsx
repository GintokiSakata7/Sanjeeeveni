import React from 'react';
import { MapPin, Compass } from 'lucide-react';
import LocationPickerMap from './LocationPickerMap';
import { INDIAN_STATES } from '../constants/hospitalConstants';

export default function Step2Address({ formData, updateField, updateMultipleFields }) {
  const handleLocationChange = (lat, lng) => {
    updateMultipleFields({
      latitude: lat,
      longitude: lng
    });
  };

  return (
    <div className="step-card">
      <div className="step-card-header">
        <MapPin className="step-icon text-red-400" size={24} />
        <div>
          <h3>Step 2: Hospital Location & Address</h3>
          <p>Provide exact physical address details and set precise GPS coordinates for emergency dispatch</p>
        </div>
      </div>

      <div className="form-grid">
        {/* Country */}
        <div className="form-group">
          <label>Country *</label>
          <input
            type="text"
            value={formData.country}
            onChange={(e) => updateField('country', e.target.value)}
            required
          />
        </div>

        {/* State */}
        <div className="form-group">
          <label>State *</label>
          <select
            value={formData.state}
            onChange={(e) => updateField('state', e.target.value)}
          >
            {INDIAN_STATES.map((st) => (
              <option key={st} value={st}>
                {st}
              </option>
            ))}
          </select>
        </div>

        {/* District */}
        <div className="form-group">
          <label>District *</label>
          <input
            type="text"
            placeholder="e.g. Hyderabad"
            value={formData.district}
            onChange={(e) => updateField('district', e.target.value)}
            required
          />
        </div>

        {/* City */}
        <div className="form-group">
          <label>City / Town *</label>
          <input
            type="text"
            placeholder="e.g. Hyderabad"
            value={formData.city}
            onChange={(e) => updateField('city', e.target.value)}
            required
          />
        </div>

        {/* Area */}
        <div className="form-group">
          <label>Area / Locality *</label>
          <input
            type="text"
            placeholder="e.g. Road No 1, Banjara Hills"
            value={formData.area}
            onChange={(e) => updateField('area', e.target.value)}
            required
          />
        </div>

        {/* Pincode */}
        <div className="form-group">
          <label>Pincode *</label>
          <input
            type="text"
            placeholder="e.g. 500034"
            value={formData.pincode}
            onChange={(e) => updateField('pincode', e.target.value)}
            required
          />
        </div>

        {/* Complete Address */}
        <div className="form-group col-span-2">
          <label>Complete Street Address *</label>
          <textarea
            rows={2}
            placeholder="e.g. Door No. 8-2-248/1/7/A, Main Road, Banjara Hills, Hyderabad, Telangana 500034"
            value={formData.complete_address}
            onChange={(e) => updateField('complete_address', e.target.value)}
            required
          />
        </div>
      </div>

      {/* Map Location Picker Component */}
      <LocationPickerMap
        latitude={formData.latitude}
        longitude={formData.longitude}
        onLocationChange={handleLocationChange}
      />
    </div>
  );
}
