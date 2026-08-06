import requests
import json

r = requests.get(
    'https://nominatim.openstreetmap.org/search',
    params={'q': 'hospital in hyderabad', 'format': 'json', 'limit': 35},
    headers={'User-Agent': 'SupabaseSeeder/1.0'}
).json()

diseases_list = [
    ['Cardiology', 'Emergency Trauma', 'Heart Failure', 'Cardiac Arrest'],
    ['Oncology', 'Cancer Care', 'Chemotherapy', 'Radiation Therapy'],
    ['Pediatrics', 'Neonatal Care', 'Child Development', 'Pediatric ICU'],
    ['Pulmonology', 'COVID/Respiratory', 'Asthma', 'Pneumonia'],
    ['Neurology', 'Neurosurgery', 'Epilepsy', 'Stroke Management'],
    ['Orthopedics', 'Joint Replacement', 'Bone Fracture', 'Spine Care'],
    ['Nephrology', 'Kidney Dialysis', 'Urology', 'Renal Transplant'],
    ['General Medicine', 'Gastroenterology', 'Diabetes', 'Infectious Diseases']
]

hospitals = []
seen = set()

for idx, item in enumerate(r):
    raw_name = item.get('display_name').split(',')[0].strip()
    if len(raw_name) < 4 or raw_name.lower() in ['hospital', 'area hospital', 'habeeb nagar main road']:
        continue
    if raw_name in seen:
        continue
    seen.add(raw_name)

    lat = float(item['lat'])
    lon = float(item['lon'])
    addr_parts = item.get('display_name').split(',')
    addr = f"{raw_name}, {addr_parts[1].strip() if len(addr_parts)>1 else 'Hyderabad'}, Hyderabad, Telangana"
    diseases = diseases_list[idx % len(diseases_list)]
    phone = f"+91-40-{23600000 + (idx * 13579) % 899999}"

    hospitals.append({
        'name': raw_name,
        'address': addr,
        'lat': lat,
        'lon': lon,
        'phone': phone,
        'diseases': diseases,
        'beds': 100 + (idx * 25) % 200,
        'avail': 30 + (idx * 9) % 50,
        'icu': 15 + (idx * 4) % 25,
        'avail_icu': 2 + (idx % 7)
    })

sql_lines = [
    "-- 1. Create Extension & Hospitals Table",
    'CREATE EXTENSION IF NOT EXISTS "pgcrypto";',
    "",
    "DROP TABLE IF EXISTS public.hospitals CASCADE;",
    "",
    "CREATE TABLE public.hospitals (",
    "    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),",
    "    name VARCHAR(255) NOT NULL,",
    "    address TEXT NOT NULL,",
    "    latitude DOUBLE PRECISION NOT NULL,",
    "    longitude DOUBLE PRECISION NOT NULL,",
    "    contact_phone VARCHAR(50) NOT NULL,",
    "    diseases_allocated TEXT[] DEFAULT ARRAY['General Medicine'],",
    "    total_beds INTEGER DEFAULT 50,",
    "    available_beds INTEGER DEFAULT 20,",
    "    icu_beds INTEGER DEFAULT 10,",
    "    available_icu INTEGER DEFAULT 3,",
    "    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL",
    ");",
    "",
    "ALTER TABLE public.hospitals ENABLE ROW LEVEL SECURITY;",
    'CREATE POLICY "Allow public read access to hospitals" ON public.hospitals FOR SELECT USING (true);',
    "",
    "-- 2. Insert Real Hyderabad Hospitals with Disease Allocations",
    "INSERT INTO public.hospitals (id, name, address, latitude, longitude, contact_phone, diseases_allocated, total_beds, available_beds, icu_beds, available_icu) VALUES"
]

val_strings = []
for h in hospitals:
    clean_name = h['name'].replace("'", "''")
    clean_addr = h['address'].replace("'", "''")
    dis_formatted = "ARRAY[" + ", ".join([f"'{d}'" for d in h['diseases']]) + "]"
    val = f"(gen_random_uuid(), '{clean_name}', '{clean_addr}', {h['lat']}, {h['lon']}, '{h['phone']}', {dis_formatted}, {h['beds']}, {h['avail']}, {h['icu']}, {h['avail_icu']})"
    val_strings.append(val)

sql_lines.append(",\n".join(val_strings) + ";")

with open("supabase_hyderabad_hospitals_seed.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(sql_lines))

print(f"Successfully generated SQL seed script with {len(hospitals)} real Hyderabad hospitals!")
