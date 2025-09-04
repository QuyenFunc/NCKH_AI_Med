-- Tạo database cho Dia5 Medical AI
CREATE DATABASE IF NOT EXISTS dia5_medical_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Sử dụng database
USE dia5_medical_ai;

-- Tạo user cho ứng dụng (tùy chọn)
-- CREATE USER IF NOT EXISTS 'dia5_user'@'localhost' IDENTIFIED BY 'dia5_password';
-- GRANT ALL PRIVILEGES ON dia5_medical_ai.* TO 'dia5_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Kiểm tra database đã tạo thành công
SHOW DATABASES LIKE 'dia5_medical_ai';
