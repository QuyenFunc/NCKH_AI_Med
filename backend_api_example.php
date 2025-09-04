<?php
// Example Backend API for Dia5 Medical App
// This is a simple PHP REST API example - you can use Node.js, Python, etc.

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Database connection
$host = 'localhost';
$dbname = 'dia5_medical_app';
$username = 'your_db_username';
$password = 'your_db_password';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database connection failed']);
    exit();
}

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = trim($path, '/');
$pathParts = explode('/', $path);

// API endpoints
switch ($pathParts[0]) {
    case 'auth':
        handleAuth($method, $pathParts, $pdo);
        break;
    case 'profile':
        handleProfile($method, $pathParts, $pdo);
        break;
    case 'news':
        handleNews($method, $pathParts, $pdo);
        break;
    case 'chat':
        handleChat($method, $pathParts, $pdo);
        break;
    default:
        http_response_code(404);
        echo json_encode(['error' => 'Endpoint not found']);
        break;
}

// Authentication endpoints
function handleAuth($method, $pathParts, $pdo) {
    if ($method === 'POST' && $pathParts[1] === 'login') {
        $input = json_decode(file_get_contents('php://input'), true);
        $email = $input['email'] ?? '';
        $password = $input['password'] ?? '';
        
        $stmt = $pdo->prepare("SELECT id, email, password_hash, name, is_profile_complete FROM users WHERE email = ?");
        $stmt->execute([$email]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if ($user && password_verify($password, $user['password_hash'])) {
            // Update last login
            $updateStmt = $pdo->prepare("UPDATE users SET last_login_at = NOW() WHERE id = ?");
            $updateStmt->execute([$user['id']]);
            
            unset($user['password_hash']);
            echo json_encode(['success' => true, 'user' => $user]);
        } else {
            http_response_code(401);
            echo json_encode(['error' => 'Invalid credentials']);
        }
    }
    
    elseif ($method === 'POST' && $pathParts[1] === 'register') {
        $input = json_decode(file_get_contents('php://input'), true);
        $email = $input['email'] ?? '';
        $password = $input['password'] ?? '';
        $name = $input['name'] ?? null;
        
        // Check if email exists
        $stmt = $pdo->prepare("SELECT id FROM users WHERE email = ?");
        $stmt->execute([$email]);
        if ($stmt->fetch()) {
            http_response_code(400);
            echo json_encode(['error' => 'Email already exists']);
            return;
        }
        
        // Create user
        $userId = bin2hex(random_bytes(16));
        $passwordHash = password_hash($password, PASSWORD_DEFAULT);
        
        $stmt = $pdo->prepare("INSERT INTO users (id, email, password_hash, name) VALUES (?, ?, ?, ?)");
        $stmt->execute([$userId, $email, $passwordHash, $name]);
        
        $user = [
            'id' => $userId,
            'email' => $email,
            'name' => $name,
            'is_profile_complete' => false
        ];
        
        echo json_encode(['success' => true, 'user' => $user]);
    }
}

// Profile endpoints
function handleProfile($method, $pathParts, $pdo) {
    if ($method === 'POST' && $pathParts[1] === 'save') {
        $input = json_decode(file_get_contents('php://input'), true);
        $userId = $input['user_id'] ?? '';
        
        // Save basic profile
        $stmt = $pdo->prepare("
            INSERT INTO user_profiles (user_id, birth_year, gender, province) 
            VALUES (?, ?, ?, ?) 
            ON DUPLICATE KEY UPDATE 
            birth_year = VALUES(birth_year), 
            gender = VALUES(gender), 
            province = VALUES(province)
        ");
        $stmt->execute([
            $userId,
            $input['birth_year'] ?? null,
            $input['gender'] ?? null,
            $input['province'] ?? null
        ]);
        
        // Save medical history
        $medicalStmt = $pdo->prepare("
            INSERT INTO medical_history (user_id, chronic_diseases, allergies, current_medications, smoking_status, drinking_frequency) 
            VALUES (?, ?, ?, ?, ?, ?) 
            ON DUPLICATE KEY UPDATE 
            chronic_diseases = VALUES(chronic_diseases),
            allergies = VALUES(allergies),
            current_medications = VALUES(current_medications),
            smoking_status = VALUES(smoking_status),
            drinking_frequency = VALUES(drinking_frequency)
        ");
        $medicalStmt->execute([
            $userId,
            json_encode($input['chronic_diseases'] ?? []),
            json_encode($input['allergies'] ?? []),
            json_encode($input['current_medications'] ?? []),
            $input['smoking_status'] ?? null,
            $input['drinking_frequency'] ?? null
        ]);
        
        // Update user profile complete status
        $updateUser = $pdo->prepare("UPDATE users SET is_profile_complete = TRUE WHERE id = ?");
        $updateUser->execute([$userId]);
        
        echo json_encode(['success' => true]);
    }
    
    elseif ($method === 'GET') {
        $userId = $_GET['user_id'] ?? '';
        
        $stmt = $pdo->prepare("
            SELECT up.*, mh.chronic_diseases, mh.allergies, mh.current_medications, 
                   mh.smoking_status, mh.drinking_frequency
            FROM user_profiles up
            LEFT JOIN medical_history mh ON up.user_id = mh.user_id
            WHERE up.user_id = ?
        ");
        $stmt->execute([$userId]);
        $profile = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if ($profile) {
            // Decode JSON fields
            $profile['chronic_diseases'] = json_decode($profile['chronic_diseases'] ?? '[]', true);
            $profile['allergies'] = json_decode($profile['allergies'] ?? '[]', true);
            $profile['current_medications'] = json_decode($profile['current_medications'] ?? '[]', true);
        }
        
        echo json_encode(['profile' => $profile]);
    }
}

// News endpoints
function handleNews($method, $pathParts, $pdo) {
    if ($method === 'GET') {
        $category = $_GET['category'] ?? '';
        $limit = $_GET['limit'] ?? 20;
        
        $sql = "SELECT * FROM news_articles";
        $params = [];
        
        if ($category) {
            $sql .= " WHERE category LIKE ?";
            $params[] = "%$category%";
        }
        
        $sql .= " ORDER BY published_date DESC LIMIT ?";
        $params[] = (int)$limit;
        
        $stmt = $pdo->prepare($sql);
        $stmt->execute($params);
        $news = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        echo json_encode(['news' => $news]);
    }
}

// Chat endpoints
function handleChat($method, $pathParts, $pdo) {
    if ($method === 'POST') {
        $input = json_decode(file_get_contents('php://input'), true);
        $userId = $input['user_id'] ?? '';
        $message = $input['message'] ?? '';
        
        // Here you would integrate with your AI service
        // For now, return a simple response
        $response = "Cảm ơn bạn đã chia sẻ triệu chứng. Đây là phản hồi từ AI...";
        
        // Save chat history
        $stmt = $pdo->prepare("INSERT INTO chat_history (user_id, message, sender, response) VALUES (?, ?, 'user', ?)");
        $stmt->execute([$userId, $message, $response]);
        
        echo json_encode(['response' => $response]);
    }
}
?>
