import 'dart:async';
// import 'dart:convert';
// import 'package:http/http.dart' as http;

class ChatService {
  // static const String _baseUrl = 'https://api.example.com'; // Thay đổi URL này thành API backend thực tế
  
  // Simulate API call for now - replace with real implementation later
  Future<String> sendMessage(String message) async {
    // Simulate network delay
    await Future.delayed(const Duration(seconds: 2));
    
    // Simulate different responses based on input
    if (message.toLowerCase().contains('đau đầu')) {
      return '''**Chẩn đoán sơ bộ:**

Dựa trên triệu chứng đau đầu bạn mô tả, có thể là:

• **Đau đầu căng thẳng** - Nguyên nhân phổ biến nhất
• **Đau nửa đầu (migraine)** - Nếu kèm theo buồn nôn, nhạy cảm với ánh sáng
• **Đau đầu do stress** - Liên quan đến căng thẳng công việc

**Khuyến nghị:**
1. Nghỉ ngơi đầy đủ
2. Uống đủ nước
3. Tránh căng thẳng
4. Nếu đau kéo dài >3 ngày, hãy đến gặp bác sĩ

*Lưu ý: Đây chỉ là chẩn đoán sơ bộ, không thay thế ý kiến bác sĩ chuyên khoa.*''';
    } else if (message.toLowerCase().contains('sốt')) {
      return '''**Chẩn đoán sơ bộ:**

Triệu chứng sốt có thể do:

• **Nhiễm trùng virus** - Cảm lạnh, cúm
• **Nhiễm trùng vi khuẩn** - Viêm họng, viêm phổi
• **Phản ứng miễn dịch** - Do vaccine hoặc thuốc

**Khuyến nghị:**
1. Uống nhiều nước
2. Nghỉ ngơi
3. Hạ sốt bằng paracetamol nếu cần
4. Theo dõi nhiệt độ thường xuyên

**Cảnh báo:** Nếu sốt >39°C hoặc kéo dài >3 ngày, hãy đến bệnh viện ngay!''';
    } else {
      return '''Cảm ơn bạn đã chia sẻ triệu chứng. 

Để Dia5 có thể đưa ra chẩn đoán chính xác hơn, bạn có thể mô tả chi tiết:

• Triệu chứng cụ thể
• Thời gian xuất hiện
• Mức độ nghiêm trọng (1-10)
• Các yếu tố khởi phát

Ví dụ: "Tôi bị đau đầu từ 2 ngày nay, đau âm ỉ ở thái dương, tăng khi căng thẳng"

*Dia5 luôn sẵn sàng hỗ trợ bạn!*''';
    }
  }
  
  // Real API implementation (commented out for now)
  /*
  Future<String> _callRealAPI(String message) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/chat'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_KEY',
        },
        body: json.encode({
          'message': message,
          'user_id': 'user123', // Get from user session
        }),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['response'] ?? 'Xin lỗi, tôi không thể xử lý yêu cầu này.';
      } else {
        throw Exception('API call failed');
      }
    } catch (e) {
      return 'Đã có lỗi xảy ra. Vui lòng thử lại sau.';
    }
  }
  */
}
