-- =====================================================================
-- Galactic Gains — Database Setup
-- Run this in Supabase SQL Editor to set up additional tables and seed data.
-- The three core tables (physical_profile, equipment_inventory, food_preferences)
-- should already exist.
-- =====================================================================

-- Optional: Recommendation History table
-- This lets Gemini review past suggestions to avoid repeats.
CREATE TABLE IF NOT EXISTS recommendation_history (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now(),
    user_name TEXT NOT NULL,
    workout TEXT,
    dinner TEXT
);

-- Seed Ashley's profile (update if already exists)
INSERT INTO physical_profile (age, height_in, weight_lbs, medical_notes, user_name)
VALUES (44, 63, 111, 'Weight maintenance, increasing health and stamina. Harrington rods in back — avoid high-impact spinal compression.', 'Ashley')
ON CONFLICT DO NOTHING;

-- Seed placeholder users
INSERT INTO physical_profile (age, height_in, weight_lbs, medical_notes, user_name)
VALUES
    (0, 0, 0, '', 'User A'),
    (0, 0, 0, '', 'User B'),
    (0, 0, 0, '', 'User C'),
    (0, 0, 0, '', 'User D')
ON CONFLICT DO NOTHING;
