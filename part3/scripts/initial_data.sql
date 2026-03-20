-- ============================================================
-- HBnB - Initial Data Script
-- ============================================================

-- 1. Administrator user
-- Password: admin1234 (hashed with bcrypt)
INSERT INTO users (id, first_name, last_name, email, password, is_admin)
VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$MTSEhoujf8FmOK1c.ZK/v.p/dQjoGNwiaGQXkzd9Yaib8NzDrzmUa',
    TRUE
);

-- 2. Initial amenities
INSERT INTO amenities (id, name) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'WiFi'),
    ('550e8400-e29b-41d4-a716-446655440002', 'Swimming Pool'),
    ('550e8400-e29b-41d4-a716-446655440003', 'Air Conditioning');
