import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://qoeidmvhsbggbclezfsl.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFvZWlkbXZoc2JnZ2JjbGV6ZnNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2MDY4ODYsImV4cCI6MjA4MDE4Mjg4Nn0.cf6kIAIlbrMYwfbrDUxhD6-SBMFZ7I0Jog334Ok3NLM';

export const supabase = createClient(supabaseUrl, supabaseKey);
