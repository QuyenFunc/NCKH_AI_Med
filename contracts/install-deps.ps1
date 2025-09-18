# Install dependencies script for PharmaLedger Blockchain project
Write-Host "🔧 Installing Blockchain Dependencies..." -ForegroundColor Cyan
Write-Host "📦 Solidity 0.8.28 | OpenZeppelin 5.4.0 | Hardhat 3.0.x | Ethers 6.15.x" -ForegroundColor Yellow

# Clean install
if (Test-Path "node_modules") {
    Write-Host "🗑️  Cleaning old node_modules..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "node_modules"
}

if (Test-Path "package-lock.json") {
    Write-Host "🗑️  Cleaning old package-lock.json..." -ForegroundColor Yellow
    Remove-Item -Force "package-lock.json"
}

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Green
npm install

# Verify installation
Write-Host "`n🔍 Verifying installation..." -ForegroundColor Cyan
$hardhatVersion = npm list hardhat --depth=0 2>$null | Select-String "hardhat@"
$ozVersion = npm list @openzeppelin/contracts --depth=0 2>$null | Select-String "@openzeppelin/contracts@"
$ethersVersion = npm list ethers --depth=0 2>$null | Select-String "ethers@"

Write-Host "✅ Hardhat: $hardhatVersion" -ForegroundColor Green
Write-Host "✅ OpenZeppelin: $ozVersion" -ForegroundColor Green  
Write-Host "✅ Ethers: $ethersVersion" -ForegroundColor Green

Write-Host "`n🎉 Dependencies installed successfully!" -ForegroundColor Green
Write-Host "🚀 Ready to compile and deploy smart contracts!" -ForegroundColor Cyan
