import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api_service.dart';
import '../models/message.dart';

class ChatService {
  static ChatService? _instance;
  static ChatService get instance => _instance ??= ChatService._();
  ChatService._();

  final ApiService _apiService = ApiService.instance;
  
  // Python chatbot service URL
  static const String _chatbotUrl = 'http://10.0.2.2:5001';
  
  String? _currentSessionId;
  
  String? get currentSessionId => _currentSessionId;

  // Create new chat session
  Future<ChatSessionResult> createSession() async {
    try {
      final response = await _apiService.post(
        '/chat/sessions',
        {},
        fromJson: (data) => data as Map<String, dynamic>,
      );
      
      if (response.isSuccess && response.data != null) {
        _currentSessionId = response.data!['id'];
        return ChatSessionResult.success(_currentSessionId!);
      } else {
        return ChatSessionResult.error(response.error ?? 'Không thể tạo phiên chat');
      }
    } catch (e) {
      print('Create session error: $e');
      return ChatSessionResult.error('Đã có lỗi xảy ra khi tạo phiên chat');
    }
  }

  // Send user message to backend and get session ID
  Future<ChatResult> sendUserMessage(String message) async {
    try {
      if (_currentSessionId == null) {
        final sessionResult = await createSession();
        if (sessionResult.isError) {
          return ChatResult.error(sessionResult.error!);
        }
      }

      final response = await _apiService.post(
        '/chat/sessions/$_currentSessionId/messages',
        {'message': message},
        fromJson: (data) => data as Map<String, dynamic>,
      );
      
      if (response.isSuccess && response.data != null) {
        final messageData = response.data!;
        final userMessage = Message(
          id: messageData['id'],
          content: messageData['messageText'],
          sender: MessageSender.user,
          timestamp: DateTime.parse(messageData['timestamp']),
        );
        
        return ChatResult.success(userMessage);
      } else {
        return ChatResult.error(response.error ?? 'Không thể gửi tin nhắn');
      }
    } catch (e) {
      print('Send message error: $e');
      return ChatResult.error('Đã có lỗi xảy ra khi gửi tin nhắn');
    }
  }

  // Stream chat response from Python chatbot
  Stream<String> streamChatResponse(String message) async* {
    try {
      print('Streaming response from chatbot for: $message');
      
      final request = http.Request(
        'POST',
        Uri.parse('$_chatbotUrl/chat/stream'),
      );
      
      request.headers.addAll({
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      });
      
      request.body = json.encode({
        'message': message,
        'session_id': _currentSessionId,
      });

      final streamedResponse = await request.send();
      
      if (streamedResponse.statusCode == 200) {
        String buffer = '';
        
        await for (final chunk in streamedResponse.stream.transform(utf8.decoder)) {
          buffer += chunk;
          
          // Process complete lines
          while (buffer.contains('\n')) {
            final lineEnd = buffer.indexOf('\n');
            final line = buffer.substring(0, lineEnd).trim();
            buffer = buffer.substring(lineEnd + 1);
            
            if (line.startsWith('data: ')) {
              final data = line.substring(6);
              if (data == '[DONE]') {
                return;
              }
              
              try {
                final jsonData = json.decode(data);
                final content = jsonData['content'] as String?;
                if (content != null && content.isNotEmpty) {
                  yield content;
                }
              } catch (e) {
                print('Error parsing JSON: $e');
              }
            }
          }
        }
      } else {
        throw Exception('Chatbot service error: ${streamedResponse.statusCode}');
      }
    } catch (e) {
      print('Stream chat error: $e');
      yield 'Xin lỗi, đã có lỗi xảy ra khi kết nối với chatbot. Vui lòng thử lại sau.';
    }
  }

  // Save AI response to backend
  Future<ChatResult> saveAiResponse(
    String message, {
    double? confidence,
    int? processingTime,
    String? sourcesJson,
  }) async {
    try {
      if (_currentSessionId == null) return ChatResult.error('Không có session ID');

      final response = await _apiService.post(
        '/chat/sessions/$_currentSessionId/ai-response',
        {
          'message': message,
          'confidence': confidence,
          'processingTime': processingTime,
          'sourcesJson': sourcesJson,
        },
        fromJson: (data) => ChatMessage.fromJson(data),
      );
      
      if (response.isSuccess && response.data != null) {
        final chatMessage = response.data!;
        final aiMessage = Message(
          id: chatMessage.id,
          content: chatMessage.messageText,
          sender: MessageSender.bot,
          timestamp: chatMessage.timestamp,
        );
        
        return ChatResult.success(aiMessage);
      } else {
        return ChatResult.error(response.error ?? 'Không thể lưu phản hồi AI');
      }
    } catch (e) {
      print('Save AI response error: $e');
      return ChatResult.error('Đã có lỗi xảy ra khi lưu phản hồi AI');
    }
  }

  // Get chat history
  Future<List<Message>> getChatHistory() async {
    try {
      if (_currentSessionId == null) return [];

      final response = await _apiService.get(
        '/chat/sessions/$_currentSessionId/messages',
        fromJson: (data) => (data as List).map((item) => ChatMessage.fromJson(item)).toList(),
      );
      
      if (response.isSuccess && response.data != null) {
        return response.data!.map((chatMessage) => Message(
          id: chatMessage.id,
          content: chatMessage.messageText,
          sender: chatMessage.sender == 'AI' ? MessageSender.bot : MessageSender.user,
          timestamp: chatMessage.timestamp,
        )).toList();
      }
    } catch (e) {
      print('Get chat history error: $e');
    }
    return [];
  }

  // Get user sessions
  Future<List<ChatSession>> getUserSessions() async {
    try {
      final response = await _apiService.get(
        '/chat/sessions',
        fromJson: (data) => (data as List).map((item) => ChatSession.fromJson(item)).toList(),
      );
      
      if (response.isSuccess && response.data != null) {
        return response.data!;
      }
    } catch (e) {
      print('Get user sessions error: $e');
    }
    return [];
  }

  // End current session
  Future<bool> endSession() async {
    try {
      if (_currentSessionId == null) return false;

      final response = await _apiService.put(
        '/chat/sessions/$_currentSessionId/end',
        {},
      );
      
      if (response.isSuccess) {
        _currentSessionId = null;
        return true;
      }
    } catch (e) {
      print('End session error: $e');
    }
    return false;
  }

  // Delete session
  Future<bool> deleteSession(String sessionId) async {
    try {
      final response = await _apiService.delete('/chat/sessions/$sessionId');
      
      if (response.isSuccess) {
        if (_currentSessionId == sessionId) {
          _currentSessionId = null;
        }
        return true;
      }
    } catch (e) {
      print('Delete session error: $e');
    }
    return false;
  }

  // Set current session
  void setCurrentSession(String sessionId) {
    _currentSessionId = sessionId;
  }

  // Clear current session
  void clearCurrentSession() {
    _currentSessionId = null;
  }
}

// Result classes
class ChatResult {
  final bool success;
  final Message? message;
  final String? error;

  ChatResult._({required this.success, this.message, this.error});

  factory ChatResult.success(Message message) => ChatResult._(success: true, message: message);
  factory ChatResult.error(String error) => ChatResult._(success: false, error: error);

  bool get isSuccess => success;
  bool get isError => !success;
}

class ChatSessionResult {
  final bool success;
  final String? sessionId;
  final String? error;

  ChatSessionResult._({required this.success, this.sessionId, this.error});

  factory ChatSessionResult.success(String sessionId) => ChatSessionResult._(success: true, sessionId: sessionId);
  factory ChatSessionResult.error(String error) => ChatSessionResult._(success: false, error: error);

  bool get isSuccess => success;
  bool get isError => !success;
}

// Backend response models
class ChatMessage {
  final String id;
  final String messageText;
  final String sender;
  final DateTime timestamp;
  final double? confidence;
  final int? processingTime;
  final String? sourcesJson;

  ChatMessage({
    required this.id,
    required this.messageText,
    required this.sender,
    required this.timestamp,
    this.confidence,
    this.processingTime,
    this.sourcesJson,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? '',
      messageText: json['messageText'] ?? '',
      sender: json['sender'] ?? '',
      timestamp: DateTime.parse(json['timestamp']),
      confidence: json['confidence']?.toDouble(),
      processingTime: json['processingTime'],
      sourcesJson: json['sourcesJson'],
    );
  }
}

class ChatSession {
  final String id;
  final String sessionType;
  final DateTime startedAt;
  final DateTime? endedAt;
  final int totalMessages;

  ChatSession({
    required this.id,
    required this.sessionType,
    required this.startedAt,
    this.endedAt,
    required this.totalMessages,
  });

  factory ChatSession.fromJson(Map<String, dynamic> json) {
    return ChatSession(
      id: json['id'] ?? '',
      sessionType: json['sessionType'] ?? '',
      startedAt: DateTime.parse(json['startedAt']),
      endedAt: json['endedAt'] != null ? DateTime.parse(json['endedAt']) : null,
      totalMessages: json['totalMessages'] ?? 0,
    );
  }
}
