// Test script để kiểm tra API connections
// Chạy script này để test các API endpoints

import 'dart:developer' as developer;
import 'api_service.dart';
import 'auth_service.dart';
import 'chat_service.dart';
import 'diagnosis_service.dart';

class ApiTester {
  static Future<void> testAllApis() async {
    developer.log('🧪 Bắt đầu test API connections...');
    
    // Test 1: Auth API
    await _testAuthApi();
    
    // Test 2: Chat API (cần auth)
    await _testChatApi();
    
    // Test 3: Diagnosis API (cần auth)
    await _testDiagnosisApi();
    
    developer.log('✅ Hoàn thành test API connections');
  }

  static Future<void> _testAuthApi() async {
    developer.log('🔐 Testing Auth API...');
    
    try {
      // Test register
      final registerResult = await AuthService.instance.register(
        'test@example.com',
        'password123',
        'password123',
        'Test User',
      );
      
      if (registerResult.isSuccess) {
        developer.log('✅ Register API: SUCCESS');
      } else {
        developer.log('❌ Register API: ${registerResult.error}');
      }
      
      // Test login
      final loginResult = await AuthService.instance.login(
        'test@example.com',
        'password123',
      );
      
      if (loginResult.isSuccess) {
        developer.log('✅ Login API: SUCCESS');
      } else {
        developer.log('❌ Login API: ${loginResult.error}');
      }
      
    } catch (e) {
      developer.log('❌ Auth API Error: $e');
    }
  }

  static Future<void> _testChatApi() async {
    developer.log('💬 Testing Chat API...');
    
    try {
      final chatService = ChatService.instance;
      
      // Test create session
      final sessionResult = await chatService.createSession();
      if (sessionResult.isSuccess) {
        developer.log('✅ Create Session API: SUCCESS - ${sessionResult.sessionId}');
        
        // Test send message
        final messageResult = await chatService.sendUserMessage('Hello test');
        if (messageResult.isSuccess) {
          developer.log('✅ Send Message API: SUCCESS');
        } else {
          developer.log('❌ Send Message API: ${messageResult.error}');
        }
        
        // Test get chat history
        final history = await chatService.getChatHistory();
        developer.log('✅ Get Chat History: ${history.length} messages');
        
      } else {
        developer.log('❌ Create Session API: ${sessionResult.error}');
      }
      
    } catch (e) {
      developer.log('❌ Chat API Error: $e');
    }
  }

  static Future<void> _testDiagnosisApi() async {
    developer.log('🔬 Testing Diagnosis API...');
    
    try {
      final diagnosisService = DiagnosisService.instance;
      
      // Test get diagnosis history
      final history = await diagnosisService.getDiagnosisHistory();
      developer.log('✅ Get Diagnosis History: ${history.length} diagnoses');
      
      // Test get diagnosis (requires session ID)
      if (ChatService.instance.currentSessionId != null) {
        final diagnosisResult = await diagnosisService.getDiagnosis(
          ChatService.instance.currentSessionId!
        );
        
        if (diagnosisResult.isSuccess) {
          developer.log('✅ Get Diagnosis API: SUCCESS');
        } else {
          developer.log('❌ Get Diagnosis API: ${diagnosisResult.error}');
        }
      }
      
    } catch (e) {
      developer.log('❌ Diagnosis API Error: $e');
    }
  }

  // Test network connectivity
  static Future<bool> testNetworkConnectivity() async {
    developer.log('🌐 Testing network connectivity...');
    
    try {
      final apiService = ApiService.instance;
      
      // Simple health check - try to reach backend
      final response = await apiService.get(
        '/chat/health',
        requireAuth: false,
      );
      
      if (response.isSuccess) {
        developer.log('✅ Network connectivity: OK');
        developer.log('Backend response: ${response.data}');
        return true;
      } else {
        developer.log('❌ Network connectivity: ${response.error}');
        return false;
      }
      
    } catch (e) {
      developer.log('❌ Network connectivity error: $e');
      return false;
    }
  }

  // Test backend services health
  static Future<void> testBackendHealth() async {
    developer.log('🏥 Testing backend services health...');
    
    try {
      final apiService = ApiService.instance;
      
      // Test main backend
      final backendHealth = await apiService.get(
        '/chat/health',
        requireAuth: false,
      );
      
      if (backendHealth.isSuccess) {
        developer.log('✅ Backend health: OK');
        final healthData = backendHealth.data as Map<String, dynamic>?;
        if (healthData != null) {
          developer.log('Backend status: ${healthData['status']}');
          developer.log('Chatbot service: ${healthData['chatbot_service']}');
        }
      } else {
        developer.log('❌ Backend health: ${backendHealth.error}');
      }
      
    } catch (e) {
      developer.log('❌ Backend health error: $e');
    }
  }
}

// Helper function để chạy test từ main app
Future<void> runApiTests() async {
  await ApiTester.testNetworkConnectivity();
  await ApiTester.testBackendHealth();
  await ApiTester.testAllApis();
}
