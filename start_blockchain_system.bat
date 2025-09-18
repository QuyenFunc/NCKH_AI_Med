@echo off
setlocal EnableDelayedExpansion

echo.
echo ================================================================
echo    🚀 BLOCKCHAIN DRUG TRACEABILITY SYSTEM LAUNCHER
echo ================================================================
echo    Khởi động hệ thống truy xuất nguồn gốc thuốc hoàn chỉnh
echo    Bao gồm: Blockchain + Backend + AI Services + Web Portals
echo ================================================================
echo.

:: Colors for output
set "RED=[31m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "CYAN=[36m"
set "WHITE=[37m"
set "RESET=[0m"

:: Function to print colored text
goto :start

:print_colored
echo %~2%~1%RESET%
goto :eof

:start

echo %CYAN%📋 Kiểm tra Prerequisites...%RESET%
echo.

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ Node.js không được tìm thấy. Vui lòng cài đặt Node.js.%RESET%
    pause
    exit /b 1
)

:: Check Java
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ Java không được tìm thấy. Vui lòng cài đặt Java.%RESET%
    pause
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ Python không được tìm thấy. Vui lòng cài đặt Python.%RESET%
    pause
    exit /b 1
)

echo %GREEN%✅ Tất cả prerequisites đã sẵn sàng!%RESET%
echo.

echo %YELLOW%🔧 Bắt đầu khởi động các services...%RESET%
echo.

:: 1. Start Hardhat Blockchain Node
echo %CYAN%1️⃣  Khởi động Hardhat Blockchain Node (Port 8545)...%RESET%
cd contracts
start "Blockchain Node" cmd /c "npx hardhat node"
timeout /t 5 /nobreak >nul

:: 2. Deploy Smart Contracts
echo %CYAN%2️⃣  Deploy Smart Contracts...%RESET%
npx hardhat run scripts/deploy.js --network localhost
if %errorlevel% neq 0 (
    echo %RED%❌ Lỗi khi deploy smart contracts%RESET%
    pause
    exit /b 1
)
cd ..

:: 3. Start Backend Spring Boot
echo %CYAN%3️⃣  Khởi động Backend API (Port 8080)...%RESET%
cd backend
start "Backend API" cmd /c "mvn spring-boot:run"
timeout /t 10 /nobreak >nul
cd ..

:: 4. Start AI Chatbot Service
echo %CYAN%4️⃣  Khởi động AI Chatbot Service (Port 5000)...%RESET%
cd AI\chatbox
start "AI Chatbot" cmd /c "python medical_chatbot_enhanced.py"
timeout /t 5 /nobreak >nul
cd ..\..

:: 5. Start AI Recommendation Service
echo %CYAN%5️⃣  Khởi động AI Recommendation Service (Port 5002)...%RESET%
cd AI\recommendation_system
start "AI Recommendation" cmd /c "python start_recommendation_service.py"
timeout /t 5 /nobreak >nul
cd ..\..

:: 6. Start Pharmacy Web Portal
echo %CYAN%6️⃣  Khởi động Pharmacy Web Portal (Port 3000)...%RESET%
cd web_portal
start "Pharmacy Portal" cmd /c "npm start"
timeout /t 5 /nobreak >nul
cd ..

:: 7. Start Distributor Web Portal
echo %CYAN%7️⃣  Khởi động Distributor Web Portal (Port 3001)...%RESET%
cd web_NhaPhanPhoi
start "Distributor Portal" cmd /c "npm start"
timeout /t 5 /nobreak >nul
cd ..

echo.
echo %GREEN%🎉 Tất cả services đã được khởi động!%RESET%
echo.

:: Wait for services to be ready
echo %YELLOW%⏳ Đang chờ các services khởi động hoàn tất...%RESET%
timeout /t 15 /nobreak >nul

echo.
echo ================================================================
echo %GREEN%✅ HỆ THỐNG ĐÃ SẴN SÀNG SỬ DỤNG!%RESET%
echo ================================================================
echo.
echo %CYAN%🌐 Web Portals:%RESET%
echo    • Pharmacy Portal:    http://localhost:3000
echo    • Distributor Portal: http://localhost:3001
echo.
echo %CYAN%🔧 API Services:%RESET%
echo    • Backend API:        http://localhost:8080
echo    • API Documentation:  http://localhost:8080/swagger-ui.html
echo    • AI Chatbot:         http://localhost:5000
echo    • AI Recommendation:  http://localhost:5002
echo.
echo %CYAN%⛓️  Blockchain:%RESET%
echo    • Hardhat Node:       http://localhost:8545
echo    • Smart Contract:     0x5FbDB2315678afecb367f032d93F642f64180aa3
echo.
echo %CYAN%📱 Mobile App:%RESET%
echo    • Flutter: Chạy 'flutter run' trong terminal riêng
echo.
echo ================================================================
echo %YELLOW%💡 HƯỚNG DẪN SỬ DỤNG:%RESET%
echo.
echo %WHITE%1. Manufacturer (Nhà sản xuất):%RESET%
echo    - Sử dụng API để tạo lô thuốc mới
echo    - POST http://localhost:8080/api/blockchain/manufacturer/batch
echo.
echo %WHITE%2. Distributor (Nhà phân phối):%RESET%
echo    - Truy cập: http://localhost:3001
echo    - Quản lý lô hàng và tạo shipments
echo.
echo %WHITE%3. Pharmacy (Hiệu thuốc):%RESET%
echo    - Truy cập: http://localhost:3000
echo    - Nhận hàng và quản lý kho
echo.
echo %WHITE%4. Consumer (Người tiêu dùng):%RESET%
echo    - Sử dụng Flutter app để scan QR code
echo    - Hoặc truy cập API: GET /api/blockchain/public/verify/{qrCode}
echo.
echo ================================================================
echo %RED%⚠️  LƯU Ý:%RESET%
echo    • Không đóng cửa sổ này để giữ các services chạy
echo    • Để dừng hệ thống, đóng tất cả cửa sổ terminal
echo    • Kiểm tra logs trong các cửa sổ riêng biệt nếu có lỗi
echo ================================================================
echo.

echo %GREEN%Nhấn phím bất kỳ để mở web portals...%RESET%
pause >nul

:: Open web browsers
start "" "http://localhost:3000"
start "" "http://localhost:3001"
start "" "http://localhost:8080/swagger-ui.html"

echo.
echo %GREEN%🚀 Hệ thống đang chạy. Chúc bạn sử dụng hiệu quả!%RESET%
echo.

:: Keep the window open
echo %CYAN%Nhấn Ctrl+C để dừng hệ thống...%RESET%
:loop
timeout /t 30 /nobreak >nul
echo %YELLOW%[%date% %time%] Hệ thống đang hoạt động bình thường...%RESET%
goto loop
