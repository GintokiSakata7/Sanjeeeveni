import { createClient } from '@supabase/supabase-js';

const defaultUrl = 'https://tdbtgoqwetpwuujzccbw.supabase.co';
const defaultKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRkYnRnb3F3ZXRwd3V1anpjY2J3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NTk0MDM4OSwiZXhwIjoyMTAxNTE2Mzg5fQ.0YXIO84KzhBiwcOuo1NTWaGe4aJubXK6p8fkqCGNjQs';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || defaultUrl;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || defaultKey;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
