@echo off
echo ========================================
echo    NCKH AI Medical - Start All Services
echo ========================================
echo.

echo Starting services in separate windows...
echo.

echo 1. Starting Blockchain (Hardhat)...
start "Blockchain" cmd /k "cd contracts && npx hardhat node"
timeout /t 5

echo 3. Starting Web Nha San Xuat (Port 3001)...
start "Web-NhaSanXuat" cmd /k "cd web_NhaSanXuat && npm start"
timeout /t 2

echo 4. Starting Web Nha Phan Phoi (Port 3002)...
start "Web-NhaPhanPhoi" cmd /k "cd web_NhaPhanPhoi && npm start"
timeout /t 2

echo 5. Starting Web Hieu Thuoc (Port 3003)...
start "Web-HieuThuoc" cmd /k "cd web_HieuThuoc && npm start"
timeout /t 2

@REM echo 6. Starting Web Nguoi Dung (Port 3004)...
@REM start "Web-NguoiDung" cmd /k "cd web_NguoiDung\frontend && npm run dev"

echo.
echo ========================================
echo    All Services Started Successfully!
echo ========================================
echo.
echo Service URLs:
echo • Blockchain: http://localhost:8545
echo • Backend API: http://localhost:8080
echo • Web Nha San Xuat: http://localhost:3001
echo • Web Nha Phan Phoi: http://localhost:3002
echo • Web Hieu Thuoc: http://localhost:3003
echo • Web Nguoi Dung: http://localhost:3004
echo.
echo BlockScout Explorer: http://localhost:3000
echo.
echo Press any key to exit...
pause
