-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th9 30, 2025 lúc 11:36 AM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `dia5_medical_ai`
--

DELIMITER $$
--
-- Thủ tục
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_distributor_receive_shipment` (IN `p_shipment_id` BIGINT, IN `p_distributor_id` BIGINT)   BEGIN
    DECLARE v_batch_id BIGINT;
    DECLARE v_quantity INT;
    DECLARE v_from_company_id BIGINT;
    DECLARE v_exists INT;
    
    -- Get shipment details
    SELECT batch_id, quantity, from_company_id
    INTO v_batch_id, v_quantity, v_from_company_id
    FROM drug_shipments
    WHERE id = p_shipment_id AND to_company_id = p_distributor_id;
    
    -- Check if inventory record exists
    SELECT COUNT(*) INTO v_exists
    FROM distributor_inventory
    WHERE distributor_id = p_distributor_id AND batch_id = v_batch_id;
    
    IF v_exists > 0 THEN
        -- Update existing record
        UPDATE distributor_inventory
        SET quantity = quantity + v_quantity,
            received_shipment_id = p_shipment_id,
            received_date = NOW(),
            updated_at = NOW()
        WHERE distributor_id = p_distributor_id AND batch_id = v_batch_id;
    ELSE
        -- Insert new record
        INSERT INTO distributor_inventory (
            distributor_id, batch_id, drug_name, manufacturer, batch_number,
            quantity, manufacture_date, expiry_date, qr_code,
            received_from_company_id, received_shipment_id, received_date, received_quantity
        )
        SELECT 
            p_distributor_id, db.id, db.drug_name, db.manufacturer, db.batch_number,
            v_quantity, db.manufacture_timestamp, db.expiry_date, db.qr_code,
            v_from_company_id, p_shipment_id, NOW(), v_quantity
        FROM drug_batches db
        WHERE db.id = v_batch_id;
    END IF;
    
    -- Update shipment status
    UPDATE drug_shipments
    SET shipment_status = 'DELIVERED',
        actual_delivery_date = NOW()
    WHERE id = p_shipment_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_pharmacy_receive_shipment` (IN `p_shipment_id` BIGINT, IN `p_pharmacy_id` BIGINT)   BEGIN
    DECLARE v_batch_id BIGINT;
    DECLARE v_quantity INT;
    DECLARE v_from_company_id BIGINT;
    DECLARE v_exists INT;
    
    -- Get shipment details
    SELECT batch_id, quantity, from_company_id
    INTO v_batch_id, v_quantity, v_from_company_id
    FROM drug_shipments
    WHERE id = p_shipment_id AND to_company_id = p_pharmacy_id;
    
    -- Check if inventory record exists
    SELECT COUNT(*) INTO v_exists
    FROM pharmacy_inventory
    WHERE pharmacy_id = p_pharmacy_id AND batch_id = v_batch_id;
    
    IF v_exists > 0 THEN
        -- Update existing record
        UPDATE pharmacy_inventory
        SET quantity = quantity + v_quantity,
            received_shipment_id = p_shipment_id,
            received_date = NOW(),
            updated_at = NOW()
        WHERE pharmacy_id = p_pharmacy_id AND batch_id = v_batch_id;
    ELSE
        -- Insert new record
        INSERT INTO pharmacy_inventory (
            pharmacy_id, batch_id, drug_name, manufacturer, batch_number,
            quantity, manufacture_date, expiry_date, qr_code,
            received_from_distributor_id, received_shipment_id, received_date, received_quantity
        )
        SELECT 
            p_pharmacy_id, db.id, db.drug_name, db.manufacturer, db.batch_number,
            v_quantity, db.manufacture_timestamp, db.expiry_date, db.qr_code,
            v_from_company_id, p_shipment_id, NOW(), v_quantity
        FROM drug_batches db
        WHERE db.id = v_batch_id;
    END IF;
    
    -- Update shipment status
    UPDATE drug_shipments
    SET shipment_status = 'DELIVERED',
        actual_delivery_date = NOW()
    WHERE id = p_shipment_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `VerifyDrugByQR` (IN `qr_code_input` VARCHAR(1000))   BEGIN
    DECLARE batch_count INT DEFAULT 0;
    DECLARE is_expired BOOLEAN DEFAULT FALSE;
    DECLARE batch_status VARCHAR(50);
    DECLARE expiry_date_val TIMESTAMP;
    DECLARE batch_id_val BIGINT;
    
    -- Check if batch exists
    SELECT COUNT(*), status, expiry_date, id
    INTO batch_count, batch_status, expiry_date_val, batch_id_val
    FROM drug_batches 
    WHERE qr_code = qr_code_input
    LIMIT 1;
    
    -- Check if expired
    IF expiry_date_val < NOW() THEN
        SET is_expired = TRUE;
    END IF;
    
    -- Return verification result with batch details
    IF batch_count > 0 THEN
        SELECT 
            db.*,
            CASE 
                WHEN is_expired THEN 'EXPIRED'
                WHEN batch_status = 'SOLD' THEN 'ALREADY_SOLD'
                ELSE 'VALID'
            END as verification_status,
            is_expired,
            (SELECT COUNT(*) FROM drug_shipments WHERE batch_id = batch_id_val) as shipment_count
        FROM drug_batches db 
        WHERE db.id = batch_id_val;
    ELSE
        SELECT 
            qr_code_input as qr_code,
            'INVALID' as verification_status,
            FALSE as batch_exists,
            NULL as drug_name,
            NULL as manufacturer;
    END IF;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `ai_diagnoses`
--

CREATE TABLE `ai_diagnoses` (
  `id` int(11) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `session_id` varchar(36) NOT NULL,
  `primary_diagnosis_id` int(11) DEFAULT NULL,
  `primary_confidence` decimal(5,2) DEFAULT NULL,
  `differential_diagnoses` text DEFAULT NULL,
  `risk_factors_applied` text DEFAULT NULL,
  `urgency_level` enum('emergency','urgent','routine','self_care') DEFAULT NULL,
  `recommended_actions` text DEFAULT NULL,
  `specialist_referral_needed` tinyint(1) DEFAULT 0,
  `recommended_specialty_id` int(11) DEFAULT NULL,
  `ai_model_version` varchar(50) DEFAULT NULL,
  `processing_time_ms` int(11) DEFAULT NULL,
  `follow_up_needed` tinyint(1) DEFAULT 0,
  `follow_up_timeframe` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `allergen_categories`
--

CREATE TABLE `allergen_categories` (
  `id` int(11) NOT NULL,
  `category` varchar(50) NOT NULL,
  `name` varchar(200) NOT NULL,
  `common_symptoms` text DEFAULT NULL,
  `severity_levels` text DEFAULT NULL,
  `cross_reactions` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `blockchain_config`
--

CREATE TABLE `blockchain_config` (
  `id` int(11) NOT NULL,
  `config_key` varchar(100) NOT NULL,
  `config_value` text NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `updated_by` varchar(36) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `blockchain_config`
--

INSERT INTO `blockchain_config` (`id`, `config_key`, `config_value`, `description`, `is_active`, `updated_by`, `created_at`, `updated_at`) VALUES
(1, 'contract_address', '0x5FbDB2315678afecb367f032d93F642f64180aa3', 'PharmaLedger smart contract address', 1, NULL, '2025-09-18 15:38:49', '2025-09-18 15:38:49'),
(2, 'network_url', 'http://localhost:8545', 'Blockchain network RPC URL', 1, NULL, '2025-09-18 15:38:49', '2025-09-18 15:38:49'),
(3, 'chain_id', '1337', 'Blockchain network chain ID', 1, NULL, '2025-09-18 15:38:49', '2025-09-18 15:38:49'),
(4, 'last_synced_block', '0', 'Last synced block number for event indexing', 1, NULL, '2025-09-18 15:38:49', '2025-09-18 15:38:49'),
(5, 'indexer_enabled', 'true', 'Enable/disable blockchain event indexing', 1, NULL, '2025-09-18 15:38:49', '2025-09-18 15:38:49'),
(6, 'gas_price', '20000000000', 'Default gas price in wei', 1, NULL, '2025-09-18 15:38:49', '2025-09-18 15:38:49'),
(7, 'gas_limit', '6721975', 'Default gas limit for transactions', 1, NULL, '2025-09-18 15:38:49', '2025-09-18 15:38:49');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `blockchain_events`
--

CREATE TABLE `blockchain_events` (
  `id` bigint(20) NOT NULL,
  `batch_id` decimal(38,0) DEFAULT NULL,
  `block_number` decimal(38,0) NOT NULL,
  `contract_address` varchar(255) NOT NULL,
  `event_data` text DEFAULT NULL,
  `event_type` varchar(255) NOT NULL,
  `from_address` varchar(255) DEFAULT NULL,
  `indexed_at` datetime(6) NOT NULL,
  `log_index` decimal(38,0) NOT NULL,
  `processed` bit(1) NOT NULL,
  `shipment_id` decimal(38,0) DEFAULT NULL,
  `to_address` varchar(255) DEFAULT NULL,
  `transaction_hash` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `blockchain_transactions`
--

CREATE TABLE `blockchain_transactions` (
  `id` bigint(20) NOT NULL,
  `block_number` decimal(38,0) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `error_message` varchar(1000) DEFAULT NULL,
  `event_logs` tinytext DEFAULT NULL,
  `from_address` varchar(42) NOT NULL,
  `function_name` varchar(100) NOT NULL,
  `gas_price` decimal(38,0) DEFAULT NULL,
  `gas_used` decimal(38,0) DEFAULT NULL,
  `input_data` tinytext DEFAULT NULL,
  `status` enum('FAILED','PENDING','REVERTED','SUCCESS') NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `to_address` varchar(42) NOT NULL,
  `transaction_hash` varchar(66) NOT NULL,
  `batch_id` bigint(20) DEFAULT NULL,
  `shipment_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `chat_messages`
--

CREATE TABLE `chat_messages` (
  `id` int(11) NOT NULL,
  `session_id` varchar(36) NOT NULL,
  `message_order` int(11) NOT NULL,
  `sender` enum('user','ai') NOT NULL,
  `message_text` text NOT NULL,
  `message_type` enum('text','symptom_data','diagnosis_result','recommendation') DEFAULT NULL,
  `ai_confidence` decimal(5,2) DEFAULT NULL,
  `processing_time_ms` int(11) DEFAULT NULL,
  `sentiment_score` decimal(3,2) DEFAULT NULL,
  `contains_urgency_keywords` tinyint(1) DEFAULT 0,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `sources_json` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `chat_messages`
--

INSERT INTO `chat_messages` (`id`, `session_id`, `message_order`, `sender`, `message_text`, `message_type`, `ai_confidence`, `processing_time_ms`, `sentiment_score`, `contains_urgency_keywords`, `timestamp`, `sources_json`) VALUES
(1, '11b2cfdd-b75f-4289-8843-bf797591b8ca', 1, 'user', 'Tôi bị đau đầu và chóng mặt, có thể là bệnh gì?', 'text', NULL, NULL, NULL, 0, '2025-09-09 20:36:36', NULL),
(2, '98b60c6b-8f77-4462-883a-7636279ba350', 1, 'user', 'Tôi bị đau đầu và chóng mặt, có thể là bệnh gì?', 'text', NULL, NULL, NULL, 0, '2025-09-09 20:38:48', NULL),
(3, 'ec9b72f3-02dc-4efa-9146-6aa08366251e', 1, 'user', 'Tôi bị đau đầu và chóng mặt, có thể là bệnh gì?', 'text', NULL, NULL, NULL, 0, '2025-09-09 20:42:31', NULL),
(4, 'ec9b72f3-02dc-4efa-9146-6aa08366251e', 2, 'ai', 'Chào bạn! 😊 Cảm ơn bạn đã chia sẻ thông tin về tình trạng sức khỏe của mình. Đau đầu và chóng mặt là hai triệu chứng phổ biến nhưng có thể liên quan đến nhiều nguyên nhân khác nhau. Dưới đây là một số khả năng có thể xảy ra dựa trên mô tả của bạn:\n\n### 🔍 Nguyên nhân có thể:\n1. **Đau đầu căng thẳng (Tension-type headache - Mã ICD: 8A81)**: Thường gặp do căng thẳng, mệt mỏi, hoặc tư thế không thoải mái. Đau thường âm ỉ ở hai bên đầu và có thể kèm theo chóng mặt nhẹ.\n2. **Đau đầu cấp tính không phân loại khác (Acute headache, not elsewhere classified - Mã ICD: MG31.1)**: Có thể xuất hiện đột ngột và không rõ nguyên nhân cụ thể.\n3. **Nguyên nhân thứ phát khác (Other specified secondary headache - Mã ICD: 8A84.Y)**: Ví dụ như đau đầu sau chấn thương đầu/cổ hoặc liên quan đến các vấn đề y tế khác (như viêm xoang, huyết áp, thiếu máu...).\n\n### 💡 Thông tin cần thêm:\nĐể hiểu rõ hơn về tình trạng của bạn, tôi cần biết thêm một số chi tiết:\n- Bạn bị đau đầu và chóng mặt bao lâu rồi? 🕒\n- Mức độ đau như thế nào (nhẹ, trung bình hay dữ dội)? \n- Có triệu chứng khác kèm theo không (buồn nôn, nhạy cảm với ánh sáng/tiếng động, mất thăng bằng)? \n\n### 🩺 Khuyến nghị:\nVì đau đầu và chóng mặt có thể liên quan đến nhiều vấn đề sức khỏe (từ nhẹ đến nghiêm trọng), bạn nên:\n- **Đến gặp bác sĩ** để được thăm khám trực tiếp, chẩn đoán chính xác và loại trừ các nguyên nhân tiềm ẩn.\n- **Theo dõi triệu chứng** và ghi lại các yếu tố khởi phát (nếu có) để hỗ trợ bác sĩ trong quá trình chẩn đoán.\n\nHy vọng bạn sớm cảm thấy khỏe hơn! 🌸 Hãy luôn ưu tiên sức khỏe của mình nhé!', 'text', 0.95, 34, NULL, 0, '2025-09-09 20:42:31', '[{\"title\":\"Acute headache, not elsewhere classified\",\"url\":\"https://icd.who.int/browse/2025-01/mms/en#1068555332\",\"content\":\"\",\"confidence\":0.6001658421065811},{\"title\":\"Tension-type headache\",\"url\":\"https://icd.who.int/browse/2025-01/mms/en#1410019257\",\"content\":\"\",\"confidence\":0.5996614960334102},{\"title\":\"Other specified secondary headache\",\"url\":\"https://icd.who.int/browse/2025-01/mms/en#296971178/other\",\"content\":\"\",\"confidence\":0.5991367285477387},{\"title\":\"Headache disorders\",\"url\":\"https://icd.who.int/browse/2025-01/mms/en#28995849\",\"content\":\"\",\"confidence\":0.5923248371101191},{\"title\":\"Headache, not elsewhere classified\",\"url\":\"https://icd.who.int/browse/2025-01/mms/en#1405405864\",\"content\":\"\",\"confidence\":0.5865008381397036}]'),
(5, 'ec9b72f3-02dc-4efa-9146-6aa08366251e', 3, 'user', 'Tôi đau đầu 2 tiếng rồi', 'text', NULL, NULL, NULL, 0, '2025-09-09 20:44:50', NULL),
(6, 'ec9b72f3-02dc-4efa-9146-6aa08366251e', 4, 'ai', 'Chào bạn! 😊\n\nCảm ơn bạn đã chia sẻ thêm triệu chứng đau đầu kéo dài 2 tiếng. Khi kết hợp với các triệu chứng đã đề cập trước đó như buồn nôn, chóng mặt và mệt mỏi, tình trạng này cần được quan tâm đúng mức.\n\nDựa trên thông tin bạn cung cấp, đau đầu của bạn có thể liên quan đến nhiều khả năng khác nhau, ví dụ như:\n- **Căng thẳng hoặc mệt mỏi** kéo dài\n- **Thiếu nước** hoặc hạ đường huyết\n- **Rối loạn tiền đình** (kèm theo chóng mặt)\n- **Đau đầu căng thẳng** hoặc **chứng đau nửa đầu** (kèm theo buồn nôn)\n\nTuy nhiên, đây chỉ là những khả năng mang tính tham khảo. Để xác định rõ nguyên nhân, tôi khuyên bạn:\n\n1️⃣ **Theo dõi thêm các triệu chứng đi kèm**: Bạn có bị nhạy cảm với ánh sáng/tiếng động không? Cơn đau đầu có dữ dội hơn khi vận động không?\n\n2️⃣ **Nghỉ ngơi ngay** ở nơi yên tĩnh, tránh ánh sáng mạnh và uống đủ nước.\n\n3️⃣ **Đến cơ sở y tế gần nhất** để được bác sĩ thăm khám trực tiếp nếu cơn đau đầu:\n- Tiếp tục kéo dài hoặc tăng nặng\n- Đi kèm nôn ói nhiều, cứng cổ hoặc rối loạn thị giác\n\nViệc thăm khám sớm sẽ giúp loại trừ các nguyên nhân nghiêm trọng và có hướng xử trí phù hợp. Bạn nhớ giữ bình tĩnh và đừng chủ quan nhé! 💪\n\nHy vọng bạn sớm cải thiện sức khỏe!', 'text', 0.85, 29, NULL, 0, '2025-09-09 20:44:50', '[{\"title\":\"Otalgia\",\"url\":\"https://icd.who.int/browse/2025-01/mms/en#962492793\",\"content\":\"\",\"confidence\":0.6120218706813014},{\"title\":\"Headache, not elsewhere classified\",\"url\":\"https://icd.who.int/browse/2025-01/mms/en#1405405864\",\"content\":\"\",\"confidence\":0.6089169304927932},{\"title\":\"Headache disorders\",\"url\":\"https://icd.who.int/browse/2025-01/mms/en#28995849\",\"content\":\"\",\"confidence\":0.6057844466367355},{\"title\":\"Secondary headache, unspecified\",\"url\":\"https://icd.who.int/browse/2025-01/mms/en#296971178/unspecified\",\"content\":\"\",\"confidence\":0.6039447013075269},{\"title\":\"Secondary headache\",\"url\":\"https://icd.who.int/browse/2025-01/mms/en#296971178\",\"content\":\"\",\"confidence\":0.5977259771101366}]'),
(7, 'cf38e0d6-7537-4457-897d-8a56f29fe66a', 1, 'user', 'hi', 'text', NULL, NULL, NULL, 0, '2025-09-12 23:38:08', NULL);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `chat_sessions`
--

CREATE TABLE `chat_sessions` (
  `id` varchar(36) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `session_type` enum('symptom_check','follow_up','general_question','medication_query') DEFAULT NULL,
  `started_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `ended_at` timestamp NULL DEFAULT NULL,
  `total_messages` int(11) DEFAULT 0,
  `satisfaction_rating` int(11) DEFAULT NULL,
  `was_helpful` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `chat_sessions`
--

INSERT INTO `chat_sessions` (`id`, `user_id`, `session_type`, `started_at`, `ended_at`, `total_messages`, `satisfaction_rating`, `was_helpful`) VALUES
('11b2cfdd-b75f-4289-8843-bf797591b8ca', '076e2d56-8c6e-40f0-b07f-b997442cb66e', 'symptom_check', '2025-09-09 20:29:32', NULL, 1, NULL, NULL),
('98b60c6b-8f77-4462-883a-7636279ba350', 'c95e23bb-7a92-47af-a2b3-48d5e9d8a3f7', 'symptom_check', '2025-09-09 20:38:39', NULL, 1, NULL, NULL),
('cf38e0d6-7537-4457-897d-8a56f29fe66a', '076e2d56-8c6e-40f0-b07f-b997442cb66e', 'symptom_check', '2025-09-12 23:38:02', NULL, 1, NULL, NULL),
('ec9b72f3-02dc-4efa-9146-6aa08366251e', 'c95e23bb-7a92-47af-a2b3-48d5e9d8a3f7', 'symptom_check', '2025-09-09 20:41:17', NULL, 4, NULL, NULL);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `disease_categories`
--

CREATE TABLE `disease_categories` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `icd10_code` varchar(20) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `severity_level` enum('mild','moderate','severe','critical') DEFAULT NULL,
  `is_chronic` tinyint(1) DEFAULT 0,
  `is_hereditary` tinyint(1) DEFAULT 0,
  `is_contagious` tinyint(1) DEFAULT 0,
  `specialty_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `distributor_inventory`
--

CREATE TABLE `distributor_inventory` (
  `id` bigint(20) NOT NULL,
  `distributor_id` bigint(20) NOT NULL COMMENT 'FK to pharma_companies (DISTRIBUTOR)',
  `batch_id` bigint(20) NOT NULL COMMENT 'FK to drug_batches',
  `drug_name` varchar(255) NOT NULL,
  `manufacturer` varchar(255) NOT NULL,
  `batch_number` varchar(100) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 0 COMMENT 'Số lượng hiện có trong kho',
  `reserved_quantity` int(11) NOT NULL DEFAULT 0 COMMENT 'Số lượng đã được đặt trước/đang chờ xuất',
  `available_quantity` int(11) GENERATED ALWAYS AS (`quantity` - `reserved_quantity`) STORED COMMENT 'Số lượng có thể xuất',
  `manufacture_date` timestamp NULL DEFAULT NULL,
  `expiry_date` timestamp NULL DEFAULT NULL,
  `qr_code` varchar(1000) DEFAULT NULL,
  `warehouse_location` varchar(100) DEFAULT 'Kho chính' COMMENT 'Vị trí trong kho: Kho A, Kệ B1, v.v.',
  `storage_conditions` varchar(500) DEFAULT NULL,
  `storage_temperature` varchar(50) DEFAULT NULL COMMENT 'Nhiệt độ bảo quản',
  `unit_price` decimal(15,2) DEFAULT 0.00 COMMENT 'Giá nhập (từ NSX)',
  `selling_price` decimal(15,2) DEFAULT 0.00 COMMENT 'Giá bán (cho hiệu thuốc)',
  `total_value` decimal(15,2) GENERATED ALWAYS AS (`quantity` * `unit_price`) STORED,
  `status` enum('GOOD','LOW_STOCK','EXPIRING_SOON','EXPIRED','QUARANTINE') DEFAULT 'GOOD',
  `min_stock_level` int(11) DEFAULT 100 COMMENT 'Ngưỡng tồn kho tối thiểu',
  `max_stock_level` int(11) DEFAULT 10000 COMMENT 'Ngưỡng tồn kho tối đa',
  `blockchain_batch_id` decimal(38,0) DEFAULT NULL COMMENT 'ID lô trên blockchain',
  `receive_tx_hash` varchar(66) DEFAULT NULL COMMENT 'TX hash khi nhận hàng',
  `current_owner_address` varchar(42) DEFAULT NULL COMMENT 'Địa chỉ ví blockchain',
  `received_from_company_id` bigint(20) DEFAULT NULL COMMENT 'Nhận từ công ty nào (thường là NSX)',
  `received_shipment_id` bigint(20) DEFAULT NULL COMMENT 'FK to drug_shipments',
  `received_date` timestamp NULL DEFAULT NULL,
  `received_quantity` int(11) DEFAULT 0 COMMENT 'Số lượng nhập ban đầu',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by` varchar(36) DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Quản lý kho của nhà phân phối';

--
-- Đang đổ dữ liệu cho bảng `distributor_inventory`
--

INSERT INTO `distributor_inventory` (`id`, `distributor_id`, `batch_id`, `drug_name`, `manufacturer`, `batch_number`, `quantity`, `reserved_quantity`, `manufacture_date`, `expiry_date`, `qr_code`, `warehouse_location`, `storage_conditions`, `storage_temperature`, `unit_price`, `selling_price`, `status`, `min_stock_level`, `max_stock_level`, `blockchain_batch_id`, `receive_tx_hash`, `current_owner_address`, `received_from_company_id`, `received_shipment_id`, `received_date`, `received_quantity`, `created_at`, `updated_at`, `created_by`, `updated_by`, `notes`) VALUES
(1, 3, 1, 'Paracetamol 500mg', 'Công ty Dược phẩm ABC', 'BATCH-2024-001', 500, 0, '2025-09-29 12:00:12', '2027-09-29 12:00:12', 'QR-PARA-001', 'Kho A - Kệ 1', NULL, NULL, 5000.00, 7000.00, 'GOOD', 100, 10000, 17583466080285480, NULL, '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC', 1, NULL, '2025-09-30 01:22:50', 500, '2025-09-30 08:57:05', '2025-09-30 08:57:05', NULL, NULL, NULL);

--
-- Bẫy `distributor_inventory`
--
DELIMITER $$
CREATE TRIGGER `trg_distributor_inventory_movement_log` AFTER UPDATE ON `distributor_inventory` FOR EACH ROW BEGIN
    IF OLD.quantity != NEW.quantity THEN
        INSERT INTO `inventory_movements` (
            `inventory_type`,
            `inventory_id`,
            `movement_type`,
            `quantity_before`,
            `quantity_change`,
            `quantity_after`,
            `reason`,
            `movement_date`
        ) VALUES (
            'DISTRIBUTOR',
            NEW.id,
            CASE 
                WHEN NEW.quantity > OLD.quantity THEN 'RECEIVE'
                WHEN NEW.quantity < OLD.quantity THEN 'SHIP_OUT'
                ELSE 'ADJUSTMENT'
            END,
            OLD.quantity,
            NEW.quantity - OLD.quantity,
            NEW.quantity,
            'Auto-logged by trigger',
            NOW()
        );
    END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `trg_distributor_inventory_status_update` BEFORE UPDATE ON `distributor_inventory` FOR EACH ROW BEGIN
    DECLARE days_to_expiry INT;
    SET days_to_expiry = DATEDIFF(NEW.expiry_date, NOW());
    
    -- Kiểm tra hết hạn
    IF days_to_expiry < 0 THEN
        SET NEW.status = 'EXPIRED';
    -- Sắp hết hạn (30 ngày)
    ELSEIF days_to_expiry <= 30 THEN
        SET NEW.status = 'EXPIRING_SOON';
    -- Tồn kho thấp
    ELSEIF NEW.available_quantity <= NEW.min_stock_level THEN
        SET NEW.status = 'LOW_STOCK';
    ELSE
        SET NEW.status = 'GOOD';
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `distributor_users`
--

CREATE TABLE `distributor_users` (
  `id` varchar(36) NOT NULL,
  `company_address` varchar(500) DEFAULT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `email` varchar(255) NOT NULL,
  `is_active` bit(1) NOT NULL,
  `is_profile_complete` bit(1) NOT NULL,
  `is_verified` bit(1) NOT NULL,
  `last_login_at` datetime(6) DEFAULT NULL,
  `license_expiry_date` datetime(6) DEFAULT NULL,
  `license_number` varchar(50) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `role` enum('DISTRIBUTOR','MANUFACTURER','PHARMACY') NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `wallet_address` varchar(42) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `distributor_users`
--

INSERT INTO `distributor_users` (`id`, `company_address`, `company_name`, `created_at`, `email`, `is_active`, `is_profile_complete`, `is_verified`, `last_login_at`, `license_expiry_date`, `license_number`, `name`, `password_hash`, `phone_number`, `role`, `updated_at`, `wallet_address`) VALUES
('dist-001-uuid', '789 Đường GHI, Quận 3, TP.HCM', 'Nhà phân phối XYZ', '2025-09-29 19:00:12.000000', 'distributor@demo.com', b'1', b'1', b'1', '2025-09-30 09:09:40.000000', NULL, NULL, 'Nguyễn Văn Phân Phối', '$2a$10$uN57ieoP7PaMW9qkLUTfbOquJScUoXF7KEDsxr6Spcl.XwyH8h5XO', '0903456789', 'DISTRIBUTOR', '2025-09-30 09:33:35.000000', '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'),
('dist-002-uuid', '321 Đường JKL, Quận 7, TP.HCM', 'Zuellig Pharma Vietnam', '2025-09-29 19:00:12.000000', 'zuellig@demo.com', b'1', b'1', b'1', NULL, NULL, NULL, 'Trần Thị Zuellig', '$2a$10$LYes.J77LJsTVkcrK.Eea.CzbAosv/MhaWbPx5KZoIGwriBg3rIfq', '0904567890', 'DISTRIBUTOR', NULL, '0x90F79bf6EB2c4f870365E785982E1f101E93b906');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `drug_batches`
--

CREATE TABLE `drug_batches` (
  `id` bigint(20) NOT NULL,
  `batch_id` decimal(38,0) NOT NULL,
  `batch_number` varchar(100) NOT NULL,
  `block_number` decimal(38,0) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `current_owner` varchar(42) NOT NULL,
  `drug_name` varchar(255) NOT NULL,
  `expiry_date` datetime(6) NOT NULL,
  `is_synced` bit(1) NOT NULL,
  `manufacture_timestamp` datetime(6) NOT NULL,
  `manufacturer` varchar(255) NOT NULL,
  `manufacturer_address` varchar(42) NOT NULL,
  `qr_code` varchar(1000) DEFAULT NULL,
  `quantity` bigint(20) NOT NULL,
  `status` enum('DELIVERED','IN_TRANSIT','MANUFACTURED','SOLD') NOT NULL,
  `storage_conditions` varchar(500) DEFAULT NULL,
  `transaction_hash` varchar(66) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL
) ;

--
-- Đang đổ dữ liệu cho bảng `drug_batches`
--

INSERT INTO `drug_batches` (`id`, `batch_id`, `batch_number`, `block_number`, `created_at`, `current_owner`, `drug_name`, `expiry_date`, `is_synced`, `manufacture_timestamp`, `manufacturer`, `manufacturer_address`, `qr_code`, `quantity`, `status`, `storage_conditions`, `transaction_hash`, `updated_at`) VALUES
(1, 17583466080285480, 'BATCH-2024-001', NULL, '2025-09-29 19:00:12.000000', '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC', 'Paracetamol 500mg', '2027-09-29 19:00:12.000000', b'1', '2025-09-29 19:00:12.000000', 'Công ty Dược phẩm ABC', '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266', 'QR-PARA-001', 500, 'DELIVERED', 'Bảo quản nơi khô ráo, thoáng mát', NULL, '2025-09-30 08:22:50.000000'),
(2, 1001, 'BATCH-2024-002', NULL, '2025-09-29 19:00:12.000000', '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266', 'Amoxicillin 250mg', '2027-03-29 19:00:12.000000', b'1', '2025-09-29 19:00:12.000000', 'Công ty Dược phẩm ABC', '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266', 'QR-AMOX-002', 500, 'IN_TRANSIT', 'Bảo quản nơi khô ráo, tránh ánh sáng', NULL, '2025-09-29 14:12:31.000000'),
(3, 2001, 'BATCH-2024-003', NULL, '2025-09-29 19:00:12.000000', '0x70997970C51812dc3A010C7d01b50e0d17dc79C8', 'Vitamin C 1000mg', '2028-09-29 19:00:12.000000', b'1', '2025-09-29 19:00:12.000000', 'Traphaco JSC', '0x70997970C51812dc3A010C7d01b50e0d17dc79C8', 'QR-VITC-003', 2000, 'MANUFACTURED', 'Bảo quản nơi khô ráo', NULL, '2025-09-29 19:00:12.000000');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `drug_products`
--

CREATE TABLE `drug_products` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `active_ingredient` varchar(255) DEFAULT NULL,
  `dosage` varchar(100) DEFAULT NULL,
  `dosage_form` enum('tablet','capsule','syrup','injection','cream','drops','other') DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `manufacturer_id` bigint(20) NOT NULL,
  `description` text DEFAULT NULL,
  `storage_conditions` varchar(500) DEFAULT NULL,
  `shelf_life_months` int(11) DEFAULT NULL,
  `registration_number` varchar(100) DEFAULT NULL,
  `approval_date` date DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `shelf_life` varchar(100) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `unit` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `drug_products`
--

INSERT INTO `drug_products` (`id`, `name`, `active_ingredient`, `dosage`, `dosage_form`, `category`, `manufacturer_id`, `description`, `storage_conditions`, `shelf_life_months`, `registration_number`, `approval_date`, `is_active`, `created_at`, `updated_at`, `shelf_life`, `status`, `unit`) VALUES
(1, 'Paracetamol 500mg', 'Paracetamol', '500mg', 'tablet', 'Giảm đau, hạ sốt', 1, 'Thuốc giảm đau, hạ sốt', 'Bảo quản nơi khô ráo, thoáng mát', 24, 'VD-12345-20', NULL, 1, '2025-09-29 12:00:12', '2025-09-29 12:00:12', NULL, 'ACTIVE', NULL),
(2, 'Amoxicillin 250mg', 'Amoxicillin', '250mg', 'capsule', 'Kháng sinh', 1, 'Kháng sinh phổ rộng', 'Bảo quản nơi khô ráo, tránh ánh sáng', 18, 'VD-12346-20', NULL, 1, '2025-09-29 12:00:12', '2025-09-29 12:00:12', NULL, 'ACTIVE', NULL),
(3, 'Vitamin C 1000mg', 'Acid Ascorbic', '1000mg', 'tablet', 'Vitamin', 2, 'Bổ sung vitamin C', 'Bảo quản nơi khô ráo', 36, 'VD-12347-20', NULL, 1, '2025-09-29 12:00:12', '2025-09-29 12:00:12', NULL, 'ACTIVE', NULL);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `drug_shipments`
--

CREATE TABLE `drug_shipments` (
  `id` bigint(20) NOT NULL,
  `shipment_code` varchar(100) NOT NULL,
  `batch_id` bigint(20) NOT NULL,
  `from_company_id` bigint(20) NOT NULL,
  `to_company_id` bigint(20) NOT NULL,
  `quantity` int(11) NOT NULL,
  `shipment_date` timestamp NULL DEFAULT NULL,
  `expected_delivery_date` timestamp NULL DEFAULT NULL,
  `actual_delivery_date` timestamp NULL DEFAULT NULL,
  `shipment_status` enum('PENDING','IN_TRANSIT','DELIVERED','CANCELLED') DEFAULT 'PENDING',
  `create_tx_hash` varchar(66) DEFAULT NULL,
  `receive_tx_hash` varchar(66) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ;

--
-- Đang đổ dữ liệu cho bảng `drug_shipments`
--

INSERT INTO `drug_shipments` (`id`, `shipment_code`, `batch_id`, `from_company_id`, `to_company_id`, `quantity`, `shipment_date`, `expected_delivery_date`, `actual_delivery_date`, `shipment_status`, `create_tx_hash`, `receive_tx_hash`, `notes`, `created_at`, `updated_at`) VALUES
(1, 'SHIP-2024-001', 1, 1, 3, 100, '2025-09-29 12:00:12', '2025-10-02 12:00:12', NULL, 'PENDING', NULL, NULL, '{\"blockchain_id\": \"17583466080285480\", \"from_address\": \"0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266\", \"to_address\": \"0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC\"}', '2025-09-29 12:00:12', '2025-09-29 12:00:12'),
(2, 'SHIP-2024-002', 2, 3, 5, 50, '2025-09-29 12:00:12', '2025-10-01 12:00:12', NULL, 'IN_TRANSIT', NULL, NULL, '{\"blockchain_id\": \"1001\", \"from_address\": \"0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC\", \"to_address\": \"0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65\"}', '2025-09-29 12:00:12', '2025-09-29 12:00:12'),
(12, 'SHIP-17591528224436380', 1, 1, 3, 500, '2025-09-29 06:33:42', '2025-10-02 06:33:42', '2025-09-29 07:40:00', 'DELIVERED', '0x21a2fbe3d39b0b375121d6b1937d527cfe562e024930a16f55ee31cd1df92d82', NULL, '{\"block_number\":\"10\",\"to_address\":\"0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC\",\"original_shipment_id\":\"17591528224436381\",\"from_address\":\"0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266\",\"tracking_info\":\"Shipment to Nhà phân phối XYZ\",\"is_synced\":true}', '2025-09-29 06:33:42', '2025-09-29 07:40:00'),
(13, 'SHIP-17591551514629408', 2, 1, 3, 250, '2025-09-29 07:12:31', '2025-10-02 07:12:31', NULL, 'PENDING', '0xbc4409983860845a7ee24a76593c923b53545d2e485ec8c238a96fa1fd738480', NULL, '{\"block_number\":\"11\",\"to_address\":\"0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC\",\"original_shipment_id\":\"17591551514629408\",\"from_address\":\"0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266\",\"tracking_info\":\"Shipment to Nhà phân phối XYZ\",\"is_synced\":true}', '2025-09-29 07:12:31', '2025-09-29 07:12:31'),
(14, 'SHIP-1759220569914', 1, 3, 5, 500, '2025-09-30 01:22:50', '2025-10-02 01:22:50', NULL, 'IN_TRANSIT', '0x9e6c6fd6246e2667dcb6d886be78f4aaf750ebd1ec74aebc0777de08e0820348', NULL, '{\"block_number\":\"1\",\"to_address\":\"0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65\",\"original_shipment_id\":\"1759220569914\",\"from_address\":\"0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC\",\"tracking_info\":\"SH569158P30\",\"is_synced\":true, \"shipment_info\": {\"driver_name\": \"\", \"pharmacy_address\": \"456 Đường MNO, Quận 2, TP.HCM\", \"user_notes\": \"\", \"pharmacy_name\": \"Hiệu thuốc An Khang\", \"transport_method\": \"Xe tải\", \"tracking_number\": \"SH569158P30\", \"driver_phone\": \"\"}}', '2025-09-30 01:22:50', '2025-09-30 01:22:50');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `drug_verification_records`
--

CREATE TABLE `drug_verification_records` (
  `id` bigint(20) NOT NULL,
  `batch_id` bigint(20) NOT NULL,
  `verified_by_company_id` bigint(20) DEFAULT NULL,
  `verification_type` enum('QR_SCAN','MANUAL_CHECK','COUNTER_VERIFICATION','CONSUMER_SCAN') NOT NULL,
  `verification_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `verification_location` varchar(255) DEFAULT NULL,
  `is_authentic` tinyint(1) NOT NULL,
  `verification_result` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`verification_result`)),
  `scanner_device` varchar(100) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `blockchain_verified` tinyint(1) DEFAULT 0,
  `blockchain_query_time_ms` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `inventory_movements`
--

CREATE TABLE `inventory_movements` (
  `id` bigint(20) NOT NULL,
  `inventory_type` enum('DISTRIBUTOR','PHARMACY') NOT NULL,
  `inventory_id` bigint(20) NOT NULL COMMENT 'ID của distributor_inventory hoặc pharmacy_inventory',
  `movement_type` enum('RECEIVE','SHIP_OUT','SALE','RETURN','ADJUSTMENT','DAMAGE','EXPIRED','RECALL','TRANSFER') NOT NULL,
  `quantity_before` int(11) NOT NULL,
  `quantity_change` int(11) NOT NULL COMMENT 'Số dương = tăng, số âm = giảm',
  `quantity_after` int(11) NOT NULL,
  `related_shipment_id` bigint(20) DEFAULT NULL,
  `related_sale_id` bigint(20) DEFAULT NULL COMMENT 'FK to sales/orders (if exists)',
  `performed_by` varchar(36) DEFAULT NULL COMMENT 'User thực hiện',
  `reason` varchar(500) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `movement_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Lịch sử biến động kho (nhập/xuất/bán/điều chỉnh)';

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `manufacturer_users`
--

CREATE TABLE `manufacturer_users` (
  `id` varchar(36) NOT NULL,
  `company_address` varchar(500) DEFAULT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `email` varchar(255) NOT NULL,
  `is_verified` bit(1) NOT NULL,
  `last_login_at` datetime(6) DEFAULT NULL,
  `license_number` varchar(50) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('ADMIN','DISTRIBUTOR','MANUFACTURER','PHARMACY','USER') NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `wallet_address` varchar(42) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `manufacturer_users`
--

INSERT INTO `manufacturer_users` (`id`, `company_address`, `company_name`, `created_at`, `email`, `is_verified`, `last_login_at`, `license_number`, `name`, `password_hash`, `role`, `updated_at`, `wallet_address`) VALUES
('manu-001-uuid', '123 Đường ABC, Quận 1, TP.HCM', 'Công ty Dược phẩm ABC', '2025-09-29 19:00:12.000000', 'manufacturer@demo.com', b'1', '2025-09-30 09:09:39.000000', NULL, 'Lê Văn Sản Xuất', '$2a$10$spx7GchkASRJLkExmlVKbeDOnadX5Sls2ZxMA/RJ7yPfI0zp53gF6', 'MANUFACTURER', '2025-09-30 09:33:35.000000', '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'),
('manu-002-uuid', '456 Đường DEF, Hà Nội', 'Traphaco JSC', '2025-09-29 19:00:12.000000', 'traphaco@demo.com', b'1', NULL, NULL, 'Phạm Thị Traphaco', '$2a$10$tyE/oab7/nH7Al93GIpA3eGPL1xmxn0xTNq5RFKCn7Wbv2Q1zSayW', 'MANUFACTURER', NULL, '0x70997970C51812dc3A010C7d01b50e0d17dc79C8');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `medical_specialties`
--

CREATE TABLE `medical_specialties` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `parent_specialty_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `medical_specialties`
--

INSERT INTO `medical_specialties` (`id`, `name`, `description`, `parent_specialty_id`, `created_at`) VALUES
(1, 'Nội khoa', 'Chuyên khoa điều trị các bệnh nội tạng', NULL, '2025-09-04 13:30:25'),
(2, 'Ngoại khoa', 'Chuyên khoa phẫu thuật', NULL, '2025-09-04 13:30:25'),
(3, 'Sản phụ khoa', 'Chuyên khoa sản khoa và phụ khoa', NULL, '2025-09-04 13:30:25'),
(4, 'Nhi khoa', 'Chuyên khoa điều trị trẻ em', NULL, '2025-09-04 13:30:25'),
(5, 'Tim mạch', 'Chuyên khoa tim mạch', NULL, '2025-09-04 13:30:25'),
(6, 'Thần kinh', 'Chuyên khoa thần kinh', NULL, '2025-09-04 13:30:25'),
(7, 'Tâm thần', 'Chuyên khoa tâm thần', NULL, '2025-09-04 13:30:25'),
(8, 'Da liễu', 'Chuyên khoa da liễu', NULL, '2025-09-04 13:30:25'),
(9, 'Mắt', 'Chuyên khoa mắt', NULL, '2025-09-04 13:30:25'),
(10, 'Tai mũi họng', 'Chuyên khoa tai mũi họng', NULL, '2025-09-04 13:30:25'),
(11, 'Cơ xương khớp', 'Chuyên khoa cơ xương khớp', NULL, '2025-09-04 13:30:25'),
(12, 'Tiết niệu', 'Chuyên khoa tiết niệu', NULL, '2025-09-04 13:30:25'),
(13, 'Nội tiết', 'Chuyên khoa nội tiết', NULL, '2025-09-04 13:30:25'),
(14, 'Hô hấp', 'Chuyên khoa hô hấp', NULL, '2025-09-04 13:30:25'),
(15, 'Tiêu hóa', 'Chuyên khoa tiêu hóa', NULL, '2025-09-04 13:30:25');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `medications`
--

CREATE TABLE `medications` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `generic_name` varchar(200) DEFAULT NULL,
  `brand_names` text DEFAULT NULL,
  `drug_class` varchar(100) DEFAULT NULL,
  `dosage_forms` text DEFAULT NULL,
  `common_dosages` text DEFAULT NULL,
  `contraindications` text DEFAULT NULL,
  `side_effects` text DEFAULT NULL,
  `interactions` text DEFAULT NULL,
  `pregnancy_category` enum('A','B','C','D','X','unknown') DEFAULT NULL,
  `requires_prescription` tinyint(1) DEFAULT 1,
  `is_controlled_substance` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `medications`
--

INSERT INTO `medications` (`id`, `name`, `generic_name`, `brand_names`, `drug_class`, `dosage_forms`, `common_dosages`, `contraindications`, `side_effects`, `interactions`, `pregnancy_category`, `requires_prescription`, `is_controlled_substance`, `created_at`) VALUES
(1, 'Paracetamol 500mg', 'Paracetamol', NULL, 'Giảm đau hạ sốt', '[\"tablet\", \"capsule\"]', '[\"500mg\"]', '[\"Allergy to paracetamol\"]', '[\"Nausea\", \"Rash\"]', '[\"Warfarin\"]', 'B', 0, 0, '2025-09-20 05:29:14'),
(2, 'Amoxicillin 250mg', 'Amoxicillin', NULL, 'Kháng sinh', '[\"capsule\", \"tablet\"]', '[\"250mg\", \"500mg\"]', '[\"Penicillin allergy\"]', '[\"Diarrhea\", \"Nausea\"]', '[\"Warfarin\", \"Methotrexate\"]', 'B', 1, 0, '2025-09-20 05:29:14'),
(3, 'Vitamin C 1000mg', 'Ascorbic Acid', NULL, 'Vitamin & KCS', '[\"tablet\", \"effervescent\"]', '[\"1000mg\", \"500mg\"]', '[\"Kidney stones\"]', '[\"Stomach upset\"]', '[\"Iron supplements\"]', 'A', 0, 0, '2025-09-20 05:29:14'),
(4, 'Metformin 500mg', 'Metformin HCl', NULL, 'Thuốc tiểu đường', '[\"tablet\", \"extended-release\"]', '[\"500mg\", \"850mg\", \"1000mg\"]', '[\"Kidney disease\", \"Heart failure\"]', '[\"Nausea\", \"Diarrhea\", \"Metallic taste\"]', '[\"Alcohol\", \"Iodinated contrast\"]', 'B', 1, 0, '2025-09-20 05:29:14'),
(5, 'Ibuprofen 400mg', 'Ibuprofen', NULL, 'Giảm đau hạ sốt', '[\"tablet\", \"capsule\", \"gel\"]', '[\"200mg\", \"400mg\", \"600mg\"]', '[\"NSAID allergy\", \"Peptic ulcer\"]', '[\"Stomach pain\", \"Headache\"]', '[\"Warfarin\", \"ACE inhibitors\"]', 'C', 0, 0, '2025-09-20 05:29:14'),
(6, 'Aspirin 100mg', 'Acetylsalicylic Acid', NULL, 'Thuốc tim mạch', '[\"tablet\", \"enteric-coated\"]', '[\"75mg\", \"100mg\", \"300mg\"]', '[\"Bleeding disorders\", \"Children with viral infections\"]', '[\"Stomach bleeding\", \"Tinnitus\"]', '[\"Warfarin\", \"Methotrexate\"]', 'D', 0, 0, '2025-09-20 05:29:14'),
(7, 'Omeprazole 20mg', 'Omeprazole', NULL, 'Thuốc tiêu hóa', '[\"capsule\", \"tablet\"]', '[\"10mg\", \"20mg\", \"40mg\"]', '[\"Hypersensitivity to proton pump inhibitors\"]', '[\"Headache\", \"Nausea\", \"Diarrhea\"]', '[\"Clopidogrel\", \"Warfarin\"]', 'C', 1, 0, '2025-09-20 05:29:14'),
(8, 'Cetirizine 10mg', 'Cetirizine HCl', NULL, 'Thuốc dị ứng', '[\"tablet\", \"syrup\"]', '[\"5mg\", \"10mg\"]', '[\"Severe kidney disease\"]', '[\"Drowsiness\", \"Dry mouth\"]', '[\"Alcohol\", \"CNS depressants\"]', 'B', 0, 0, '2025-09-20 05:29:14'),
(9, 'Paracetamol 500mg', 'Paracetamol', NULL, 'Giảm đau hạ sốt', '[\"tablet\", \"capsule\"]', '[\"500mg\"]', '[\"Allergy to paracetamol\"]', '[\"Nausea\", \"Rash\"]', '[\"Warfarin\"]', 'B', 0, 0, '2025-09-20 05:33:41');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `ml_model_performance`
--

CREATE TABLE `ml_model_performance` (
  `id` int(11) NOT NULL,
  `model_name` varchar(100) NOT NULL,
  `model_version` varchar(50) NOT NULL,
  `accuracy_rate` decimal(5,2) DEFAULT NULL,
  `precision_score` decimal(5,2) DEFAULT NULL,
  `recall_score` decimal(5,2) DEFAULT NULL,
  `f1_score` decimal(5,2) DEFAULT NULL,
  `total_predictions` int(11) DEFAULT 0,
  `correct_predictions` int(11) DEFAULT 0,
  `false_positives` int(11) DEFAULT 0,
  `false_negatives` int(11) DEFAULT 0,
  `performance_by_specialty` text DEFAULT NULL,
  `performance_by_severity` text DEFAULT NULL,
  `evaluation_date` date NOT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `news_articles`
--

CREATE TABLE `news_articles` (
  `id` int(11) NOT NULL,
  `author` varchar(200) DEFAULT NULL,
  `bookmark_count` int(11) NOT NULL,
  `content` longtext DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `fact_checked` bit(1) NOT NULL,
  `image_url` varchar(1000) DEFAULT NULL,
  `last_updated` datetime(6) DEFAULT NULL,
  `medical_accuracy_score` decimal(3,2) DEFAULT NULL,
  `publication_date` datetime(6) DEFAULT NULL,
  `reading_level` enum('advanced','basic','intermediate') DEFAULT NULL,
  `related_diseases` text DEFAULT NULL,
  `related_symptoms` text DEFAULT NULL,
  `share_count` int(11) NOT NULL,
  `source_name` varchar(100) DEFAULT NULL,
  `summary` text DEFAULT NULL,
  `target_audience` enum('general_public','patients','professionals') DEFAULT NULL,
  `title` varchar(500) NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `url` varchar(1000) DEFAULT NULL,
  `view_count` int(11) NOT NULL,
  `primary_category_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `ownership_history`
--

CREATE TABLE `ownership_history` (
  `id` bigint(20) NOT NULL,
  `batch_id` bigint(20) NOT NULL,
  `from_company_id` bigint(20) DEFAULT NULL,
  `to_company_id` bigint(20) NOT NULL,
  `transfer_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `transfer_type` enum('MANUFACTURE','SHIPMENT','DELIVERY','SALE') NOT NULL,
  `quantity_transferred` int(11) DEFAULT NULL,
  `blockchain_tx_hash` varchar(66) NOT NULL,
  `block_number` bigint(20) DEFAULT NULL,
  `gas_used` bigint(20) DEFAULT NULL,
  `event_log_index` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `pharmacy_inventory`
--

CREATE TABLE `pharmacy_inventory` (
  `id` bigint(20) NOT NULL,
  `pharmacy_id` bigint(20) NOT NULL COMMENT 'FK to pharma_companies (PHARMACY)',
  `batch_id` bigint(20) NOT NULL COMMENT 'FK to drug_batches',
  `drug_name` varchar(255) NOT NULL,
  `manufacturer` varchar(255) NOT NULL,
  `batch_number` varchar(100) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 0 COMMENT 'Số lượng hiện có trong kho',
  `reserved_quantity` int(11) NOT NULL DEFAULT 0 COMMENT 'Số lượng đã được đặt trước (đơn hàng online)',
  `available_quantity` int(11) GENERATED ALWAYS AS (`quantity` - `reserved_quantity`) STORED COMMENT 'Số lượng có thể bán',
  `sold_quantity` int(11) NOT NULL DEFAULT 0 COMMENT 'Tổng số lượng đã bán',
  `manufacture_date` timestamp NULL DEFAULT NULL,
  `expiry_date` timestamp NULL DEFAULT NULL,
  `qr_code` varchar(1000) DEFAULT NULL,
  `shelf_location` varchar(100) DEFAULT 'Kệ chính' COMMENT 'Vị trí: Kệ A, Tủ B, Quầy 1, v.v.',
  `storage_conditions` varchar(500) DEFAULT NULL,
  `storage_temperature` varchar(50) DEFAULT NULL,
  `cost_price` decimal(15,2) DEFAULT 0.00 COMMENT 'Giá vốn (mua từ NPP)',
  `retail_price` decimal(15,2) DEFAULT 0.00 COMMENT 'Giá bán lẻ cho khách hàng',
  `discount_price` decimal(15,2) DEFAULT NULL COMMENT 'Giá khuyến mãi (nếu có)',
  `total_value` decimal(15,2) GENERATED ALWAYS AS (`quantity` * `cost_price`) STORED,
  `profit_margin` decimal(5,2) GENERATED ALWAYS AS (case when `cost_price` > 0 then (`retail_price` - `cost_price`) / `cost_price` * 100 else 0 end) STORED COMMENT 'Lợi nhuận %',
  `status` enum('IN_STOCK','LOW_STOCK','OUT_OF_STOCK','EXPIRING_SOON','EXPIRED','RECALL') DEFAULT 'IN_STOCK',
  `min_stock_level` int(11) DEFAULT 20 COMMENT 'Ngưỡng cảnh báo hết hàng',
  `max_stock_level` int(11) DEFAULT 500 COMMENT 'Ngưỡng tồn kho tối đa',
  `reorder_point` int(11) DEFAULT 30 COMMENT 'Điểm đặt hàng lại',
  `blockchain_batch_id` decimal(38,0) DEFAULT NULL,
  `receive_tx_hash` varchar(66) DEFAULT NULL,
  `current_owner_address` varchar(42) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT 0 COMMENT 'Đã xác thực trên blockchain',
  `received_from_distributor_id` bigint(20) DEFAULT NULL COMMENT 'Nhận từ NPP nào',
  `received_shipment_id` bigint(20) DEFAULT NULL COMMENT 'FK to drug_shipments',
  `received_date` timestamp NULL DEFAULT NULL,
  `received_quantity` int(11) DEFAULT 0 COMMENT 'Số lượng nhập ban đầu',
  `first_sale_date` timestamp NULL DEFAULT NULL COMMENT 'Ngày bán đầu tiên',
  `last_sale_date` timestamp NULL DEFAULT NULL COMMENT 'Ngày bán gần nhất',
  `average_daily_sales` decimal(10,2) DEFAULT 0.00 COMMENT 'Trung bình bán/ngày',
  `days_of_supply` int(11) GENERATED ALWAYS AS (case when `average_daily_sales` > 0 then floor(`available_quantity` / `average_daily_sales`) else 999 end) STORED COMMENT 'Số ngày đủ bán',
  `requires_prescription` tinyint(1) DEFAULT 0 COMMENT 'Cần đơn thuốc',
  `controlled_substance` tinyint(1) DEFAULT 0 COMMENT 'Thuốc kiểm soát đặc biệt',
  `is_featured` tinyint(1) DEFAULT 0 COMMENT 'Sản phẩm nổi bật',
  `is_on_sale` tinyint(1) DEFAULT 0 COMMENT 'Đang khuyến mãi',
  `display_order` int(11) DEFAULT 999 COMMENT 'Thứ tự hiển thị',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by` varchar(36) DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Quản lý kho của hiệu thuốc';

--
-- Đang đổ dữ liệu cho bảng `pharmacy_inventory`
--

INSERT INTO `pharmacy_inventory` (`id`, `pharmacy_id`, `batch_id`, `drug_name`, `manufacturer`, `batch_number`, `quantity`, `reserved_quantity`, `sold_quantity`, `manufacture_date`, `expiry_date`, `qr_code`, `shelf_location`, `storage_conditions`, `storage_temperature`, `cost_price`, `retail_price`, `discount_price`, `status`, `min_stock_level`, `max_stock_level`, `reorder_point`, `blockchain_batch_id`, `receive_tx_hash`, `current_owner_address`, `is_verified`, `received_from_distributor_id`, `received_shipment_id`, `received_date`, `received_quantity`, `first_sale_date`, `last_sale_date`, `average_daily_sales`, `requires_prescription`, `controlled_substance`, `is_featured`, `is_on_sale`, `display_order`, `created_at`, `updated_at`, `created_by`, `updated_by`, `notes`) VALUES
(1, 5, 1, 'Paracetamol 500mg', 'Công ty Dược phẩm ABC', 'BATCH-2024-001', 0, 0, 0, '2025-09-29 12:00:12', '2027-09-29 12:00:12', 'QR-PARA-001', 'Quầy 1 - Kệ Giảm đau', NULL, NULL, 7000.00, 10000.00, NULL, 'IN_STOCK', 20, 500, 30, 17583466080285480, NULL, '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65', 1, 3, NULL, NULL, 0, NULL, NULL, 0.00, 0, 0, 0, 0, 999, '2025-09-30 08:57:05', '2025-09-30 08:57:05', NULL, NULL, NULL);

--
-- Bẫy `pharmacy_inventory`
--
DELIMITER $$
CREATE TRIGGER `trg_pharmacy_inventory_movement_log` AFTER UPDATE ON `pharmacy_inventory` FOR EACH ROW BEGIN
    IF OLD.quantity != NEW.quantity THEN
        INSERT INTO `inventory_movements` (
            `inventory_type`,
            `inventory_id`,
            `movement_type`,
            `quantity_before`,
            `quantity_change`,
            `quantity_after`,
            `reason`,
            `movement_date`
        ) VALUES (
            'PHARMACY',
            NEW.id,
            CASE 
                WHEN NEW.quantity > OLD.quantity THEN 'RECEIVE'
                WHEN NEW.quantity < OLD.quantity AND NEW.sold_quantity > OLD.sold_quantity THEN 'SALE'
                WHEN NEW.quantity < OLD.quantity THEN 'ADJUSTMENT'
                ELSE 'ADJUSTMENT'
            END,
            OLD.quantity,
            NEW.quantity - OLD.quantity,
            NEW.quantity,
            'Auto-logged by trigger',
            NOW()
        );
    END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `trg_pharmacy_inventory_status_update` BEFORE UPDATE ON `pharmacy_inventory` FOR EACH ROW BEGIN
    DECLARE days_to_expiry INT;
    SET days_to_expiry = DATEDIFF(NEW.expiry_date, NOW());
    
    -- Kiểm tra hết hạn
    IF days_to_expiry < 0 THEN
        SET NEW.status = 'EXPIRED';
    -- Sắp hết hạn (30 ngày)
    ELSEIF days_to_expiry <= 30 THEN
        SET NEW.status = 'EXPIRING_SOON';
    -- Hết hàng
    ELSEIF NEW.available_quantity <= 0 THEN
        SET NEW.status = 'OUT_OF_STOCK';
    -- Tồn kho thấp
    ELSEIF NEW.available_quantity <= NEW.min_stock_level THEN
        SET NEW.status = 'LOW_STOCK';
    ELSE
        SET NEW.status = 'IN_STOCK';
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `pharmacy_users`
--

CREATE TABLE `pharmacy_users` (
  `id` bigint(20) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `pharmacy_name` varchar(255) NOT NULL,
  `pharmacy_code` varchar(50) DEFAULT NULL,
  `wallet_address` varchar(42) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `is_profile_complete` tinyint(1) NOT NULL DEFAULT 0,
  `last_login_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `pharmacy_users`
--

INSERT INTO `pharmacy_users` (`id`, `email`, `password`, `pharmacy_name`, `pharmacy_code`, `wallet_address`, `address`, `phone`, `is_active`, `is_profile_complete`, `last_login_at`, `created_at`, `updated_at`) VALUES
(1, 'pharmacy@ankhang.com', '$2a$10$MDxKhLpYxBs0uadHKywfa.HweyWMBVmyEpahToXZOCWHje1X5nY9u', 'Hiệu thuốc An Khang', 'HT-2024-001', '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65', '456 Đường MNO, Quận 2, TP.HCM', '0905678901', 1, 1, '2025-09-30 00:45:56', '2025-09-30 07:45:42', '2025-09-30 00:45:56'),
(2, 'pharmacy@pharmacity.vn', '$2a$10$MDxKhLpYxBs0uadHKywfa.HweyWMBVmyEpahToXZOCWHje1X5nY9u', 'Pharmacity Bình Thạnh', 'HT-2024-002', '0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc', '789 Đường PQR, Quận Bình Thạnh, TP.HCM', '0906789012', 1, 1, NULL, '2025-09-30 07:45:42', '2025-09-30 07:45:42');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `pharma_companies`
--

CREATE TABLE `pharma_companies` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `company_type` enum('MANUFACTURER','DISTRIBUTOR','PHARMACY') NOT NULL,
  `wallet_address` varchar(42) DEFAULT NULL,
  `license_number` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `phone` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `contact_person` varchar(255) DEFAULT NULL,
  `registration_number` varchar(100) DEFAULT NULL,
  `tax_code` varchar(50) DEFAULT NULL,
  `establishment_date` date DEFAULT NULL,
  `blockchain_verified` tinyint(1) DEFAULT 0,
  `verification_date` timestamp NULL DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `manufacturer_user_id` varchar(36) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `pharma_companies`
--

INSERT INTO `pharma_companies` (`id`, `name`, `company_type`, `wallet_address`, `license_number`, `address`, `phone`, `email`, `contact_person`, `registration_number`, `tax_code`, `establishment_date`, `blockchain_verified`, `verification_date`, `is_active`, `created_at`, `updated_at`, `manufacturer_user_id`, `status`) VALUES
(1, 'Công ty Dược phẩm ABC', 'MANUFACTURER', '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266', 'NSX-2024-001', '123 Đường ABC, Quận 1, TP.HCM', '0901234567', 'nsx@demo.com', NULL, NULL, NULL, NULL, 0, NULL, 1, '2025-09-29 12:00:12', '2025-09-29 05:54:41', 'manu-001-uuid', 'ACTIVE'),
(2, 'Traphaco JSC', 'MANUFACTURER', '0x70997970C51812dc3A010C7d01b50e0d17dc79C8', 'NSX-2024-002', '456 Đường DEF, Hà Nội', '0902345678', 'info@traphaco.com.vn', NULL, NULL, NULL, NULL, 0, NULL, 1, '2025-09-29 12:00:12', '2025-09-29 12:00:12', NULL, 'ACTIVE'),
(3, 'Nhà phân phối XYZ', 'DISTRIBUTOR', '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC', 'NPP-2024-001', '789 Đường GHI, Quận 3, TP.HCM', '0903456789', 'npp@xyz.com', NULL, NULL, NULL, NULL, 0, NULL, 1, '2025-09-29 12:00:12', '2025-09-29 12:00:12', NULL, 'ACTIVE'),
(4, 'Zuellig Pharma Vietnam', 'DISTRIBUTOR', '0x90F79bf6EB2c4f870365E785982E1f101E93b906', 'NPP-2024-002', '321 Đường JKL, Quận 7, TP.HCM', '0904567890', 'vietnam@zuelligpharma.com', NULL, NULL, NULL, NULL, 0, NULL, 1, '2025-09-29 12:00:12', '2025-09-29 12:00:12', NULL, 'ACTIVE'),
(5, 'Hiệu thuốc An Khang', 'PHARMACY', '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65', 'HT-2024-001', '456 Đường MNO, Quận 2, TP.HCM', '0905678901', 'info@ankhang.com', NULL, NULL, NULL, NULL, 0, NULL, 1, '2025-09-29 12:00:12', '2025-09-29 12:00:12', NULL, 'ACTIVE'),
(6, 'Pharmacity Bình Thạnh', 'PHARMACY', '0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc', 'HT-2024-002', '789 Đường PQR, Quận Bình Thạnh, TP.HCM', '0906789012', 'binhthahn@pharmacity.vn', NULL, NULL, NULL, NULL, 0, NULL, 1, '2025-09-29 12:00:12', '2025-09-29 12:00:12', NULL, 'ACTIVE');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `provinces`
--

CREATE TABLE `provinces` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `code` varchar(10) DEFAULT NULL,
  `region` enum('north','central','south') DEFAULT NULL,
  `climate` enum('tropical','subtropical','temperate') DEFAULT NULL,
  `endemic_diseases` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `provinces`
--

INSERT INTO `provinces` (`id`, `name`, `code`, `region`, `climate`, `endemic_diseases`, `created_at`, `updated_at`) VALUES
(1, 'Hà Nội', 'HN', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(2, 'Hồ Chí Minh', 'HCM', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(3, 'Đà Nẵng', 'DN', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(4, 'Hải Phòng', 'HP', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(5, 'Cần Thơ', 'CT', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(6, 'An Giang', 'AG', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(7, 'Bà Rịa - Vũng Tàu', 'BR', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(8, 'Bạc Liêu', 'BL', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(9, 'Bắc Giang', 'BG', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(10, 'Bắc Kạn', 'BK', 'north', 'temperate', NULL, '2025-09-04 13:30:25', NULL),
(11, 'Bắc Ninh', 'BN', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(12, 'Bến Tre', 'BT', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(13, 'Bình Dương', 'BD', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(14, 'Bình Định', 'BĐ', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(15, 'Bình Phước', 'BP', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(16, 'Bình Thuận', 'BTh', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(17, 'Cà Mau', 'CM', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(18, 'Cao Bằng', 'CB', 'north', 'temperate', NULL, '2025-09-04 13:30:25', NULL),
(19, 'Đắk Lắk', 'ĐL', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(20, 'Đắk Nông', 'ĐN', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(21, 'Điện Biên', 'ĐB', 'north', 'temperate', NULL, '2025-09-04 13:30:25', NULL),
(22, 'Đồng Nai', 'ĐNa', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(23, 'Đồng Tháp', 'ĐT', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(24, 'Gia Lai', 'GL', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(25, 'Hà Giang', 'HG', 'north', 'temperate', NULL, '2025-09-04 13:30:25', NULL),
(26, 'Hà Nam', 'HNa', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(27, 'Hà Tĩnh', 'HT', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(28, 'Hải Dương', 'HĐ', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(29, 'Hậu Giang', 'HGi', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(30, 'Hòa Bình', 'HB', 'north', 'temperate', NULL, '2025-09-04 13:30:25', NULL),
(31, 'Hưng Yên', 'HY', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(32, 'Khánh Hòa', 'KH', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(33, 'Kiên Giang', 'KG', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(34, 'Kon Tum', 'KT', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(35, 'Lai Châu', 'LC', 'north', 'temperate', NULL, '2025-09-04 13:30:25', NULL),
(36, 'Lạng Sơn', 'LS', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(37, 'Lào Cai', 'LCa', 'north', 'temperate', NULL, '2025-09-04 13:30:25', NULL),
(38, 'Lâm Đồng', 'LĐ', 'central', 'temperate', NULL, '2025-09-04 13:30:25', NULL),
(39, 'Long An', 'LA', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(40, 'Nam Định', 'NĐ', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(41, 'Nghệ An', 'NA', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(42, 'Ninh Bình', 'NB', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(43, 'Ninh Thuận', 'NT', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(44, 'Phú Thọ', 'PT', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(45, 'Phú Yên', 'PY', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(46, 'Quảng Bình', 'QB', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(47, 'Quảng Nam', 'QN', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(48, 'Quảng Ngãi', 'QNg', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(49, 'Quảng Ninh', 'QNi', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(50, 'Quảng Trị', 'QT', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(51, 'Sóc Trăng', 'ST', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(52, 'Sơn La', 'SL', 'north', 'temperate', NULL, '2025-09-04 13:30:25', NULL),
(53, 'Tây Ninh', 'TN', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(54, 'Thái Bình', 'TB', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(55, 'Thái Nguyên', 'TNg', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(56, 'Thanh Hóa', 'TH', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(57, 'Thừa Thiên Huế', 'TTH', 'central', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(58, 'Tiền Giang', 'TG', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(59, 'Trà Vinh', 'TV', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(60, 'Tuyên Quang', 'TQ', 'north', 'temperate', NULL, '2025-09-04 13:30:25', NULL),
(61, 'Vĩnh Long', 'VL', 'south', 'tropical', NULL, '2025-09-04 13:30:25', NULL),
(62, 'Vĩnh Phúc', 'VP', 'north', 'subtropical', NULL, '2025-09-04 13:30:25', NULL),
(63, 'Yên Bái', 'YB', 'north', 'temperate', NULL, '2025-09-04 13:30:25', NULL);

-- --------------------------------------------------------

--
-- Cấu trúc đóng vai cho view `recent_diagnoses_summary`
-- (See below for the actual view)
--
CREATE TABLE `recent_diagnoses_summary` (
`user_id` varchar(36)
,`session_id` varchar(36)
,`primary_diagnosis` varchar(200)
,`primary_confidence` decimal(5,2)
,`urgency_level` enum('emergency','urgent','routine','self_care')
,`created_at` timestamp
,`symptoms_count` bigint(21)
);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `symptoms`
--

CREATE TABLE `symptoms` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `severity_scale` enum('1-10','mild-severe','absent-present') DEFAULT NULL,
  `measurement_unit` varchar(50) DEFAULT NULL,
  `related_body_systems` text DEFAULT NULL,
  `common_causes` text DEFAULT NULL,
  `red_flag_indicators` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `users`
--

CREATE TABLE `users` (
  `id` varchar(36) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `last_login_at` timestamp NULL DEFAULT NULL,
  `is_profile_complete` tinyint(1) DEFAULT 0,
  `is_active` tinyint(1) DEFAULT 1,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `users`
--

INSERT INTO `users` (`id`, `email`, `password_hash`, `name`, `created_at`, `last_login_at`, `is_profile_complete`, `is_active`, `updated_at`) VALUES
('076e2d56-8c6e-40f0-b07f-b997442cb66e', 'lebadaomac@gmail.com', '$2a$10$uX7xbqFgg/cx8AfoDfiSde625P/TZb/jvw0T6Rp0WIpUSha8zD5qq', 'quyen', '2025-09-09 10:05:56', '2025-09-12 23:27:38', 1, 1, '2025-09-12 23:27:38'),
('c95e23bb-7a92-47af-a2b3-48d5e9d8a3f7', 'quyen@gmail.com', '$2a$10$/nvz1ezBv0JZs8gZE/cU6e/EUvk2qBLlGJQG3IbEdihr9liBVfTgq', 'quyen', '2025-09-09 20:38:33', NULL, 0, 1, '2025-09-09 20:38:33');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_allergies`
--

CREATE TABLE `user_allergies` (
  `id` int(11) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `allergen_id` int(11) NOT NULL,
  `severity` enum('mild','moderate','severe','anaphylaxis') DEFAULT NULL,
  `first_reaction_date` date DEFAULT NULL,
  `last_reaction_date` date DEFAULT NULL,
  `symptoms_experienced` text DEFAULT NULL,
  `treatment_required` text DEFAULT NULL,
  `confirmed_by_test` tinyint(1) DEFAULT 0,
  `test_type` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_analytics`
--

CREATE TABLE `user_analytics` (
  `id` int(11) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `session_date` date NOT NULL,
  `total_sessions` int(11) DEFAULT 0,
  `total_time_minutes` int(11) DEFAULT 0,
  `features_used` text DEFAULT NULL,
  `symptoms_reported` int(11) DEFAULT 0,
  `diagnoses_received` int(11) DEFAULT 0,
  `articles_read` int(11) DEFAULT 0,
  `recommendations_followed` int(11) DEFAULT 0,
  `average_satisfaction` decimal(3,2) DEFAULT NULL,
  `helpful_responses` int(11) DEFAULT 0,
  `total_responses` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_blockchain_addresses`
--

CREATE TABLE `user_blockchain_addresses` (
  `id` bigint(20) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `blockchain_address` varchar(42) NOT NULL,
  `address_type` enum('MANUFACTURER','DISTRIBUTOR','PHARMACY','CONSUMER') NOT NULL,
  `is_verified` tinyint(1) NOT NULL DEFAULT 0,
  `private_key_encrypted` text DEFAULT NULL COMMENT 'Encrypted private key (optional)',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_chronic_diseases`
--

CREATE TABLE `user_chronic_diseases` (
  `id` int(11) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `disease_id` int(11) NOT NULL,
  `diagnosed_date` date DEFAULT NULL,
  `diagnosed_by` varchar(200) DEFAULT NULL,
  `current_status` enum('active','remission','cured','managed') DEFAULT NULL,
  `severity_current` enum('mild','moderate','severe') DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_demographics`
--

CREATE TABLE `user_demographics` (
  `id` bigint(20) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `birth_year` int(11) NOT NULL,
  `birth_month` int(11) DEFAULT NULL,
  `gender` enum('male','female','other') NOT NULL,
  `height_cm` int(11) DEFAULT NULL,
  `weight_kg` decimal(5,2) DEFAULT NULL,
  `blood_type` enum('A+','A-','B+','B-','AB+','AB-','O+','O-','unknown') DEFAULT NULL,
  `province_id` int(11) DEFAULT NULL,
  `occupation` varchar(100) DEFAULT NULL,
  `education_level` enum('primary','secondary','high_school','bachelor','master','phd','other') DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `user_demographics`
--

INSERT INTO `user_demographics` (`id`, `user_id`, `birth_year`, `birth_month`, `gender`, `height_cm`, `weight_kg`, `blood_type`, `province_id`, `occupation`, `education_level`, `created_at`, `updated_at`) VALUES
(3, '076e2d56-8c6e-40f0-b07f-b997442cb66e', 2004, NULL, 'male', NULL, NULL, NULL, 7, NULL, NULL, '2025-09-09 10:05:57', '2025-09-09 10:05:57');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_family_history`
--

CREATE TABLE `user_family_history` (
  `id` int(11) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `relationship` enum('mother','father','sibling','grandparent','aunt_uncle','cousin','other') DEFAULT NULL,
  `disease_id` int(11) NOT NULL,
  `age_of_onset` int(11) DEFAULT NULL,
  `is_deceased` tinyint(1) DEFAULT 0,
  `cause_of_death` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc đóng vai cho view `user_health_profiles`
-- (See below for the actual view)
--
CREATE TABLE `user_health_profiles` (
`user_id` varchar(36)
,`email` varchar(255)
,`name` varchar(255)
,`birth_year` int(11)
,`gender` enum('male','female','other')
,`height_cm` int(11)
,`weight_kg` decimal(5,2)
,`blood_type` enum('A+','A-','B+','B-','AB+','AB-','O+','O-','unknown')
,`province_name` varchar(100)
,`region` enum('north','central','south')
,`smoking_status` enum('never','former','current')
,`alcohol_frequency` enum('never','rarely','weekly','daily')
,`exercise_frequency` enum('none','rare','weekly','daily')
,`chronic_disease_count` bigint(21)
,`active_medication_count` bigint(21)
,`allergy_count` bigint(21)
);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_lifestyle`
--

CREATE TABLE `user_lifestyle` (
  `id` int(11) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `smoking_status` enum('never','former','current') NOT NULL,
  `smoking_start_age` int(11) DEFAULT NULL,
  `smoking_quit_age` int(11) DEFAULT NULL,
  `cigarettes_per_day` int(11) DEFAULT NULL,
  `years_smoked` int(11) DEFAULT NULL,
  `alcohol_frequency` enum('never','rarely','weekly','daily') DEFAULT NULL,
  `alcohol_units_per_week` decimal(4,1) DEFAULT NULL,
  `alcohol_type_preference` text DEFAULT NULL,
  `exercise_frequency` enum('none','rare','weekly','daily') DEFAULT NULL,
  `exercise_intensity` enum('light','moderate','vigorous') DEFAULT NULL,
  `exercise_duration_minutes` int(11) DEFAULT NULL,
  `exercise_types` text DEFAULT NULL,
  `diet_type` enum('omnivore','vegetarian','vegan','keto','paleo','other') DEFAULT NULL,
  `meals_per_day` int(11) DEFAULT 3,
  `water_intake_liters` decimal(3,1) DEFAULT NULL,
  `sleep_hours_average` decimal(3,1) DEFAULT NULL,
  `sleep_quality` enum('poor','fair','good','excellent') DEFAULT NULL,
  `sleep_disorders` text DEFAULT NULL,
  `stress_level` enum('low','moderate','high','severe') DEFAULT NULL,
  `mental_health_status` enum('excellent','good','fair','poor') DEFAULT NULL,
  `work_environment` enum('office','outdoor','industrial','medical','other') DEFAULT NULL,
  `chemical_exposure` tinyint(1) DEFAULT 0,
  `physical_demands` enum('sedentary','light','moderate','heavy') DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `user_lifestyle`
--

INSERT INTO `user_lifestyle` (`id`, `user_id`, `smoking_status`, `smoking_start_age`, `smoking_quit_age`, `cigarettes_per_day`, `years_smoked`, `alcohol_frequency`, `alcohol_units_per_week`, `alcohol_type_preference`, `exercise_frequency`, `exercise_intensity`, `exercise_duration_minutes`, `exercise_types`, `diet_type`, `meals_per_day`, `water_intake_liters`, `sleep_hours_average`, `sleep_quality`, `sleep_disorders`, `stress_level`, `mental_health_status`, `work_environment`, `chemical_exposure`, `physical_demands`, `created_at`, `updated_at`) VALUES
(4, '076e2d56-8c6e-40f0-b07f-b997442cb66e', 'never', NULL, NULL, NULL, NULL, 'never', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, '2025-09-09 10:05:57', '2025-09-09 10:05:57');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_medications`
--

CREATE TABLE `user_medications` (
  `id` int(11) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `medication_id` int(11) NOT NULL,
  `dosage` varchar(50) DEFAULT NULL,
  `frequency` varchar(50) DEFAULT NULL,
  `route` enum('oral','injection','topical','inhaled','other') DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `prescribed_by` varchar(200) DEFAULT NULL,
  `indication` varchar(200) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `adherence_level` enum('excellent','good','fair','poor') DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_news_interactions`
--

CREATE TABLE `user_news_interactions` (
  `id` int(11) NOT NULL,
  `interaction_timestamp` datetime(6) NOT NULL,
  `interaction_type` enum('bookmark','like','report','share','view') DEFAULT NULL,
  `reading_time_seconds` int(11) DEFAULT NULL,
  `article_id` int(11) NOT NULL,
  `user_id` varchar(36) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_symptom_reports`
--

CREATE TABLE `user_symptom_reports` (
  `id` int(11) NOT NULL,
  `user_id` varchar(36) NOT NULL,
  `session_id` varchar(36) DEFAULT NULL,
  `symptom_id` int(11) NOT NULL,
  `severity` int(11) DEFAULT NULL,
  `duration_hours` int(11) DEFAULT NULL,
  `frequency` enum('constant','intermittent','occasional') DEFAULT NULL,
  `triggers` text DEFAULT NULL,
  `associated_symptoms` text DEFAULT NULL,
  `location_body_part` varchar(100) DEFAULT NULL,
  `quality_description` text DEFAULT NULL,
  `onset_type` enum('sudden','gradual') DEFAULT NULL,
  `reported_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc đóng vai cho view `v_batch_status`
-- (See below for the actual view)
--
CREATE TABLE `v_batch_status` (
`batch_id` decimal(38,0)
,`drug_name` varchar(255)
,`batch_number` varchar(100)
,`manufacturer` varchar(255)
,`quantity` bigint(20)
,`status` enum('DELIVERED','IN_TRANSIT','MANUFACTURED','SOLD')
,`expiry_date` datetime(6)
,`validity_status` varchar(13)
,`current_owner_name` varchar(255)
);

-- --------------------------------------------------------

--
-- Cấu trúc đóng vai cho view `v_blockchain_overview`
-- (See below for the actual view)
--
CREATE TABLE `v_blockchain_overview` (
`transaction_hash` varchar(66)
,`function_name` varchar(100)
,`from_address` varchar(42)
,`to_address` varchar(42)
,`status` enum('FAILED','PENDING','REVERTED','SUCCESS')
,`gas_used` decimal(38,0)
,`timestamp` datetime(6)
,`batch_drug_name` varchar(255)
,`shipment_code` varchar(100)
);

-- --------------------------------------------------------

--
-- Cấu trúc đóng vai cho view `v_company_users`
-- (See below for the actual view)
--
CREATE TABLE `v_company_users` (
`company_id` bigint(20)
,`company_name` varchar(255)
,`company_type` enum('MANUFACTURER','DISTRIBUTOR','PHARMACY')
,`wallet_address` varchar(42)
,`license_number` varchar(255)
,`user_email` varchar(255)
,`user_name` varchar(255)
,`user_type` varchar(12)
);

-- --------------------------------------------------------

--
-- Cấu trúc đóng vai cho view `v_distributor_inventory_full`
-- (See below for the actual view)
--
CREATE TABLE `v_distributor_inventory_full` (
`id` bigint(20)
,`distributor_id` bigint(20)
,`batch_id` bigint(20)
,`drug_name` varchar(255)
,`manufacturer` varchar(255)
,`batch_number` varchar(100)
,`quantity` int(11)
,`reserved_quantity` int(11)
,`available_quantity` int(11)
,`manufacture_date` timestamp
,`expiry_date` timestamp
,`qr_code` varchar(1000)
,`warehouse_location` varchar(100)
,`storage_conditions` varchar(500)
,`storage_temperature` varchar(50)
,`unit_price` decimal(15,2)
,`selling_price` decimal(15,2)
,`total_value` decimal(15,2)
,`status` enum('GOOD','LOW_STOCK','EXPIRING_SOON','EXPIRED','QUARANTINE')
,`min_stock_level` int(11)
,`max_stock_level` int(11)
,`blockchain_batch_id` decimal(38,0)
,`receive_tx_hash` varchar(66)
,`current_owner_address` varchar(42)
,`received_from_company_id` bigint(20)
,`received_shipment_id` bigint(20)
,`received_date` timestamp
,`received_quantity` int(11)
,`created_at` timestamp
,`updated_at` timestamp
,`created_by` varchar(36)
,`updated_by` varchar(36)
,`notes` text
,`distributor_name` varchar(255)
,`distributor_wallet` varchar(42)
,`batch_status` enum('DELIVERED','IN_TRANSIT','MANUFACTURED','SOLD')
,`manufacturer_address` varchar(42)
,`days_to_expiry` int(7)
,`alert_status` varchar(13)
);

-- --------------------------------------------------------

--
-- Cấu trúc đóng vai cho view `v_pharmacy_inventory_full`
-- (See below for the actual view)
--
CREATE TABLE `v_pharmacy_inventory_full` (
`id` bigint(20)
,`pharmacy_id` bigint(20)
,`batch_id` bigint(20)
,`drug_name` varchar(255)
,`manufacturer` varchar(255)
,`batch_number` varchar(100)
,`quantity` int(11)
,`reserved_quantity` int(11)
,`available_quantity` int(11)
,`sold_quantity` int(11)
,`manufacture_date` timestamp
,`expiry_date` timestamp
,`qr_code` varchar(1000)
,`shelf_location` varchar(100)
,`storage_conditions` varchar(500)
,`storage_temperature` varchar(50)
,`cost_price` decimal(15,2)
,`retail_price` decimal(15,2)
,`discount_price` decimal(15,2)
,`total_value` decimal(15,2)
,`profit_margin` decimal(5,2)
,`status` enum('IN_STOCK','LOW_STOCK','OUT_OF_STOCK','EXPIRING_SOON','EXPIRED','RECALL')
,`min_stock_level` int(11)
,`max_stock_level` int(11)
,`reorder_point` int(11)
,`blockchain_batch_id` decimal(38,0)
,`receive_tx_hash` varchar(66)
,`current_owner_address` varchar(42)
,`is_verified` tinyint(1)
,`received_from_distributor_id` bigint(20)
,`received_shipment_id` bigint(20)
,`received_date` timestamp
,`received_quantity` int(11)
,`first_sale_date` timestamp
,`last_sale_date` timestamp
,`average_daily_sales` decimal(10,2)
,`days_of_supply` int(11)
,`requires_prescription` tinyint(1)
,`controlled_substance` tinyint(1)
,`is_featured` tinyint(1)
,`is_on_sale` tinyint(1)
,`display_order` int(11)
,`created_at` timestamp
,`updated_at` timestamp
,`created_by` varchar(36)
,`updated_by` varchar(36)
,`notes` text
,`pharmacy_name` varchar(255)
,`pharmacy_wallet` varchar(42)
,`pharmacy_address` varchar(255)
,`batch_status` enum('DELIVERED','IN_TRANSIT','MANUFACTURED','SOLD')
,`manufacturer_address` varchar(42)
,`days_to_expiry` int(7)
,`alert_status` varchar(13)
);

-- --------------------------------------------------------

--
-- Cấu trúc đóng vai cho view `v_shipment_history`
-- (See below for the actual view)
--
CREATE TABLE `v_shipment_history` (
`shipment_code` varchar(100)
,`batch_id` decimal(38,0)
,`drug_name` varchar(255)
,`batch_number` varchar(100)
,`from_company` varchar(255)
,`to_company` varchar(255)
,`quantity` int(11)
,`shipment_status` enum('PENDING','IN_TRANSIT','DELIVERED','CANCELLED')
,`shipment_date` timestamp
,`expected_delivery_date` timestamp
,`actual_delivery_date` timestamp
);

-- --------------------------------------------------------

--
-- Cấu trúc cho view `recent_diagnoses_summary`
--
DROP TABLE IF EXISTS `recent_diagnoses_summary`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `recent_diagnoses_summary`  AS SELECT `ad`.`user_id` AS `user_id`, `ad`.`session_id` AS `session_id`, `dc`.`name` AS `primary_diagnosis`, `ad`.`primary_confidence` AS `primary_confidence`, `ad`.`urgency_level` AS `urgency_level`, `ad`.`created_at` AS `created_at`, count(`usr`.`symptom_id`) AS `symptoms_count` FROM ((`ai_diagnoses` `ad` join `disease_categories` `dc` on(`ad`.`primary_diagnosis_id` = `dc`.`id`)) left join `user_symptom_reports` `usr` on(`ad`.`session_id` = `usr`.`session_id`)) WHERE `ad`.`created_at` >= current_timestamp() - interval 30 day GROUP BY `ad`.`id` ORDER BY `ad`.`created_at` DESC ;

-- --------------------------------------------------------

--
-- Cấu trúc cho view `user_health_profiles`
--
DROP TABLE IF EXISTS `user_health_profiles`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `user_health_profiles`  AS SELECT `u`.`id` AS `user_id`, `u`.`email` AS `email`, `u`.`name` AS `name`, `ud`.`birth_year` AS `birth_year`, `ud`.`gender` AS `gender`, `ud`.`height_cm` AS `height_cm`, `ud`.`weight_kg` AS `weight_kg`, `ud`.`blood_type` AS `blood_type`, `p`.`name` AS `province_name`, `p`.`region` AS `region`, `ul`.`smoking_status` AS `smoking_status`, `ul`.`alcohol_frequency` AS `alcohol_frequency`, `ul`.`exercise_frequency` AS `exercise_frequency`, count(distinct `ucd`.`disease_id`) AS `chronic_disease_count`, count(distinct `um`.`medication_id`) AS `active_medication_count`, count(distinct `ua`.`allergen_id`) AS `allergy_count` FROM ((((((`users` `u` left join `user_demographics` `ud` on(`u`.`id` = `ud`.`user_id`)) left join `provinces` `p` on(`ud`.`province_id` = `p`.`id`)) left join `user_lifestyle` `ul` on(`u`.`id` = `ul`.`user_id`)) left join `user_chronic_diseases` `ucd` on(`u`.`id` = `ucd`.`user_id` and `ucd`.`current_status` = 'active')) left join `user_medications` `um` on(`u`.`id` = `um`.`user_id` and `um`.`is_active` = 1)) left join `user_allergies` `ua` on(`u`.`id` = `ua`.`user_id` and `ua`.`is_active` = 1)) GROUP BY `u`.`id` ;

-- --------------------------------------------------------

--
-- Cấu trúc cho view `v_batch_status`
--
DROP TABLE IF EXISTS `v_batch_status`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_batch_status`  AS SELECT `db`.`batch_id` AS `batch_id`, `db`.`drug_name` AS `drug_name`, `db`.`batch_number` AS `batch_number`, `db`.`manufacturer` AS `manufacturer`, `db`.`quantity` AS `quantity`, `db`.`status` AS `status`, `db`.`expiry_date` AS `expiry_date`, CASE WHEN `db`.`expiry_date` < current_timestamp() THEN 'EXPIRED' WHEN to_days(`db`.`expiry_date`) - to_days(current_timestamp()) <= 90 THEN 'EXPIRING_SOON' ELSE 'VALID' END AS `validity_status`, `pc`.`name` AS `current_owner_name` FROM (`drug_batches` `db` left join `pharma_companies` `pc` on(`db`.`current_owner` = `pc`.`wallet_address`)) ;

-- --------------------------------------------------------

--
-- Cấu trúc cho view `v_blockchain_overview`
--
DROP TABLE IF EXISTS `v_blockchain_overview`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_blockchain_overview`  AS SELECT `bt`.`transaction_hash` AS `transaction_hash`, `bt`.`function_name` AS `function_name`, `bt`.`from_address` AS `from_address`, `bt`.`to_address` AS `to_address`, `bt`.`status` AS `status`, `bt`.`gas_used` AS `gas_used`, `bt`.`timestamp` AS `timestamp`, `db`.`drug_name` AS `batch_drug_name`, `ds`.`shipment_code` AS `shipment_code` FROM ((`blockchain_transactions` `bt` left join `drug_batches` `db` on(`bt`.`batch_id` = `db`.`id`)) left join `drug_shipments` `ds` on(`bt`.`shipment_id` = `ds`.`id`)) ORDER BY `bt`.`timestamp` DESC ;

-- --------------------------------------------------------

--
-- Cấu trúc cho view `v_company_users`
--
DROP TABLE IF EXISTS `v_company_users`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_company_users`  AS SELECT `pc`.`id` AS `company_id`, `pc`.`name` AS `company_name`, `pc`.`company_type` AS `company_type`, `pc`.`wallet_address` AS `wallet_address`, `pc`.`license_number` AS `license_number`, coalesce(`du`.`email`,`mu`.`email`) AS `user_email`, coalesce(`du`.`name`,`mu`.`name`) AS `user_name`, CASE WHEN `du`.`id` is not null THEN 'DISTRIBUTOR' WHEN `mu`.`id` is not null THEN 'MANUFACTURER' ELSE NULL END AS `user_type` FROM ((`pharma_companies` `pc` left join `distributor_users` `du` on(`pc`.`wallet_address` = `du`.`wallet_address`)) left join `manufacturer_users` `mu` on(`pc`.`wallet_address` = `mu`.`wallet_address`)) ;

-- --------------------------------------------------------

--
-- Cấu trúc cho view `v_distributor_inventory_full`
--
DROP TABLE IF EXISTS `v_distributor_inventory_full`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_distributor_inventory_full`  AS SELECT `di`.`id` AS `id`, `di`.`distributor_id` AS `distributor_id`, `di`.`batch_id` AS `batch_id`, `di`.`drug_name` AS `drug_name`, `di`.`manufacturer` AS `manufacturer`, `di`.`batch_number` AS `batch_number`, `di`.`quantity` AS `quantity`, `di`.`reserved_quantity` AS `reserved_quantity`, `di`.`available_quantity` AS `available_quantity`, `di`.`manufacture_date` AS `manufacture_date`, `di`.`expiry_date` AS `expiry_date`, `di`.`qr_code` AS `qr_code`, `di`.`warehouse_location` AS `warehouse_location`, `di`.`storage_conditions` AS `storage_conditions`, `di`.`storage_temperature` AS `storage_temperature`, `di`.`unit_price` AS `unit_price`, `di`.`selling_price` AS `selling_price`, `di`.`total_value` AS `total_value`, `di`.`status` AS `status`, `di`.`min_stock_level` AS `min_stock_level`, `di`.`max_stock_level` AS `max_stock_level`, `di`.`blockchain_batch_id` AS `blockchain_batch_id`, `di`.`receive_tx_hash` AS `receive_tx_hash`, `di`.`current_owner_address` AS `current_owner_address`, `di`.`received_from_company_id` AS `received_from_company_id`, `di`.`received_shipment_id` AS `received_shipment_id`, `di`.`received_date` AS `received_date`, `di`.`received_quantity` AS `received_quantity`, `di`.`created_at` AS `created_at`, `di`.`updated_at` AS `updated_at`, `di`.`created_by` AS `created_by`, `di`.`updated_by` AS `updated_by`, `di`.`notes` AS `notes`, `pc`.`name` AS `distributor_name`, `pc`.`wallet_address` AS `distributor_wallet`, `db`.`status` AS `batch_status`, `db`.`manufacturer_address` AS `manufacturer_address`, to_days(`di`.`expiry_date`) - to_days(current_timestamp()) AS `days_to_expiry`, CASE WHEN `di`.`available_quantity` <= `di`.`min_stock_level` THEN 'NEED_REORDER' WHEN to_days(`di`.`expiry_date`) - to_days(current_timestamp()) <= 30 THEN 'EXPIRING_SOON' ELSE 'NORMAL' END AS `alert_status` FROM ((`distributor_inventory` `di` join `pharma_companies` `pc` on(`di`.`distributor_id` = `pc`.`id`)) join `drug_batches` `db` on(`di`.`batch_id` = `db`.`id`)) WHERE `pc`.`company_type` = 'DISTRIBUTOR' ;

-- --------------------------------------------------------

--
-- Cấu trúc cho view `v_pharmacy_inventory_full`
--
DROP TABLE IF EXISTS `v_pharmacy_inventory_full`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_pharmacy_inventory_full`  AS SELECT `pi`.`id` AS `id`, `pi`.`pharmacy_id` AS `pharmacy_id`, `pi`.`batch_id` AS `batch_id`, `pi`.`drug_name` AS `drug_name`, `pi`.`manufacturer` AS `manufacturer`, `pi`.`batch_number` AS `batch_number`, `pi`.`quantity` AS `quantity`, `pi`.`reserved_quantity` AS `reserved_quantity`, `pi`.`available_quantity` AS `available_quantity`, `pi`.`sold_quantity` AS `sold_quantity`, `pi`.`manufacture_date` AS `manufacture_date`, `pi`.`expiry_date` AS `expiry_date`, `pi`.`qr_code` AS `qr_code`, `pi`.`shelf_location` AS `shelf_location`, `pi`.`storage_conditions` AS `storage_conditions`, `pi`.`storage_temperature` AS `storage_temperature`, `pi`.`cost_price` AS `cost_price`, `pi`.`retail_price` AS `retail_price`, `pi`.`discount_price` AS `discount_price`, `pi`.`total_value` AS `total_value`, `pi`.`profit_margin` AS `profit_margin`, `pi`.`status` AS `status`, `pi`.`min_stock_level` AS `min_stock_level`, `pi`.`max_stock_level` AS `max_stock_level`, `pi`.`reorder_point` AS `reorder_point`, `pi`.`blockchain_batch_id` AS `blockchain_batch_id`, `pi`.`receive_tx_hash` AS `receive_tx_hash`, `pi`.`current_owner_address` AS `current_owner_address`, `pi`.`is_verified` AS `is_verified`, `pi`.`received_from_distributor_id` AS `received_from_distributor_id`, `pi`.`received_shipment_id` AS `received_shipment_id`, `pi`.`received_date` AS `received_date`, `pi`.`received_quantity` AS `received_quantity`, `pi`.`first_sale_date` AS `first_sale_date`, `pi`.`last_sale_date` AS `last_sale_date`, `pi`.`average_daily_sales` AS `average_daily_sales`, `pi`.`days_of_supply` AS `days_of_supply`, `pi`.`requires_prescription` AS `requires_prescription`, `pi`.`controlled_substance` AS `controlled_substance`, `pi`.`is_featured` AS `is_featured`, `pi`.`is_on_sale` AS `is_on_sale`, `pi`.`display_order` AS `display_order`, `pi`.`created_at` AS `created_at`, `pi`.`updated_at` AS `updated_at`, `pi`.`created_by` AS `created_by`, `pi`.`updated_by` AS `updated_by`, `pi`.`notes` AS `notes`, `pc`.`name` AS `pharmacy_name`, `pc`.`wallet_address` AS `pharmacy_wallet`, `pc`.`address` AS `pharmacy_address`, `db`.`status` AS `batch_status`, `db`.`manufacturer_address` AS `manufacturer_address`, to_days(`pi`.`expiry_date`) - to_days(current_timestamp()) AS `days_to_expiry`, CASE WHEN `pi`.`available_quantity` <= 0 THEN 'OUT_OF_STOCK' WHEN `pi`.`available_quantity` <= `pi`.`reorder_point` THEN 'NEED_REORDER' WHEN to_days(`pi`.`expiry_date`) - to_days(current_timestamp()) <= 30 THEN 'EXPIRING_SOON' ELSE 'NORMAL' END AS `alert_status` FROM ((`pharmacy_inventory` `pi` join `pharma_companies` `pc` on(`pi`.`pharmacy_id` = `pc`.`id`)) join `drug_batches` `db` on(`pi`.`batch_id` = `db`.`id`)) WHERE `pc`.`company_type` = 'PHARMACY' ;

-- --------------------------------------------------------

--
-- Cấu trúc cho view `v_shipment_history`
--
DROP TABLE IF EXISTS `v_shipment_history`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_shipment_history`  AS SELECT `ds`.`shipment_code` AS `shipment_code`, `db`.`batch_id` AS `batch_id`, `db`.`drug_name` AS `drug_name`, `db`.`batch_number` AS `batch_number`, `fc`.`name` AS `from_company`, `tc`.`name` AS `to_company`, `ds`.`quantity` AS `quantity`, `ds`.`shipment_status` AS `shipment_status`, `ds`.`shipment_date` AS `shipment_date`, `ds`.`expected_delivery_date` AS `expected_delivery_date`, `ds`.`actual_delivery_date` AS `actual_delivery_date` FROM (((`drug_shipments` `ds` join `drug_batches` `db` on(`ds`.`batch_id` = `db`.`id`)) join `pharma_companies` `fc` on(`ds`.`from_company_id` = `fc`.`id`)) join `pharma_companies` `tc` on(`ds`.`to_company_id` = `tc`.`id`)) ;

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `ai_diagnoses`
--
ALTER TABLE `ai_diagnoses`
  ADD PRIMARY KEY (`id`),
  ADD KEY `primary_diagnosis_id` (`primary_diagnosis_id`),
  ADD KEY `recommended_specialty_id` (`recommended_specialty_id`),
  ADD KEY `idx_diagnoses_user_id` (`user_id`),
  ADD KEY `idx_diagnoses_session` (`session_id`),
  ADD KEY `idx_diagnoses_urgency` (`urgency_level`),
  ADD KEY `idx_diagnoses_date` (`created_at`),
  ADD KEY `idx_ai_diagnoses_composite` (`user_id`,`urgency_level`,`created_at`);

--
-- Chỉ mục cho bảng `allergen_categories`
--
ALTER TABLE `allergen_categories`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_allergen_category` (`category`),
  ADD KEY `idx_allergen_name` (`name`);

--
-- Chỉ mục cho bảng `blockchain_config`
--
ALTER TABLE `blockchain_config`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `config_key` (`config_key`),
  ADD KEY `idx_config_key` (`config_key`),
  ADD KEY `idx_is_active` (`is_active`);

--
-- Chỉ mục cho bảng `blockchain_events`
--
ALTER TABLE `blockchain_events`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UKmy081fpj6u877vqk9jv516sr4` (`transaction_hash`),
  ADD KEY `idx_block_number` (`block_number`),
  ADD KEY `idx_transaction_hash` (`transaction_hash`),
  ADD KEY `idx_event_type` (`event_type`),
  ADD KEY `idx_transaction_hash_be` (`transaction_hash`);

--
-- Chỉ mục cho bảng `blockchain_transactions`
--
ALTER TABLE `blockchain_transactions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UKp634ahad8pjht0rqxixrykeu4` (`transaction_hash`),
  ADD UNIQUE KEY `idx_transaction_hash` (`transaction_hash`),
  ADD KEY `idx_from_address` (`from_address`),
  ADD KEY `idx_batch_id` (`batch_id`),
  ADD KEY `idx_shipment_id` (`shipment_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_composite_status_timestamp` (`status`,`timestamp`),
  ADD KEY `idx_from_address_bt` (`from_address`),
  ADD KEY `idx_batch_id_bt` (`batch_id`),
  ADD KEY `idx_shipment_id_bt` (`shipment_id`),
  ADD KEY `idx_status_bt` (`status`);

--
-- Chỉ mục cho bảng `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_chat_messages_session` (`session_id`),
  ADD KEY `idx_chat_messages_order` (`session_id`,`message_order`),
  ADD KEY `idx_chat_messages_sender` (`sender`),
  ADD KEY `idx_chat_messages_composite` (`session_id`,`message_order`,`sender`);

--
-- Chỉ mục cho bảng `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_chat_sessions_user_id` (`user_id`),
  ADD KEY `idx_chat_sessions_type` (`session_type`),
  ADD KEY `idx_chat_sessions_date` (`started_at`);

--
-- Chỉ mục cho bảng `disease_categories`
--
ALTER TABLE `disease_categories`
  ADD PRIMARY KEY (`id`),
  ADD KEY `specialty_id` (`specialty_id`),
  ADD KEY `idx_disease_icd10` (`icd10_code`),
  ADD KEY `idx_disease_chronic` (`is_chronic`),
  ADD KEY `idx_disease_severity` (`severity_level`);
ALTER TABLE `disease_categories` ADD FULLTEXT KEY `name` (`name`,`description`);

--
-- Chỉ mục cho bảng `distributor_inventory`
--
ALTER TABLE `distributor_inventory`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_distributor_batch` (`distributor_id`,`batch_id`),
  ADD KEY `idx_distributor_id` (`distributor_id`),
  ADD KEY `idx_batch_id` (`batch_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_expiry_date` (`expiry_date`),
  ADD KEY `idx_available_quantity` (`available_quantity`),
  ADD KEY `fk_dist_inv_received_from` (`received_from_company_id`),
  ADD KEY `fk_dist_inv_shipment` (`received_shipment_id`);

--
-- Chỉ mục cho bảng `distributor_users`
--
ALTER TABLE `distributor_users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UKmpvt4be3vwqcoed0ovvdh7jil` (`email`),
  ADD UNIQUE KEY `idx_email` (`email`),
  ADD UNIQUE KEY `idx_email_dist` (`email`),
  ADD UNIQUE KEY `unique_distributor_wallet` (`wallet_address`),
  ADD KEY `idx_wallet_address` (`wallet_address`),
  ADD KEY `idx_wallet_address_dist` (`wallet_address`);

--
-- Chỉ mục cho bảng `drug_batches`
--
ALTER TABLE `drug_batches`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UKt9md736g9fj8cosy0i1ewwaop` (`batch_id`),
  ADD KEY `idx_batch_id` (`batch_id`),
  ADD KEY `idx_qr_code` (`qr_code`(100)),
  ADD KEY `idx_manufacturer_address` (`manufacturer_address`),
  ADD KEY `idx_current_owner` (`current_owner`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_composite_status_expiry` (`status`,`expiry_date`);

--
-- Chỉ mục cho bảng `drug_products`
--
ALTER TABLE `drug_products`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_drug_products_manufacturer` (`manufacturer_id`),
  ADD KEY `idx_drug_products_name` (`name`),
  ADD KEY `idx_drug_products_category` (`category`),
  ADD KEY `idx_drug_products_active` (`is_active`),
  ADD KEY `idx_drug_products_manufacturer_id` (`manufacturer_id`),
  ADD KEY `idx_manufacturer_id` (`manufacturer_id`),
  ADD KEY `idx_registration_number` (`registration_number`);
ALTER TABLE `drug_products` ADD FULLTEXT KEY `name` (`name`,`active_ingredient`,`description`);
ALTER TABLE `drug_products` ADD FULLTEXT KEY `name_2` (`name`,`active_ingredient`,`description`);

--
-- Chỉ mục cho bảng `drug_shipments`
--
ALTER TABLE `drug_shipments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `shipment_code` (`shipment_code`),
  ADD UNIQUE KEY `idx_shipment_code` (`shipment_code`),
  ADD KEY `idx_drug_shipments_batch` (`batch_id`),
  ADD KEY `idx_drug_shipments_from` (`from_company_id`),
  ADD KEY `idx_drug_shipments_to` (`to_company_id`),
  ADD KEY `idx_drug_shipments_status` (`shipment_status`),
  ADD KEY `idx_drug_shipments_batch_id` (`batch_id`),
  ADD KEY `idx_drug_shipments_from_company` (`from_company_id`),
  ADD KEY `idx_drug_shipments_to_company` (`to_company_id`),
  ADD KEY `idx_drug_shipments_shipment_date` (`shipment_date`),
  ADD KEY `idx_drug_shipments_shipment_code` (`shipment_code`),
  ADD KEY `idx_batch_id` (`batch_id`),
  ADD KEY `idx_from_company` (`from_company_id`),
  ADD KEY `idx_to_company` (`to_company_id`),
  ADD KEY `idx_shipment_status` (`shipment_status`),
  ADD KEY `idx_composite_status_date` (`shipment_status`,`shipment_date`),
  ADD KEY `idx_batch_id_shipments` (`batch_id`);

--
-- Chỉ mục cho bảng `drug_verification_records`
--
ALTER TABLE `drug_verification_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_verification_records_batch` (`batch_id`),
  ADD KEY `idx_verification_records_company` (`verified_by_company_id`),
  ADD KEY `idx_verification_records_date` (`verification_date`),
  ADD KEY `idx_verification_records_type` (`verification_type`),
  ADD KEY `idx_verification_records_authentic` (`is_authentic`),
  ADD KEY `idx_verification_records_composite` (`batch_id`,`verification_date`,`is_authentic`),
  ADD KEY `idx_batch_id` (`batch_id`),
  ADD KEY `idx_verification_date` (`verification_date`),
  ADD KEY `idx_is_authentic` (`is_authentic`),
  ADD KEY `idx_batch_id_dvr` (`batch_id`);

--
-- Chỉ mục cho bảng `inventory_movements`
--
ALTER TABLE `inventory_movements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_inventory_type_id` (`inventory_type`,`inventory_id`),
  ADD KEY `idx_movement_type` (`movement_type`),
  ADD KEY `idx_movement_date` (`movement_date`),
  ADD KEY `idx_related_shipment` (`related_shipment_id`);

--
-- Chỉ mục cho bảng `manufacturer_users`
--
ALTER TABLE `manufacturer_users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UK95h07q846p7dv5v8l5epve0vs` (`email`),
  ADD UNIQUE KEY `idx_email` (`email`),
  ADD UNIQUE KEY `idx_email_manu` (`email`),
  ADD UNIQUE KEY `unique_manufacturer_wallet` (`wallet_address`),
  ADD KEY `idx_manufacturer_user_email` (`email`),
  ADD KEY `idx_manufacturer_user_wallet_address` (`wallet_address`),
  ADD KEY `idx_manufacturer_user_role` (`role`),
  ADD KEY `idx_wallet_address` (`wallet_address`),
  ADD KEY `idx_wallet_address_manu` (`wallet_address`);

--
-- Chỉ mục cho bảng `medical_specialties`
--
ALTER TABLE `medical_specialties`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `parent_specialty_id` (`parent_specialty_id`);

--
-- Chỉ mục cho bảng `medications`
--
ALTER TABLE `medications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_medication_name` (`name`),
  ADD KEY `idx_medication_generic` (`generic_name`),
  ADD KEY `idx_medication_class` (`drug_class`);
ALTER TABLE `medications` ADD FULLTEXT KEY `name` (`name`,`generic_name`);

--
-- Chỉ mục cho bảng `ml_model_performance`
--
ALTER TABLE `ml_model_performance`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_ml_performance_model` (`model_name`,`model_version`),
  ADD KEY `idx_ml_performance_date` (`evaluation_date`);

--
-- Chỉ mục cho bảng `news_articles`
--
ALTER TABLE `news_articles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `FKke29j5hkg9i08d4a8lhb48q6p` (`primary_category_id`);

--
-- Chỉ mục cho bảng `ownership_history`
--
ALTER TABLE `ownership_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_ownership_history_batch` (`batch_id`),
  ADD KEY `idx_ownership_history_tx_hash` (`blockchain_tx_hash`),
  ADD KEY `idx_ownership_history_transfer_date` (`transfer_date`),
  ADD KEY `idx_ownership_history_from` (`from_company_id`),
  ADD KEY `idx_ownership_history_to` (`to_company_id`),
  ADD KEY `idx_ownership_history_composite` (`batch_id`,`transfer_date`,`transfer_type`),
  ADD KEY `idx_batch_id` (`batch_id`),
  ADD KEY `idx_transfer_date` (`transfer_date`),
  ADD KEY `idx_blockchain_tx_hash` (`blockchain_tx_hash`),
  ADD KEY `idx_batch_id_oh` (`batch_id`);

--
-- Chỉ mục cho bảng `pharmacy_inventory`
--
ALTER TABLE `pharmacy_inventory`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_pharmacy_batch` (`pharmacy_id`,`batch_id`),
  ADD KEY `idx_pharmacy_id` (`pharmacy_id`),
  ADD KEY `idx_batch_id` (`batch_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_expiry_date` (`expiry_date`),
  ADD KEY `idx_available_quantity` (`available_quantity`),
  ADD KEY `idx_drug_name` (`drug_name`),
  ADD KEY `idx_is_featured` (`is_featured`),
  ADD KEY `fk_pharm_inv_distributor` (`received_from_distributor_id`),
  ADD KEY `fk_pharm_inv_shipment` (`received_shipment_id`);

--
-- Chỉ mục cho bảng `pharmacy_users`
--
ALTER TABLE `pharmacy_users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `pharmacy_code` (`pharmacy_code`),
  ADD UNIQUE KEY `wallet_address` (`wallet_address`),
  ADD KEY `idx_email` (`email`),
  ADD KEY `idx_wallet_address` (`wallet_address`),
  ADD KEY `idx_pharmacy_code` (`pharmacy_code`);

--
-- Chỉ mục cho bảng `pharma_companies`
--
ALTER TABLE `pharma_companies`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `license_number` (`license_number`),
  ADD UNIQUE KEY `wallet_address` (`wallet_address`),
  ADD UNIQUE KEY `wallet_address_2` (`wallet_address`),
  ADD UNIQUE KEY `wallet_address_3` (`wallet_address`),
  ADD KEY `idx_pharma_companies_type` (`company_type`),
  ADD KEY `idx_pharma_companies_wallet` (`wallet_address`),
  ADD KEY `idx_pharma_companies_license` (`license_number`),
  ADD KEY `idx_pharma_companies_active` (`is_active`),
  ADD KEY `idx_company_type` (`company_type`),
  ADD KEY `idx_wallet_address` (`wallet_address`);
ALTER TABLE `pharma_companies` ADD FULLTEXT KEY `name` (`name`,`address`);
ALTER TABLE `pharma_companies` ADD FULLTEXT KEY `name_2` (`name`,`address`);

--
-- Chỉ mục cho bảng `provinces`
--
ALTER TABLE `provinces`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Chỉ mục cho bảng `symptoms`
--
ALTER TABLE `symptoms`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_symptom_category` (`category`),
  ADD KEY `idx_symptom_name` (`name`);
ALTER TABLE `symptoms` ADD FULLTEXT KEY `name` (`name`,`category`);

--
-- Chỉ mục cho bảng `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Chỉ mục cho bảng `user_allergies`
--
ALTER TABLE `user_allergies`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_allergen` (`user_id`,`allergen_id`),
  ADD UNIQUE KEY `UKlpfcepd1quxrwrg1iso3rbtol` (`user_id`,`allergen_id`),
  ADD KEY `allergen_id` (`allergen_id`),
  ADD KEY `idx_user_allergies_user_id` (`user_id`),
  ADD KEY `idx_user_allergies_severity` (`severity`);

--
-- Chỉ mục cho bảng `user_analytics`
--
ALTER TABLE `user_analytics`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_date` (`user_id`,`session_date`),
  ADD UNIQUE KEY `UK7mdo9lpckgwptue7g6mcadpbt` (`user_id`,`session_date`),
  ADD KEY `idx_analytics_user_id` (`user_id`),
  ADD KEY `idx_analytics_date` (`session_date`);

--
-- Chỉ mục cho bảng `user_blockchain_addresses`
--
ALTER TABLE `user_blockchain_addresses`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_address_type` (`user_id`,`address_type`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_blockchain_address` (`blockchain_address`),
  ADD KEY `idx_address_type` (`address_type`),
  ADD KEY `idx_is_verified` (`is_verified`);

--
-- Chỉ mục cho bảng `user_chronic_diseases`
--
ALTER TABLE `user_chronic_diseases`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_disease` (`user_id`,`disease_id`),
  ADD UNIQUE KEY `UK8sygvsr1aj77insmjtoxe1slp` (`user_id`,`disease_id`),
  ADD KEY `disease_id` (`disease_id`),
  ADD KEY `idx_user_diseases_user_id` (`user_id`),
  ADD KEY `idx_user_diseases_status` (`current_status`),
  ADD KEY `idx_user_chronic_diseases_composite` (`user_id`,`current_status`,`severity_current`);

--
-- Chỉ mục cho bảng `user_demographics`
--
ALTER TABLE `user_demographics`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `idx_demographics_user_id` (`user_id`),
  ADD KEY `idx_demographics_age` (`birth_year`),
  ADD KEY `idx_demographics_gender` (`gender`),
  ADD KEY `province_id` (`province_id`);

--
-- Chỉ mục cho bảng `user_family_history`
--
ALTER TABLE `user_family_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `disease_id` (`disease_id`),
  ADD KEY `cause_of_death` (`cause_of_death`),
  ADD KEY `idx_family_history_user_id` (`user_id`),
  ADD KEY `idx_family_history_relationship` (`relationship`);

--
-- Chỉ mục cho bảng `user_lifestyle`
--
ALTER TABLE `user_lifestyle`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `idx_lifestyle_user_id` (`user_id`),
  ADD KEY `idx_lifestyle_smoking` (`smoking_status`),
  ADD KEY `idx_lifestyle_exercise` (`exercise_frequency`);

--
-- Chỉ mục cho bảng `user_medications`
--
ALTER TABLE `user_medications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `medication_id` (`medication_id`),
  ADD KEY `idx_user_meds_user_id` (`user_id`),
  ADD KEY `idx_user_meds_active` (`is_active`),
  ADD KEY `idx_user_meds_dates` (`start_date`,`end_date`),
  ADD KEY `idx_user_medications_composite` (`user_id`,`is_active`,`start_date`);

--
-- Chỉ mục cho bảng `user_news_interactions`
--
ALTER TABLE `user_news_interactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `FKnwx3trc1fnawwofdugamsshbl` (`article_id`),
  ADD KEY `FKnnnrc539o3ogkp37dg6b4acs8` (`user_id`);

--
-- Chỉ mục cho bảng `user_symptom_reports`
--
ALTER TABLE `user_symptom_reports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `symptom_id` (`symptom_id`),
  ADD KEY `idx_symptom_reports_user_id` (`user_id`),
  ADD KEY `idx_symptom_reports_session` (`session_id`),
  ADD KEY `idx_symptom_reports_date` (`reported_at`),
  ADD KEY `idx_symptom_reports_composite` (`user_id`,`session_id`,`reported_at`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `ai_diagnoses`
--
ALTER TABLE `ai_diagnoses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `allergen_categories`
--
ALTER TABLE `allergen_categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `blockchain_config`
--
ALTER TABLE `blockchain_config`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT cho bảng `blockchain_events`
--
ALTER TABLE `blockchain_events`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `blockchain_transactions`
--
ALTER TABLE `blockchain_transactions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT cho bảng `chat_messages`
--
ALTER TABLE `chat_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT cho bảng `disease_categories`
--
ALTER TABLE `disease_categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `distributor_inventory`
--
ALTER TABLE `distributor_inventory`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT cho bảng `drug_batches`
--
ALTER TABLE `drug_batches`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `drug_products`
--
ALTER TABLE `drug_products`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT cho bảng `drug_shipments`
--
ALTER TABLE `drug_shipments`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `drug_verification_records`
--
ALTER TABLE `drug_verification_records`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `inventory_movements`
--
ALTER TABLE `inventory_movements`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `medical_specialties`
--
ALTER TABLE `medical_specialties`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT cho bảng `medications`
--
ALTER TABLE `medications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=233;

--
-- AUTO_INCREMENT cho bảng `ml_model_performance`
--
ALTER TABLE `ml_model_performance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `news_articles`
--
ALTER TABLE `news_articles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `ownership_history`
--
ALTER TABLE `ownership_history`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT cho bảng `pharmacy_inventory`
--
ALTER TABLE `pharmacy_inventory`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT cho bảng `pharmacy_users`
--
ALTER TABLE `pharmacy_users`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT cho bảng `pharma_companies`
--
ALTER TABLE `pharma_companies`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT cho bảng `provinces`
--
ALTER TABLE `provinces`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=64;

--
-- AUTO_INCREMENT cho bảng `symptoms`
--
ALTER TABLE `symptoms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_allergies`
--
ALTER TABLE `user_allergies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_analytics`
--
ALTER TABLE `user_analytics`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_blockchain_addresses`
--
ALTER TABLE `user_blockchain_addresses`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_chronic_diseases`
--
ALTER TABLE `user_chronic_diseases`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_demographics`
--
ALTER TABLE `user_demographics`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT cho bảng `user_family_history`
--
ALTER TABLE `user_family_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_lifestyle`
--
ALTER TABLE `user_lifestyle`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT cho bảng `user_medications`
--
ALTER TABLE `user_medications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_news_interactions`
--
ALTER TABLE `user_news_interactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `user_symptom_reports`
--
ALTER TABLE `user_symptom_reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `ai_diagnoses`
--
ALTER TABLE `ai_diagnoses`
  ADD CONSTRAINT `ai_diagnoses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `ai_diagnoses_ibfk_2` FOREIGN KEY (`primary_diagnosis_id`) REFERENCES `disease_categories` (`id`),
  ADD CONSTRAINT `ai_diagnoses_ibfk_3` FOREIGN KEY (`recommended_specialty_id`) REFERENCES `medical_specialties` (`id`);

--
-- Các ràng buộc cho bảng `blockchain_transactions`
--
ALTER TABLE `blockchain_transactions`
  ADD CONSTRAINT `FK1xwa92xkjqy4m4w86qt9frq0p` FOREIGN KEY (`batch_id`) REFERENCES `drug_batches` (`id`),
  ADD CONSTRAINT `FKthjbaitcky21e87g7k64ixmyu` FOREIGN KEY (`shipment_id`) REFERENCES `shipments_old_backup` (`id`);

--
-- Các ràng buộc cho bảng `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `chat_sessions` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD CONSTRAINT `chat_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `disease_categories`
--
ALTER TABLE `disease_categories`
  ADD CONSTRAINT `disease_categories_ibfk_1` FOREIGN KEY (`specialty_id`) REFERENCES `medical_specialties` (`id`);

--
-- Các ràng buộc cho bảng `distributor_inventory`
--
ALTER TABLE `distributor_inventory`
  ADD CONSTRAINT `fk_dist_inv_batch` FOREIGN KEY (`batch_id`) REFERENCES `drug_batches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_dist_inv_distributor` FOREIGN KEY (`distributor_id`) REFERENCES `pharma_companies` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_dist_inv_received_from` FOREIGN KEY (`received_from_company_id`) REFERENCES `pharma_companies` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_dist_inv_shipment` FOREIGN KEY (`received_shipment_id`) REFERENCES `drug_shipments` (`id`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `drug_products`
--
ALTER TABLE `drug_products`
  ADD CONSTRAINT `drug_products_ibfk_1` FOREIGN KEY (`manufacturer_id`) REFERENCES `pharma_companies` (`id`);

--
-- Các ràng buộc cho bảng `drug_shipments`
--
ALTER TABLE `drug_shipments`
  ADD CONSTRAINT `FKijrigymbgnkf344fc6dv25swr` FOREIGN KEY (`batch_id`) REFERENCES `drug_batches` (`id`),
  ADD CONSTRAINT `fk_drug_shipments_batch` FOREIGN KEY (`batch_id`) REFERENCES `drug_batches` (`id`) ON UPDATE CASCADE;

--
-- Các ràng buộc cho bảng `drug_verification_records`
--
ALTER TABLE `drug_verification_records`
  ADD CONSTRAINT `drug_verification_records_ibfk_1` FOREIGN KEY (`batch_id`) REFERENCES `drug_batches` (`id`),
  ADD CONSTRAINT `drug_verification_records_ibfk_2` FOREIGN KEY (`verified_by_company_id`) REFERENCES `pharma_companies` (`id`);

--
-- Các ràng buộc cho bảng `inventory_movements`
--
ALTER TABLE `inventory_movements`
  ADD CONSTRAINT `fk_inv_mov_shipment` FOREIGN KEY (`related_shipment_id`) REFERENCES `drug_shipments` (`id`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `medical_specialties`
--
ALTER TABLE `medical_specialties`
  ADD CONSTRAINT `medical_specialties_ibfk_1` FOREIGN KEY (`parent_specialty_id`) REFERENCES `medical_specialties` (`id`);

--
-- Các ràng buộc cho bảng `news_articles`
--
ALTER TABLE `news_articles`
  ADD CONSTRAINT `FKke29j5hkg9i08d4a8lhb48q6p` FOREIGN KEY (`primary_category_id`) REFERENCES `medical_specialties` (`id`);

--
-- Các ràng buộc cho bảng `ownership_history`
--
ALTER TABLE `ownership_history`
  ADD CONSTRAINT `ownership_history_ibfk_1` FOREIGN KEY (`batch_id`) REFERENCES `drug_batches` (`id`),
  ADD CONSTRAINT `ownership_history_ibfk_2` FOREIGN KEY (`from_company_id`) REFERENCES `pharma_companies` (`id`),
  ADD CONSTRAINT `ownership_history_ibfk_3` FOREIGN KEY (`to_company_id`) REFERENCES `pharma_companies` (`id`);

--
-- Các ràng buộc cho bảng `pharmacy_inventory`
--
ALTER TABLE `pharmacy_inventory`
  ADD CONSTRAINT `fk_pharm_inv_batch` FOREIGN KEY (`batch_id`) REFERENCES `drug_batches` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_pharm_inv_distributor` FOREIGN KEY (`received_from_distributor_id`) REFERENCES `pharma_companies` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_pharm_inv_pharmacy` FOREIGN KEY (`pharmacy_id`) REFERENCES `pharma_companies` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_pharm_inv_shipment` FOREIGN KEY (`received_shipment_id`) REFERENCES `drug_shipments` (`id`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `user_allergies`
--
ALTER TABLE `user_allergies`
  ADD CONSTRAINT `user_allergies_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_allergies_ibfk_2` FOREIGN KEY (`allergen_id`) REFERENCES `allergen_categories` (`id`);

--
-- Các ràng buộc cho bảng `user_analytics`
--
ALTER TABLE `user_analytics`
  ADD CONSTRAINT `user_analytics_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `user_blockchain_addresses`
--
ALTER TABLE `user_blockchain_addresses`
  ADD CONSTRAINT `user_blockchain_addresses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `user_chronic_diseases`
--
ALTER TABLE `user_chronic_diseases`
  ADD CONSTRAINT `user_chronic_diseases_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_chronic_diseases_ibfk_2` FOREIGN KEY (`disease_id`) REFERENCES `disease_categories` (`id`);

--
-- Các ràng buộc cho bảng `user_demographics`
--
ALTER TABLE `user_demographics`
  ADD CONSTRAINT `user_demographics_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_demographics_ibfk_2` FOREIGN KEY (`province_id`) REFERENCES `provinces` (`id`);

--
-- Các ràng buộc cho bảng `user_family_history`
--
ALTER TABLE `user_family_history`
  ADD CONSTRAINT `user_family_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_family_history_ibfk_2` FOREIGN KEY (`disease_id`) REFERENCES `disease_categories` (`id`),
  ADD CONSTRAINT `user_family_history_ibfk_3` FOREIGN KEY (`cause_of_death`) REFERENCES `disease_categories` (`id`);

--
-- Các ràng buộc cho bảng `user_lifestyle`
--
ALTER TABLE `user_lifestyle`
  ADD CONSTRAINT `user_lifestyle_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `user_medications`
--
ALTER TABLE `user_medications`
  ADD CONSTRAINT `user_medications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_medications_ibfk_2` FOREIGN KEY (`medication_id`) REFERENCES `medications` (`id`);

--
-- Các ràng buộc cho bảng `user_news_interactions`
--
ALTER TABLE `user_news_interactions`
  ADD CONSTRAINT `FKnnnrc539o3ogkp37dg6b4acs8` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `FKnwx3trc1fnawwofdugamsshbl` FOREIGN KEY (`article_id`) REFERENCES `news_articles` (`id`);

--
-- Các ràng buộc cho bảng `user_symptom_reports`
--
ALTER TABLE `user_symptom_reports`
  ADD CONSTRAINT `user_symptom_reports_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_symptom_reports_ibfk_2` FOREIGN KEY (`symptom_id`) REFERENCES `symptoms` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
