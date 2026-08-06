-- 1. Create Extension & Hospitals Table
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

DROP TABLE IF EXISTS public.hospitals CASCADE;

CREATE TABLE public.hospitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    contact_phone VARCHAR(50) NOT NULL,
    diseases_allocated TEXT[] DEFAULT ARRAY['General Medicine'],
    total_beds INTEGER DEFAULT 50,
    available_beds INTEGER DEFAULT 20,
    icu_beds INTEGER DEFAULT 10,
    available_icu INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.hospitals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read access to hospitals" ON public.hospitals FOR SELECT USING (true);

-- 2. Insert Real Hyderabad Hospitals with Disease Allocations
INSERT INTO public.hospitals (id, name, address, latitude, longitude, contact_phone, diseases_allocated, total_beds, available_beds, icu_beds, available_icu) VALUES
(gen_random_uuid(), 'Apollo', 'Apollo, Masjid e Noor, Hyderabad, Telangana', 17.3882657, 78.4610655, '+91-40-23600000', ARRAY['Cardiology', 'Emergency Trauma', 'Heart Failure', 'Cardiac Arrest'], 100, 30, 15, 2),
(gen_random_uuid(), 'MNJ Institute of Oncology and Regional Cancer Center', 'MNJ Institute of Oncology and Regional Cancer Center, Jamia Masjid Road, Hyderabad, Telangana', 17.392244, 78.4601927, '+91-40-23613579', ARRAY['Oncology', 'Cancer Care', 'Chemotherapy', 'Radiation Therapy'], 125, 39, 19, 3),
(gen_random_uuid(), 'Nisha Hospital', 'Nisha Hospital, Mehdi Nawaj Jung Road, Hyderabad, Telangana', 17.3944196, 78.4626817, '+91-40-23654316', ARRAY['Neurology', 'Neurosurgery', 'Epilepsy', 'Stroke Management'], 200, 66, 31, 6),
(gen_random_uuid(), 'Mansoor Maternity And Childrens Hospital', 'Mansoor Maternity And Childrens Hospital, Darus Salm Road, Hyderabad, Telangana', 17.393511, 78.4568185, '+91-40-23667895', ARRAY['Orthopedics', 'Joint Replacement', 'Bone Fracture', 'Spine Care'], 225, 75, 35, 7),
(gen_random_uuid(), 'D.K.GOVT. HOMOEO HOSPITAL', 'D.K.GOVT. HOMOEO HOSPITAL, Goshamahal Road, Hyderabad, Telangana', 17.3841667, 78.4562354, '+91-40-23681474', ARRAY['Nephrology', 'Kidney Dialysis', 'Urology', 'Renal Transplant'], 250, 34, 39, 8),
(gen_random_uuid(), 'SRISHTI EYE CENTRE', 'SRISHTI EYE CENTRE, Dargah Road, Hyderabad, Telangana', 17.3949495, 78.4573924, '+91-40-23695053', ARRAY['General Medicine', 'Gastroenterology', 'Diabetes', 'Infectious Diseases'], 275, 43, 18, 2),
(gen_random_uuid(), 'MK Dentistry', 'MK Dentistry, 10-2-229/A, Hyderabad, Telangana', 17.3951477, 78.4556625, '+91-40-23708632', ARRAY['Cardiology', 'Emergency Trauma', 'Heart Failure', 'Cardiac Arrest'], 100, 52, 22, 3),
(gen_random_uuid(), 'Medicure Diagnostic and Research Center(Alekhya Scanning Center)', 'Medicure Diagnostic and Research Center(Alekhya Scanning Center), Asif Nagar Main Road, Hyderabad, Telangana', 17.3953666, 78.4544152, '+91-40-23722211', ARRAY['Oncology', 'Cancer Care', 'Chemotherapy', 'Radiation Therapy'], 125, 61, 26, 4),
(gen_random_uuid(), 'Healing Touch Hospital', 'Healing Touch Hospital, Asif Nagar road, Hyderabad, Telangana', 17.3903338, 78.4514802, '+91-40-23735790', ARRAY['Pediatrics', 'Neonatal Care', 'Child Development', 'Pediatric ICU'], 150, 70, 30, 5),
(gen_random_uuid(), 'Nice Hospital', 'Nice Hospital, vijaynagar colony road, Hyderabad, Telangana', 17.3972385, 78.4562128, '+91-40-23749369', ARRAY['Pulmonology', 'COVID/Respiratory', 'Asthma', 'Pneumonia'], 175, 79, 34, 6),
(gen_random_uuid(), 'Niloufer Hospital', 'Niloufer Hospital, Niloufer hospital road, Hyderabad, Telangana', 17.3986812, 78.4610376, '+91-40-23762948', ARRAY['Neurology', 'Neurosurgery', 'Epilepsy', 'Stroke Management'], 200, 38, 38, 7),
(gen_random_uuid(), 'RAMA EYE HOSPITAL', 'RAMA EYE HOSPITAL, Nampally Station Road, Hyderabad, Telangana', 17.3910435, 78.4712635, '+91-40-23790106', ARRAY['Nephrology', 'Kidney Dialysis', 'Urology', 'Renal Transplant'], 250, 56, 21, 2),
(gen_random_uuid(), 'Mahatma Sriramachandra Centenary Memorial Hospital', 'Mahatma Sriramachandra Centenary Memorial Hospital, Asif Nagar Main Road, Hyderabad, Telangana', 17.3948133, 78.4525058, '+91-40-23803685', ARRAY['General Medicine', 'Gastroenterology', 'Diabetes', 'Infectious Diseases'], 275, 65, 25, 3),
(gen_random_uuid(), 'Nirmala Maternity', 'Nirmala Maternity, Orthopaedic & General Hospital, Hyderabad, Telangana', 17.3943495, 78.451799, '+91-40-23817264', ARRAY['Cardiology', 'Emergency Trauma', 'Heart Failure', 'Cardiac Arrest'], 100, 74, 29, 4),
(gen_random_uuid(), 'Rohan Hospital', 'Rohan Hospital, Asif Nagar Main Road, Hyderabad, Telangana', 17.3946344, 78.4519084, '+91-40-23830843', ARRAY['Oncology', 'Cancer Care', 'Chemotherapy', 'Radiation Therapy'], 125, 33, 33, 5),
(gen_random_uuid(), 'Lazarus Hospitals', 'Lazarus Hospitals, Mehdi Nawaj Jung Road, Hyderabad, Telangana', 17.3995348, 78.4630345, '+91-40-23844422', ARRAY['Pediatrics', 'Neonatal Care', 'Child Development', 'Pediatric ICU'], 150, 42, 37, 6),
(gen_random_uuid(), 'Primary Veternary Hospital', 'Primary Veternary Hospital, Rai Janakiprasad Road, Hyderabad, Telangana', 17.3979621, 78.4543414, '+91-40-23858001', ARRAY['Pulmonology', 'COVID/Respiratory', 'Asthma', 'Pneumonia'], 175, 51, 16, 7),
(gen_random_uuid(), 'Medwin Hospital', 'Medwin Hospital, Fateh Maidan Lane, Hyderabad, Telangana', 17.3936011, 78.471946, '+91-40-23871580', ARRAY['Neurology', 'Neurosurgery', 'Epilepsy', 'Stroke Management'], 200, 60, 20, 8),
(gen_random_uuid(), 'Jayanti Maternity and Nursing Home', 'Jayanti Maternity and Nursing Home, Nampally Station Road, Hyderabad, Telangana', 17.3893491, 78.4734696, '+91-40-23885159', ARRAY['Orthopedics', 'Joint Replacement', 'Bone Fracture', 'Spine Care'], 225, 69, 24, 2),
(gen_random_uuid(), 'Swarup Eye Centre', 'Swarup Eye Centre, Chapel Road, Hyderabad, Telangana', 17.3950421, 78.4720698, '+91-40-23898738', ARRAY['Nephrology', 'Kidney Dialysis', 'Urology', 'Renal Transplant'], 250, 78, 28, 3),
(gen_random_uuid(), 'Krishna Children''s Hospital', 'Krishna Children''s Hospital, Mehdi Nawaj Jung Road, Hyderabad, Telangana', 17.4021334, 78.4625295, '+91-40-23912317', ARRAY['General Medicine', 'Gastroenterology', 'Diabetes', 'Infectious Diseases'], 275, 37, 32, 4),
(gen_random_uuid(), 'Goshamahal Hospital', 'Goshamahal Hospital, Seena Bakery Ln, Hyderabad, Telangana', 17.3818518, 78.4727287, '+91-40-23925896', ARRAY['Cardiology', 'Emergency Trauma', 'Heart Failure', 'Cardiac Arrest'], 100, 46, 36, 5),
(gen_random_uuid(), 'Udai Omni Hospital', 'Udai Omni Hospital, KK Estate Lane, Hyderabad, Telangana', 17.3969132, 78.4722613, '+91-40-23939475', ARRAY['Oncology', 'Cancer Care', 'Chemotherapy', 'Radiation Therapy'], 125, 55, 15, 6),
(gen_random_uuid(), 'Deepa Hospital', 'Deepa Hospital, Old tophknana road, Hyderabad, Telangana', 17.3763924, 78.4676445, '+91-40-23953054', ARRAY['Pediatrics', 'Neonatal Care', 'Child Development', 'Pediatric ICU'], 150, 64, 19, 7),
(gen_random_uuid(), 'Care Hospital', 'Care Hospital, Nampally, Hyderabad, Telangana', 17.3854315, 78.4747114, '+91-40-23966633', ARRAY['Pulmonology', 'COVID/Respiratory', 'Asthma', 'Pneumonia'], 175, 73, 23, 8),
(gen_random_uuid(), 'Neo Retina Eye Care', 'Neo Retina Eye Care, KK Estate Lane, Hyderabad, Telangana', 17.3967872, 78.4728447, '+91-40-23980212', ARRAY['Neurology', 'Neurosurgery', 'Epilepsy', 'Stroke Management'], 200, 32, 27, 2),
(gen_random_uuid(), 'Kailash Diagnostic and Rehabilitation Center', 'Kailash Diagnostic and Rehabilitation Center, Abids to MJ Market Road, Hyderabad, Telangana', 17.3854802, 78.4752171, '+91-40-23993791', ARRAY['Orthopedics', 'Joint Replacement', 'Bone Fracture', 'Spine Care'], 225, 41, 31, 3),
(gen_random_uuid(), 'Aarogya Hospital', 'Aarogya Hospital, Abids to MJ Market Road, Hyderabad, Telangana', 17.3851141, 78.4754102, '+91-40-24007370', ARRAY['Nephrology', 'Kidney Dialysis', 'Urology', 'Renal Transplant'], 250, 50, 35, 4),
(gen_random_uuid(), 'Dr.Shantabai Nursing Home', 'Dr.Shantabai Nursing Home, Abids Road, Hyderabad, Telangana', 17.3913737, 78.4757126, '+91-40-24020949', ARRAY['General Medicine', 'Gastroenterology', 'Diabetes', 'Infectious Diseases'], 275, 59, 39, 5),
(gen_random_uuid(), 'Lotus Children''s Hospital', 'Lotus Children''s Hospital, Lakdikapul, Hyderabad, Telangana', 17.4041136, 78.4611649, '+91-40-24034528', ARRAY['Cardiology', 'Emergency Trauma', 'Heart Failure', 'Cardiac Arrest'], 100, 68, 18, 6),
(gen_random_uuid(), 'Seha Hospital', 'Seha Hospital, FAPCCI Marg, Hyderabad, Telangana', 17.404143, 78.4622929, '+91-40-24048107', ARRAY['Oncology', 'Cancer Care', 'Chemotherapy', 'Radiation Therapy'], 125, 77, 22, 7),
(gen_random_uuid(), 'Mahavir Hospital and Research Centre', 'Mahavir Hospital and Research Centre, Mahavir Marg, Hyderabad, Telangana', 17.4036641, 78.4570626, '+91-40-24061686', ARRAY['Pediatrics', 'Neonatal Care', 'Child Development', 'Pediatric ICU'], 150, 36, 26, 8);