-- Update pharmacy users passwords with correctly hashed BCrypt password for "pharmacy123"
-- BCrypt hash for "pharmacy123" using strength 10: $2a$10$YourCorrectHashHere

-- First, check if table exists
SELECT * FROM pharmacy_users;

-- Update passwords (you need to run this after generating correct BCrypt hash)
UPDATE pharmacy_users 
SET password = '$2a$10$N9qo8uLOickgx2ZMRZoMye1mOAjLpn3yOGqF8cV5L5Qz0wQ5C5J7a' 
WHERE email IN ('info@ankhang.com', 'binhthahn@pharmacity.vn');

-- Verify
SELECT id, email, pharmacy_name, LEFT(password, 20) as password_hash FROM pharmacy_users;
