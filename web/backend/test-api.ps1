# API Test Script for Dia5 Medical API
Write-Host "🚀 Testing Dia5 Medical API..." -ForegroundColor Green

$baseUrl = "http://localhost:8080"
$headers = @{ "Content-Type" = "application/json" }

# Wait for application to start
Write-Host "⏳ Waiting for application to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test 1: Health Check
Write-Host "`n📊 Testing Health Check..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/actuator/health" -Method GET
    Write-Host "✅ Health Check: " -ForegroundColor Green -NoNewline
    Write-Host $response.status -ForegroundColor White
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: API Documentation
Write-Host "`n📚 Testing API Documentation..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/v3/api-docs" -Method GET
    Write-Host "✅ API Docs: Available" -ForegroundColor Green
} catch {
    Write-Host "❌ API Docs Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Register new user
Write-Host "`n👤 Testing User Registration..." -ForegroundColor Cyan
$registerData = @{
    email = "test@example.com"
    password = "password123"
    confirmPassword = "password123"
    name = "Test User"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/register" -Method POST -Body $registerData -Headers $headers
    Write-Host "✅ Registration: Success" -ForegroundColor Green
    $token = $registerResponse.data.accessToken
    Write-Host "🔑 Token received: $($token.Substring(0,20))..." -ForegroundColor Yellow
} catch {
    Write-Host "❌ Registration Failed: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try login instead if user already exists
    Write-Host "`n🔑 Trying Login instead..." -ForegroundColor Cyan
    $loginData = @{
        email = "test@example.com"
        password = "password123"
    } | ConvertTo-Json
    
    try {
        $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method POST -Body $loginData -Headers $headers
        Write-Host "✅ Login: Success" -ForegroundColor Green
        $token = $loginResponse.data.accessToken
        Write-Host "🔑 Token received: $($token.Substring(0,20))..." -ForegroundColor Yellow
    } catch {
        Write-Host "❌ Login Failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Set authorization header
$authHeaders = @{ 
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
}

# Test 4: Get current user
Write-Host "`n👤 Testing Get Current User..." -ForegroundColor Cyan
try {
    $userResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/me" -Method GET -Headers $authHeaders
    Write-Host "✅ Get Current User: Success" -ForegroundColor Green
    Write-Host "📧 User Email: $($userResponse.data.email)" -ForegroundColor White
} catch {
    Write-Host "❌ Get Current User Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Get user profile
Write-Host "`n📋 Testing Get User Profile..." -ForegroundColor Cyan
try {
    $profileResponse = Invoke-RestMethod -Uri "$baseUrl/api/users/profile" -Method GET -Headers $authHeaders
    Write-Host "✅ Get User Profile: Success" -ForegroundColor Green
    Write-Host "✅ Profile Complete: $($profileResponse.data.isProfileComplete)" -ForegroundColor White
} catch {
    Write-Host "❌ Get User Profile Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Get provinces
Write-Host "`n🌍 Testing Get Provinces..." -ForegroundColor Cyan
try {
    $provincesResponse = Invoke-RestMethod -Uri "$baseUrl/api/provinces" -Method GET -Headers $authHeaders
    Write-Host "✅ Get Provinces: Success" -ForegroundColor Green
    Write-Host "📊 Total Provinces: $($provincesResponse.data.Count)" -ForegroundColor White
} catch {
    Write-Host "❌ Get Provinces Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Get medical specialties
Write-Host "`n🏥 Testing Get Medical Specialties..." -ForegroundColor Cyan
try {
    $specialtiesResponse = Invoke-RestMethod -Uri "$baseUrl/api/medical-specialties" -Method GET -Headers $authHeaders
    Write-Host "✅ Get Medical Specialties: Success" -ForegroundColor Green
    Write-Host "📊 Total Specialties: $($specialtiesResponse.data.Count)" -ForegroundColor White
} catch {
    Write-Host "❌ Get Medical Specialties Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 8: Get root specialties
Write-Host "`n🏥 Testing Get Root Specialties..." -ForegroundColor Cyan
try {
    $rootSpecialtiesResponse = Invoke-RestMethod -Uri "$baseUrl/api/medical-specialties/root" -Method GET -Headers $authHeaders
    Write-Host "✅ Get Root Specialties: Success" -ForegroundColor Green
    Write-Host "📊 Root Specialties: $($rootSpecialtiesResponse.data.Count)" -ForegroundColor White
} catch {
    Write-Host "❌ Get Root Specialties Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 9: Update profile
Write-Host "`n✏️ Testing Update Profile..." -ForegroundColor Cyan
$profileUpdateData = @{
    name = "Updated Test User"
    birthYear = 1990
    gender = "male"
    heightCm = 175
    weightKg = 70.5
} | ConvertTo-Json

try {
    $updateResponse = Invoke-RestMethod -Uri "$baseUrl/api/users/profile" -Method PUT -Body $profileUpdateData -Headers $authHeaders
    Write-Host "✅ Update Profile: Success" -ForegroundColor Green
    Write-Host "👤 Updated Name: $($updateResponse.data.name)" -ForegroundColor White
} catch {
    Write-Host "❌ Update Profile Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 10: Test unauthorized access
Write-Host "`n🔒 Testing Unauthorized Access..." -ForegroundColor Cyan
try {
    $unauthorizedResponse = Invoke-RestMethod -Uri "$baseUrl/api/users/me" -Method GET -Headers $headers
    Write-Host "❌ Security Issue: Unauthorized access allowed!" -ForegroundColor Red
} catch {
    Write-Host "✅ Security: Unauthorized access properly blocked" -ForegroundColor Green
}

# Test 11: Test logout
Write-Host "`n🚪 Testing Logout..." -ForegroundColor Cyan
try {
    $logoutResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/logout" -Method POST -Headers $authHeaders
    Write-Host "✅ Logout: Success" -ForegroundColor Green
} catch {
    Write-Host "❌ Logout Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 API Testing Complete!" -ForegroundColor Green
Write-Host "📊 Check results above for any failures." -ForegroundColor Yellow
Write-Host "📚 Swagger UI: http://localhost:8080/swagger-ui.html" -ForegroundColor Cyan
