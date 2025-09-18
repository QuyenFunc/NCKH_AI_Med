# Test Blockchain API Script
Write-Host "🔍 Testing Blockchain API Integration..." -ForegroundColor Cyan

$baseUrl = "http://localhost:8080/api"

# Test health check
Write-Host "`n1. Testing Backend Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/actuator/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Backend Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not responding: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test blockchain health
Write-Host "`n2. Testing Blockchain Health..." -ForegroundColor Yellow
try {
    $blockchainHealth = Invoke-RestMethod -Uri "$baseUrl/blockchain/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Blockchain Health: $($blockchainHealth.message)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Blockchain connection issue: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   This is expected if Hardhat node is not running" -ForegroundColor Gray
}

# Test API documentation
Write-Host "`n3. Testing API Documentation..." -ForegroundColor Yellow
try {
    $swagger = Invoke-WebRequest -Uri "http://localhost:8080/swagger-ui.html" -Method GET -TimeoutSec 5
    if ($swagger.StatusCode -eq 200) {
        Write-Host "✅ Swagger UI available at: http://localhost:8080/swagger-ui.html" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Swagger UI not accessible" -ForegroundColor Red
}

Write-Host "`n🎉 Backend API testing completed!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Start Hardhat node: cd contracts && npx hardhat node" -ForegroundColor White
Write-Host "   2. Deploy contracts: npx hardhat run scripts/deploy.js --network localhost" -ForegroundColor White
Write-Host "   3. Test blockchain endpoints" -ForegroundColor White
Write-Host "   4. Start frontend: cd web_NhaPhanPhoi && npm start" -ForegroundColor White

Write-Host "`n🌐 Available URLs:" -ForegroundColor Cyan
Write-Host "   • Backend API: http://localhost:8080" -ForegroundColor White
Write-Host "   • API Docs: http://localhost:8080/swagger-ui.html" -ForegroundColor White
Write-Host "   • Health Check: http://localhost:8080/actuator/health" -ForegroundColor White
