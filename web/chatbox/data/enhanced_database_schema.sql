-- Enhanced Database Schema for Dia5 Medical AI App
-- Professional Medical Data Structure for AI Analysis
-- MySQL Database with Normalized Relational Tables

CREATE DATABASE dia5_medical_ai;
USE dia5_medical_ai;

-- ============================================================================
-- CORE USER MANAGEMENT TABLES
-- ============================================================================

-- Users table (unchanged, already good)
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,
    is_profile_complete BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- User basic demographics
CREATE TABLE user_demographics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    birth_year INT NOT NULL,
    birth_month INT, -- For more precise age calculation
    gender ENUM('male', 'female', 'other') NOT NULL,
    height_cm INT, -- Height in centimeters
    weight_kg DECIMAL(5,2), -- Weight in kilograms
    blood_type ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'unknown'),
    province_id INT,
    occupation VARCHAR(100),
    education_level ENUM('primary', 'secondary', 'high_school', 'bachelor', 'master', 'phd', 'other'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_demographics_user_id (user_id),
    INDEX idx_demographics_age (birth_year),
    INDEX idx_demographics_gender (gender)
);

-- ============================================================================
-- GEOGRAPHIC AND REFERENCE DATA
-- ============================================================================

-- Provinces/States table
CREATE TABLE provinces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10),
    region ENUM('north', 'central', 'south'),
    climate ENUM('tropical', 'subtropical', 'temperate'),
    endemic_diseases TEXT, -- JSON array of common diseases in this region
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MEDICAL KNOWLEDGE BASE TABLES
-- ============================================================================

-- Medical specialties
CREATE TABLE medical_specialties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_specialty_id INT, -- For hierarchical specialties
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_specialty_id) REFERENCES medical_specialties(id)
);

-- Disease categories and classifications
CREATE TABLE disease_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    icd10_code VARCHAR(20), -- International Classification of Diseases
    description TEXT,
    severity_level ENUM('mild', 'moderate', 'severe', 'critical'),
    is_chronic BOOLEAN DEFAULT FALSE,
    is_hereditary BOOLEAN DEFAULT FALSE,
    is_contagious BOOLEAN DEFAULT FALSE,
    specialty_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (specialty_id) REFERENCES medical_specialties(id),
    INDEX idx_disease_icd10 (icd10_code),
    INDEX idx_disease_chronic (is_chronic),
    INDEX idx_disease_severity (severity_level)
);

-- Medications database
CREATE TABLE medications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200),
    brand_names TEXT, -- JSON array of brand names
    drug_class VARCHAR(100),
    dosage_forms TEXT, -- JSON array: ["tablet", "syrup", "injection"]
    common_dosages TEXT, -- JSON array: ["100mg", "500mg"]
    contraindications TEXT, -- JSON array of conditions where this drug should not be used
    side_effects TEXT, -- JSON array of known side effects
    interactions TEXT, -- JSON array of drug interactions
    pregnancy_category ENUM('A', 'B', 'C', 'D', 'X', 'unknown'),
    requires_prescription BOOLEAN DEFAULT TRUE,
    is_controlled_substance BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_medication_name (name),
    INDEX idx_medication_generic (generic_name),
    INDEX idx_medication_class (drug_class)
);

-- Allergy types and allergens
CREATE TABLE allergen_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL, -- 'drug', 'food', 'environmental', 'contact'
    name VARCHAR(200) NOT NULL,
    common_symptoms TEXT, -- JSON array of typical allergic reactions
    severity_levels TEXT, -- JSON array: ["mild", "moderate", "severe", "anaphylaxis"]
    cross_reactions TEXT, -- JSON array of related allergens
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_allergen_category (category),
    INDEX idx_allergen_name (name)
);

-- Symptoms database
CREATE TABLE symptoms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100), -- 'respiratory', 'cardiovascular', 'neurological', etc.
    severity_scale ENUM('1-10', 'mild-severe', 'absent-present'),
    measurement_unit VARCHAR(50), -- 'degrees', 'frequency', 'intensity', etc.
    related_body_systems TEXT, -- JSON array of affected body systems
    common_causes TEXT, -- JSON array of typical causes
    red_flag_indicators TEXT, -- JSON array of warning signs requiring immediate attention
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symptom_category (category),
    INDEX idx_symptom_name (name)
);

-- ============================================================================
-- USER MEDICAL HISTORY TABLES (NORMALIZED)
-- ============================================================================

-- User's chronic diseases (many-to-many relationship)
CREATE TABLE user_chronic_diseases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    disease_id INT NOT NULL,
    diagnosed_date DATE,
    diagnosed_by VARCHAR(200), -- Doctor/Hospital name
    current_status ENUM('active', 'remission', 'cured', 'managed'),
    severity_current ENUM('mild', 'moderate', 'severe'),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (disease_id) REFERENCES disease_categories(id),
    UNIQUE KEY unique_user_disease (user_id, disease_id),
    INDEX idx_user_diseases_user_id (user_id),
    INDEX idx_user_diseases_status (current_status)
);

-- User's medications (many-to-many relationship)
CREATE TABLE user_medications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    medication_id INT NOT NULL,
    dosage VARCHAR(50), -- "500mg twice daily"
    frequency VARCHAR(50), -- "twice daily", "as needed"
    route ENUM('oral', 'injection', 'topical', 'inhaled', 'other'),
    start_date DATE,
    end_date DATE, -- NULL if ongoing
    prescribed_by VARCHAR(200), -- Doctor name
    indication VARCHAR(200), -- What condition this treats
    is_active BOOLEAN DEFAULT TRUE,
    adherence_level ENUM('excellent', 'good', 'fair', 'poor'), -- How well they follow prescription
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (medication_id) REFERENCES medications(id),
    INDEX idx_user_meds_user_id (user_id),
    INDEX idx_user_meds_active (is_active),
    INDEX idx_user_meds_dates (start_date, end_date)
);

-- User's allergies (many-to-many relationship)
CREATE TABLE user_allergies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    allergen_id INT NOT NULL,
    severity ENUM('mild', 'moderate', 'severe', 'anaphylaxis'),
    first_reaction_date DATE,
    last_reaction_date DATE,
    symptoms_experienced TEXT, -- JSON array of symptoms they had
    treatment_required TEXT, -- What treatment was needed
    confirmed_by_test BOOLEAN DEFAULT FALSE,
    test_type VARCHAR(100), -- "skin test", "blood test", "challenge test"
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (allergen_id) REFERENCES allergen_categories(id),
    UNIQUE KEY unique_user_allergen (user_id, allergen_id),
    INDEX idx_user_allergies_user_id (user_id),
    INDEX idx_user_allergies_severity (severity)
);

-- User's family medical history
CREATE TABLE user_family_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    relationship ENUM('mother', 'father', 'sibling', 'grandparent', 'aunt_uncle', 'cousin', 'other'),
    disease_id INT NOT NULL,
    age_of_onset INT, -- Age when the relative developed the condition
    is_deceased BOOLEAN DEFAULT FALSE,
    cause_of_death INT, -- disease_id if died from medical condition
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (disease_id) REFERENCES disease_categories(id),
    FOREIGN KEY (cause_of_death) REFERENCES disease_categories(id),
    INDEX idx_family_history_user_id (user_id),
    INDEX idx_family_history_relationship (relationship)
);

-- ============================================================================
-- LIFESTYLE AND BEHAVIORAL DATA
-- ============================================================================

-- User lifestyle factors
CREATE TABLE user_lifestyle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    
    -- Smoking
    smoking_status ENUM('never', 'former', 'current') NOT NULL,
    smoking_start_age INT,
    smoking_quit_age INT,
    cigarettes_per_day INT,
    years_smoked INT,
    
    -- Alcohol
    alcohol_frequency ENUM('never', 'rarely', 'weekly', 'daily'),
    alcohol_units_per_week DECIMAL(4,1), -- Standard alcohol units
    alcohol_type_preference TEXT, -- JSON: ["beer", "wine", "spirits"]
    
    -- Physical Activity
    exercise_frequency ENUM('none', 'rare', 'weekly', 'daily'),
    exercise_intensity ENUM('light', 'moderate', 'vigorous'),
    exercise_duration_minutes INT, -- Average minutes per session
    exercise_types TEXT, -- JSON array: ["walking", "running", "gym"]
    
    -- Diet
    diet_type ENUM('omnivore', 'vegetarian', 'vegan', 'keto', 'paleo', 'other'),
    meals_per_day INT DEFAULT 3,
    water_intake_liters DECIMAL(3,1),
    
    -- Sleep
    sleep_hours_average DECIMAL(3,1),
    sleep_quality ENUM('poor', 'fair', 'good', 'excellent'),
    sleep_disorders TEXT, -- JSON array: ["insomnia", "sleep_apnea"]
    
    -- Stress and Mental Health
    stress_level ENUM('low', 'moderate', 'high', 'severe'),
    mental_health_status ENUM('excellent', 'good', 'fair', 'poor'),
    
    -- Occupational Hazards
    work_environment ENUM('office', 'outdoor', 'industrial', 'medical', 'other'),
    chemical_exposure BOOLEAN DEFAULT FALSE,
    physical_demands ENUM('sedentary', 'light', 'moderate', 'heavy'),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_lifestyle_user_id (user_id),
    INDEX idx_lifestyle_smoking (smoking_status),
    INDEX idx_lifestyle_exercise (exercise_frequency)
);

-- ============================================================================
-- MEDICAL ENCOUNTERS AND DIAGNOSES
-- ============================================================================

-- User's symptom reports
CREATE TABLE user_symptom_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36), -- Groups symptoms reported in one conversation
    symptom_id INT NOT NULL,
    severity INT, -- 1-10 scale or categorical
    duration_hours INT, -- How long they've had this symptom
    frequency ENUM('constant', 'intermittent', 'occasional'),
    triggers TEXT, -- JSON array of what makes it worse/better
    associated_symptoms TEXT, -- JSON array of other symptoms happening together
    location_body_part VARCHAR(100), -- Where on the body
    quality_description TEXT, -- "sharp", "dull", "burning", etc.
    onset_type ENUM('sudden', 'gradual'),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (symptom_id) REFERENCES symptoms(id),
    INDEX idx_symptom_reports_user_id (user_id),
    INDEX idx_symptom_reports_session (session_id),
    INDEX idx_symptom_reports_date (reported_at)
);

-- AI diagnosis results
CREATE TABLE ai_diagnoses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36) NOT NULL, -- Links to symptom report session
    
    -- Primary diagnosis
    primary_diagnosis_id INT, -- Most likely condition
    primary_confidence DECIMAL(5,2), -- 0-100% confidence
    
    -- Differential diagnoses
    differential_diagnoses TEXT, -- JSON array of {disease_id, confidence, reasoning}
    
    -- Risk factors considered
    risk_factors_applied TEXT, -- JSON array of user-specific risk factors used
    
    -- Recommendations
    urgency_level ENUM('emergency', 'urgent', 'routine', 'self_care'),
    recommended_actions TEXT, -- JSON array of next steps
    specialist_referral_needed BOOLEAN DEFAULT FALSE,
    recommended_specialty_id INT,
    
    -- AI model information
    ai_model_version VARCHAR(50),
    processing_time_ms INT,
    
    -- Follow-up
    follow_up_needed BOOLEAN DEFAULT FALSE,
    follow_up_timeframe VARCHAR(50), -- "24 hours", "1 week", etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (primary_diagnosis_id) REFERENCES disease_categories(id),
    FOREIGN KEY (recommended_specialty_id) REFERENCES medical_specialties(id),
    INDEX idx_diagnoses_user_id (user_id),
    INDEX idx_diagnoses_session (session_id),
    INDEX idx_diagnoses_urgency (urgency_level),
    INDEX idx_diagnoses_date (created_at)
);

-- ============================================================================
-- CHAT AND INTERACTION HISTORY
-- ============================================================================

-- Enhanced chat history
CREATE TABLE chat_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_type ENUM('symptom_check', 'follow_up', 'general_question', 'medication_query'),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,
    total_messages INT DEFAULT 0,
    satisfaction_rating INT, -- 1-5 stars if user provides feedback
    was_helpful BOOLEAN,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_chat_sessions_user_id (user_id),
    INDEX idx_chat_sessions_type (session_type),
    INDEX idx_chat_sessions_date (started_at)
);

-- Individual messages within sessions
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    message_order INT NOT NULL, -- Order within the session
    sender ENUM('user', 'ai') NOT NULL,
    message_text TEXT NOT NULL,
    message_type ENUM('text', 'symptom_data', 'diagnosis_result', 'recommendation'),
    
    -- For AI messages
    ai_confidence DECIMAL(5,2), -- How confident AI was in this response
    processing_time_ms INT,
    
    -- For user messages
    sentiment_score DECIMAL(3,2), -- -1 to 1, emotional tone analysis
    contains_urgency_keywords BOOLEAN DEFAULT FALSE,
    
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    INDEX idx_chat_messages_session (session_id),
    INDEX idx_chat_messages_order (session_id, message_order),
    INDEX idx_chat_messages_sender (sender)
);

-- ============================================================================
-- NEWS AND EDUCATIONAL CONTENT
-- ============================================================================

-- Enhanced news articles
CREATE TABLE news_articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content LONGTEXT,
    url VARCHAR(1000),
    image_url VARCHAR(1000),
    
    -- Categorization
    primary_category_id INT, -- Links to medical specialties
    target_audience ENUM('general_public', 'patients', 'professionals'),
    reading_level ENUM('basic', 'intermediate', 'advanced'),
    
    -- Source information
    source_name VARCHAR(100) DEFAULT 'suckhoedoisong.vn',
    author VARCHAR(200),
    publication_date TIMESTAMP,
    last_updated TIMESTAMP,
    
    -- Content analysis
    related_diseases TEXT, -- JSON array of disease_ids mentioned
    related_symptoms TEXT, -- JSON array of symptom_ids mentioned
    fact_checked BOOLEAN DEFAULT FALSE,
    medical_accuracy_score DECIMAL(3,2), -- 0-1 score
    
    -- Engagement metrics
    view_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    bookmark_count INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_category_id) REFERENCES medical_specialties(id),
    INDEX idx_news_category (primary_category_id),
    INDEX idx_news_publication_date (publication_date),
    INDEX idx_news_audience (target_audience)
);

-- User interactions with news articles
CREATE TABLE user_news_interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    article_id INT NOT NULL,
    interaction_type ENUM('view', 'bookmark', 'share', 'like', 'report'),
    reading_time_seconds INT, -- How long they spent reading
    interaction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES news_articles(id) ON DELETE CASCADE,
    INDEX idx_news_interactions_user (user_id),
    INDEX idx_news_interactions_article (article_id),
    INDEX idx_news_interactions_type (interaction_type)
);

-- ============================================================================
-- ANALYTICS AND MACHINE LEARNING TABLES
-- ============================================================================

-- User behavior analytics
CREATE TABLE user_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_date DATE NOT NULL,
    
    -- Usage patterns
    total_sessions INT DEFAULT 0,
    total_time_minutes INT DEFAULT 0,
    features_used TEXT, -- JSON array of features accessed
    
    -- Health engagement
    symptoms_reported INT DEFAULT 0,
    diagnoses_received INT DEFAULT 0,
    articles_read INT DEFAULT 0,
    recommendations_followed INT DEFAULT 0,
    
    -- AI interaction quality
    average_satisfaction DECIMAL(3,2),
    helpful_responses INT DEFAULT 0,
    total_responses INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, session_date),
    INDEX idx_analytics_user_id (user_id),
    INDEX idx_analytics_date (session_date)
);

-- Machine learning model performance tracking
CREATE TABLE ml_model_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    
    -- Performance metrics
    accuracy_rate DECIMAL(5,2),
    precision_score DECIMAL(5,2),
    recall_score DECIMAL(5,2),
    f1_score DECIMAL(5,2),
    
    -- Usage statistics
    total_predictions INT DEFAULT 0,
    correct_predictions INT DEFAULT 0,
    false_positives INT DEFAULT 0,
    false_negatives INT DEFAULT 0,
    
    -- Performance by category
    performance_by_specialty TEXT, -- JSON object with specialty-specific metrics
    performance_by_severity TEXT, -- JSON object with severity-specific metrics
    
    evaluation_date DATE NOT NULL,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ml_performance_model (model_name, model_version),
    INDEX idx_ml_performance_date (evaluation_date)
);

-- ============================================================================
-- REFERENCE DATA INSERTION
-- ============================================================================

-- Insert medical specialties
INSERT INTO medical_specialties (name, description) VALUES 
('Nội khoa', 'Chuyên khoa điều trị các bệnh nội tạng'),
('Ngoại khoa', 'Chuyên khoa phẫu thuật'),
('Sản phụ khoa', 'Chuyên khoa sản khoa và phụ khoa'),
('Nhi khoa', 'Chuyên khoa điều trị trẻ em'),
('Tim mạch', 'Chuyên khoa tim mạch'),
('Thần kinh', 'Chuyên khoa thần kinh'),
('Tâm thần', 'Chuyên khoa tâm thần'),
('Da liễu', 'Chuyên khoa da liễu'),
('Mắt', 'Chuyên khoa mắt'),
('Tai mũi họng', 'Chuyên khoa tai mũi họng'),
('Cơ xương khớp', 'Chuyên khoa cơ xương khớp'),
('Tiết niệu', 'Chuyên khoa tiết niệu'),
('Nội tiết', 'Chuyên khoa nội tiết'),
('Hô hấp', 'Chuyên khoa hô hấp'),
('Tiêu hóa', 'Chuyên khoa tiêu hóa');

-- Insert Vietnamese provinces with additional data
INSERT INTO provinces (name, code, region, climate) VALUES 
('Hà Nội', 'HN', 'north', 'subtropical'),
('Hồ Chí Minh', 'HCM', 'south', 'tropical'),
('Đà Nẵng', 'DN', 'central', 'tropical'),
('Hải Phòng', 'HP', 'north', 'subtropical'),
('Cần Thơ', 'CT', 'south', 'tropical'),
('An Giang', 'AG', 'south', 'tropical'),
('Bà Rịa - Vũng Tàu', 'BR', 'south', 'tropical'),
('Bạc Liêu', 'BL', 'south', 'tropical'),
('Bắc Giang', 'BG', 'north', 'subtropical'),
('Bắc Kạn', 'BK', 'north', 'temperate'),
('Bắc Ninh', 'BN', 'north', 'subtropical'),
('Bến Tre', 'BT', 'south', 'tropical'),
('Bình Dương', 'BD', 'south', 'tropical'),
('Bình Định', 'BĐ', 'central', 'tropical'),
('Bình Phước', 'BP', 'south', 'tropical'),
('Bình Thuận', 'BTh', 'central', 'tropical'),
('Cà Mau', 'CM', 'south', 'tropical'),
('Cao Bằng', 'CB', 'north', 'temperate'),
('Đắk Lắk', 'ĐL', 'central', 'tropical'),
('Đắk Nông', 'ĐN', 'central', 'tropical'),
('Điện Biên', 'ĐB', 'north', 'temperate'),
('Đồng Nai', 'ĐNa', 'south', 'tropical'),
('Đồng Tháp', 'ĐT', 'south', 'tropical'),
('Gia Lai', 'GL', 'central', 'tropical'),
('Hà Giang', 'HG', 'north', 'temperate'),
('Hà Nam', 'HNa', 'north', 'subtropical'),
('Hà Tĩnh', 'HT', 'central', 'tropical'),
('Hải Dương', 'HĐ', 'north', 'subtropical'),
('Hậu Giang', 'HGi', 'south', 'tropical'),
('Hòa Bình', 'HB', 'north', 'temperate'),
('Hưng Yên', 'HY', 'north', 'subtropical'),
('Khánh Hòa', 'KH', 'central', 'tropical'),
('Kiên Giang', 'KG', 'south', 'tropical'),
('Kon Tum', 'KT', 'central', 'tropical'),
('Lai Châu', 'LC', 'north', 'temperate'),
('Lạng Sơn', 'LS', 'north', 'subtropical'),
('Lào Cai', 'LCa', 'north', 'temperate'),
('Lâm Đồng', 'LĐ', 'central', 'temperate'),
('Long An', 'LA', 'south', 'tropical'),
('Nam Định', 'NĐ', 'north', 'subtropical'),
('Nghệ An', 'NA', 'central', 'tropical'),
('Ninh Bình', 'NB', 'north', 'subtropical'),
('Ninh Thuận', 'NT', 'central', 'tropical'),
('Phú Thọ', 'PT', 'north', 'subtropical'),
('Phú Yên', 'PY', 'central', 'tropical'),
('Quảng Bình', 'QB', 'central', 'tropical'),
('Quảng Nam', 'QN', 'central', 'tropical'),
('Quảng Ngãi', 'QNg', 'central', 'tropical'),
('Quảng Ninh', 'QNi', 'north', 'subtropical'),
('Quảng Trị', 'QT', 'central', 'tropical'),
('Sóc Trăng', 'ST', 'south', 'tropical'),
('Sơn La', 'SL', 'north', 'temperate'),
('Tây Ninh', 'TN', 'south', 'tropical'),
('Thái Bình', 'TB', 'north', 'subtropical'),
('Thái Nguyên', 'TNg', 'north', 'subtropical'),
('Thanh Hóa', 'TH', 'central', 'tropical'),
('Thừa Thiên Huế', 'TTH', 'central', 'tropical'),
('Tiền Giang', 'TG', 'south', 'tropical'),
('Trà Vinh', 'TV', 'south', 'tropical'),
('Tuyên Quang', 'TQ', 'north', 'temperate'),
('Vĩnh Long', 'VL', 'south', 'tropical'),
('Vĩnh Phúc', 'VP', 'north', 'subtropical'),
('Yên Bái', 'YB', 'north', 'temperate');

-- Add foreign key constraint for demographics
ALTER TABLE user_demographics ADD FOREIGN KEY (province_id) REFERENCES provinces(id);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Composite indexes for complex queries
CREATE INDEX idx_user_chronic_diseases_composite ON user_chronic_diseases(user_id, current_status, severity_current);
CREATE INDEX idx_user_medications_composite ON user_medications(user_id, is_active, start_date);
CREATE INDEX idx_symptom_reports_composite ON user_symptom_reports(user_id, session_id, reported_at);
CREATE INDEX idx_ai_diagnoses_composite ON ai_diagnoses(user_id, urgency_level, created_at);
CREATE INDEX idx_chat_messages_composite ON chat_messages(session_id, message_order, sender);

-- Full-text search indexes
ALTER TABLE disease_categories ADD FULLTEXT(name, description);
ALTER TABLE medications ADD FULLTEXT(name, generic_name);
ALTER TABLE symptoms ADD FULLTEXT(name, category);
ALTER TABLE news_articles ADD FULLTEXT(title, summary, content);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- User health profile view
CREATE VIEW user_health_profiles AS
SELECT 
    u.id as user_id,
    u.email,
    u.name,
    ud.birth_year,
    ud.gender,
    ud.height_cm,
    ud.weight_kg,
    ud.blood_type,
    p.name as province_name,
    p.region,
    ul.smoking_status,
    ul.alcohol_frequency,
    ul.exercise_frequency,
    COUNT(DISTINCT ucd.disease_id) as chronic_disease_count,
    COUNT(DISTINCT um.medication_id) as active_medication_count,
    COUNT(DISTINCT ua.allergen_id) as allergy_count
FROM users u
LEFT JOIN user_demographics ud ON u.id = ud.user_id
LEFT JOIN provinces p ON ud.province_id = p.id
LEFT JOIN user_lifestyle ul ON u.id = ul.user_id
LEFT JOIN user_chronic_diseases ucd ON u.id = ucd.user_id AND ucd.current_status = 'active'
LEFT JOIN user_medications um ON u.id = um.user_id AND um.is_active = TRUE
LEFT JOIN user_allergies ua ON u.id = ua.user_id AND ua.is_active = TRUE
GROUP BY u.id;

-- Recent diagnosis summary view
CREATE VIEW recent_diagnoses_summary AS
SELECT 
    ad.user_id,
    ad.session_id,
    dc.name as primary_diagnosis,
    ad.primary_confidence,
    ad.urgency_level,
    ad.created_at,
    COUNT(usr.symptom_id) as symptoms_count
FROM ai_diagnoses ad
JOIN disease_categories dc ON ad.primary_diagnosis_id = dc.id
LEFT JOIN user_symptom_reports usr ON ad.session_id = usr.session_id
WHERE ad.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY ad.id
ORDER BY ad.created_at DESC;
