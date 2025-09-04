-- Database Schema for Dia5 Medical AI App
-- MySQL Database

CREATE DATABASE dia5_medical_app;
USE dia5_medical_app;

-- Users table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,
    is_profile_complete BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- User Profiles table
CREATE TABLE user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    birth_year INT,
    gender ENUM('male', 'female', 'other'),
    province VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Medical History table
CREATE TABLE medical_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    chronic_diseases TEXT, -- JSON array of diseases
    allergies TEXT, -- JSON array of allergies
    current_medications TEXT, -- JSON array of medications
    smoking_status ENUM('never', 'former', 'current'),
    drinking_frequency ENUM('never', 'occasionally', 'regularly'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Chat History table
CREATE TABLE chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    message TEXT NOT NULL,
    sender ENUM('user', 'bot') NOT NULL,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- News Articles table
CREATE TABLE news_articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,
    link VARCHAR(1000),
    image_url VARCHAR(1000),
    category VARCHAR(100),
    source VARCHAR(100) DEFAULT 'suckhoedoisong.vn',
    published_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- User Bookmarks table
CREATE TABLE user_bookmarks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    news_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (news_id) REFERENCES news_articles(id) ON DELETE CASCADE,
    UNIQUE KEY unique_bookmark (user_id, news_id)
);

-- Diagnosis History table
CREATE TABLE diagnosis_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    symptoms TEXT NOT NULL,
    diagnosis_result TEXT,
    confidence_score DECIMAL(3,2),
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_medical_history_user_id ON medical_history(user_id);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);
CREATE INDEX idx_news_articles_category ON news_articles(category);
CREATE INDEX idx_news_articles_published_date ON news_articles(published_date);
CREATE INDEX idx_user_bookmarks_user_id ON user_bookmarks(user_id);
CREATE INDEX idx_diagnosis_history_user_id ON diagnosis_history(user_id);

-- Insert sample provinces (Vietnamese provinces)
CREATE TABLE provinces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO provinces (name) VALUES 
('An Giang'), ('Bà Rịa - Vũng Tàu'), ('Bạc Liêu'), ('Bắc Giang'), ('Bắc Kạn'),
('Bắc Ninh'), ('Bến Tre'), ('Bình Dương'), ('Bình Định'), ('Bình Phước'),
('Bình Thuận'), ('Cà Mau'), ('Cao Bằng'), ('Cần Thơ'), ('Đà Nẵng'),
('Đắk Lắk'), ('Đắk Nông'), ('Điện Biên'), ('Đồng Nai'), ('Đồng Tháp'),
('Gia Lai'), ('Hà Giang'), ('Hà Nam'), ('Hà Nội'), ('Hà Tĩnh'),
('Hải Dương'), ('Hải Phòng'), ('Hậu Giang'), ('Hòa Bình'), ('Hồ Chí Minh'),
('Hưng Yên'), ('Khánh Hòa'), ('Kiên Giang'), ('Kon Tum'), ('Lai Châu'),
('Lạng Sơn'), ('Lào Cai'), ('Lâm Đồng'), ('Long An'), ('Nam Định'),
('Nghệ An'), ('Ninh Bình'), ('Ninh Thuận'), ('Phú Thọ'), ('Phú Yên'),
('Quảng Bình'), ('Quảng Nam'), ('Quảng Ngãi'), ('Quảng Ninh'), ('Quảng Trị'),
('Sóc Trăng'), ('Sơn La'), ('Tây Ninh'), ('Thái Bình'), ('Thái Nguyên'),
('Thanh Hóa'), ('Thừa Thiên Huế'), ('Tiền Giang'), ('Trà Vinh'), ('Tuyên Quang'),
('Vĩnh Long'), ('Vĩnh Phúc'), ('Yên Bái');

-- Insert sample chronic diseases
CREATE TABLE chronic_diseases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(100)
);

INSERT INTO chronic_diseases (name, category) VALUES 
('Tăng huyết áp', 'Tim mạch'),
('Tiểu đường type 1', 'Nội tiết'),
('Tiểu đường type 2', 'Nội tiết'),
('Hen suyễn', 'Hô hấp'),
('Bệnh tim mạch', 'Tim mạch'),
('Cholesterol cao', 'Tim mạch'),
('Viêm khớp', 'Cơ xương khớp'),
('Loãng xương', 'Cơ xương khớp'),
('Trầm cảm', 'Tâm thần'),
('Lo âu', 'Tâm thần'),
('Béo phì', 'Chuyển hóa'),
('Bệnh thận', 'Thận - Tiết niệu'),
('Bệnh gan', 'Tiêu hóa'),
('Ung thư', 'Ung bướu');
