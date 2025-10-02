import 'package:flutter/material.dart';
import 'package:qr_code_scanner/qr_code_scanner.dart';
import '../services/drug_verification_service.dart';
import '../models/drug_verification_result.dart';

class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({super.key});

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  final GlobalKey qrKey = GlobalKey(debugLabel: 'QR');
  QRViewController? controller;
  bool isScanning = true;
  bool isVerifying = false;
  DrugVerificationResult? verificationResult;

  @override
  void reassemble() {
    super.reassemble();
    if (controller != null) {
      controller!.pauseCamera();
      controller!.resumeCamera();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Quét mã QR thuốc'),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(isScanning ? Icons.pause : Icons.play_arrow),
            onPressed: () {
              setState(() {
                if (isScanning) {
                  controller?.pauseCamera();
                } else {
                  controller?.resumeCamera();
                }
                isScanning = !isScanning;
              });
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            flex: 4,
            child: _buildQrView(context),
          ),
          Expanded(
            flex: 1,
            child: _buildResultArea(),
          ),
        ],
      ),
    );
  }

  Widget _buildQrView(BuildContext context) {
    // For proper camera sizing
    var scanArea = (MediaQuery.of(context).size.width < 400 ||
        MediaQuery.of(context).size.height < 400)
        ? 250.0
        : 300.0;

    return Stack(
      children: [
        QRView(
          key: qrKey,
          onQRViewCreated: _onQRViewCreated,
          overlay: QrScannerOverlayShape(
            borderColor: Theme.of(context).primaryColor,
            borderRadius: 10,
            borderLength: 30,
            borderWidth: 10,
            cutOutSize: scanArea,
          ),
          onPermissionSet: (ctrl, p) => _onPermissionSet(context, ctrl, p),
        ),
        Positioned(
          bottom: 20,
          left: 20,
          right: 20,
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.black87,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Text(
              '🔍 Đưa mã QR vào khung hình để quét\n🏥 Chỉ quét mã QR từ hộp thuốc chính hãng',
              style: TextStyle(
                color: Colors.white,
                fontSize: 14,
                height: 1.4,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildResultArea() {
    if (isVerifying) {
      return Container(
        padding: const EdgeInsets.all(20),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text(
              'Đang xác thực thuốc trên blockchain...',
              style: TextStyle(fontSize: 16),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    if (verificationResult != null) {
      return Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            if (verificationResult!.isAuthentic) ...[
              Icon(
                Icons.verified,
                color: Colors.green,
                size: 48,
              ),
              const SizedBox(height: 12),
              const Text(
                '✅ THUỐC CHÍNH HÃNG',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                verificationResult!.drugName,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                'Nhà sản xuất: ${verificationResult!.manufacturer}',
                style: const TextStyle(fontSize: 14),
              ),
              if (verificationResult!.currentLocation.isNotEmpty)
                Text(
                  'Đang bán tại: ${verificationResult!.currentLocation}',
                  style: const TextStyle(fontSize: 14),
                ),
            ] else ...[
              Icon(
                Icons.warning,
                color: Colors.red,
                size: 48,
              ),
              const SizedBox(height: 12),
              const Text(
                '⚠️ CẢNH BÁO: HÀNG GIẢ!',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.red,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                verificationResult!.errorMessage,
                style: const TextStyle(fontSize: 14),
                textAlign: TextAlign.center,
              ),
            ],
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  verificationResult = null;
                });
                controller?.resumeCamera();
              },
              child: const Text('Quét mã khác'),
            ),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.qr_code_scanner,
            size: 48,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 12),
          Text(
            'Hướng camera vào mã QR trên hộp thuốc',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  void _onQRViewCreated(QRViewController controller) {
    setState(() {
      this.controller = controller;
    });

    controller.scannedDataStream.listen((scanData) async {
      if (isVerifying || verificationResult != null) return;

      // Pause camera to prevent multiple scans
      await controller.pauseCamera();
      
      // Start verification
      await _verifyDrug(scanData.code ?? '');
    });
  }

  Future<void> _verifyDrug(String qrCode) async {
    if (qrCode.isEmpty) return;

    setState(() {
      isVerifying = true;
    });

    try {
      // Call drug verification service
      final result = await DrugVerificationService.instance.verifyDrug(qrCode);
      
      setState(() {
        verificationResult = result;
        isVerifying = false;
      });

      // Show result dialog
      if (result.isAuthentic) {
        _showSuccessDialog(result);
      } else {
        _showWarningDialog(result);
      }
    } catch (e) {
      setState(() {
        verificationResult = DrugVerificationResult.error(
          'Không thể xác thực: ${e.toString()}'
        );
        isVerifying = false;
      });
    }
  }

  void _showSuccessDialog(DrugVerificationResult result) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.verified, color: Colors.green),
            SizedBox(width: 8),
            Text('Thuốc chính hãng'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Tên thuốc: ${result.drugName}'),
            Text('Nhà sản xuất: ${result.manufacturer}'),
            if (result.batchNumber.isNotEmpty)
              Text('Số lô: ${result.batchNumber}'),
            if (result.expiryDate.isNotEmpty)
              Text('Hạn sử dụng: ${result.expiryDate}'),
            const SizedBox(height: 16),
            const Text(
              'Lịch sử chuỗi cung ứng:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            ...result.supplyChainHistory.map((step) => 
              Padding(
                padding: const EdgeInsets.only(left: 8, top: 4),
                child: Text('• $step'),
              )
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Đóng'),
          ),
        ],
      ),
    );
  }

  void _showWarningDialog(DrugVerificationResult result) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning, color: Colors.red),
            SizedBox(width: 8),
            Text('Cảnh báo!'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'THUỐC NÀY CÓ THỂ LÀ HÀNG GIẢ!',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.red,
              ),
            ),
            const SizedBox(height: 12),
            Text(result.errorMessage),
            const SizedBox(height: 12),
            const Text(
              'Khuyến nghị:\n• Không sử dụng sản phẩm này\n• Báo cáo cho nhà thuốc\n• Liên hệ cơ quan y tế địa phương',
              style: TextStyle(fontSize: 14),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Đã hiểu'),
          ),
        ],
      ),
    );
  }

  void _onPermissionSet(BuildContext context, QRViewController ctrl, bool p) {
    if (!p) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cần cấp quyền camera để quét mã QR')),
      );
    }
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }
}
