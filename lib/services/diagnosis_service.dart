import 'dart:async';
import 'api_service.dart';

class DiagnosisService {
  static DiagnosisService? _instance;
  static DiagnosisService get instance => _instance ??= DiagnosisService._();
  DiagnosisService._();

  final ApiService _apiService = ApiService.instance;

  // Get AI diagnosis for a chat session
  Future<DiagnosisResult> getDiagnosis(String sessionId) async {
    try {
      final response = await _apiService.post(
        '/ai-diagnosis/diagnose/$sessionId',
        {},
        fromJson: (data) => AiDiagnosisResponse.fromJson(data),
      );
      
      if (response.isSuccess && response.data != null) {
        return DiagnosisResult.success(response.data!);
      } else {
        return DiagnosisResult.error(response.error ?? 'Không thể thực hiện chẩn đoán AI');
      }
    } catch (e) {
      print('Get diagnosis error: $e');
      return DiagnosisResult.error('Đã có lỗi xảy ra khi thực hiện chẩn đoán AI');
    }
  }

  // Get diagnosis history for current user
  Future<List<AiDiagnosis>> getDiagnosisHistory() async {
    try {
      final response = await _apiService.get(
        '/ai-diagnosis/history',
        fromJson: (data) => (data as List).map((item) => AiDiagnosis.fromJson(item)).toList(),
      );
      
      if (response.isSuccess && response.data != null) {
        return response.data!;
      }
    } catch (e) {
      print('Get diagnosis history error: $e');
    }
    return [];
  }

  // Get diagnosis by session ID
  Future<AiDiagnosis?> getDiagnosisBySession(String sessionId) async {
    try {
      final response = await _apiService.get(
        '/ai-diagnosis/session/$sessionId',
        fromJson: (data) => AiDiagnosis.fromJson(data),
      );
      
      if (response.isSuccess && response.data != null) {
        return response.data!;
      }
    } catch (e) {
      print('Get diagnosis by session error: $e');
    }
    return null;
  }
}

// Result wrapper
class DiagnosisResult {
  final bool success;
  final AiDiagnosisResponse? diagnosis;
  final String? error;

  DiagnosisResult._({required this.success, this.diagnosis, this.error});

  factory DiagnosisResult.success(AiDiagnosisResponse diagnosis) => 
      DiagnosisResult._(success: true, diagnosis: diagnosis);
  factory DiagnosisResult.error(String error) => 
      DiagnosisResult._(success: false, error: error);

  bool get isSuccess => success;
  bool get isError => !success;
}

// AI Diagnosis Response model (matches backend DTO)
class AiDiagnosisResponse {
  final String diagnosisId;
  final String sessionId;
  final List<DiagnosisItem> possibleDiagnoses;
  final List<String> symptoms;
  final List<RecommendationItem> recommendations;
  final double confidence;
  final String riskLevel;
  final String urgencyLevel;
  final DateTime createdAt;
  final Map<String, dynamic>? metadata;

  AiDiagnosisResponse({
    required this.diagnosisId,
    required this.sessionId,
    required this.possibleDiagnoses,
    required this.symptoms,
    required this.recommendations,
    required this.confidence,
    required this.riskLevel,
    required this.urgencyLevel,
    required this.createdAt,
    this.metadata,
  });

  factory AiDiagnosisResponse.fromJson(Map<String, dynamic> json) {
    return AiDiagnosisResponse(
      diagnosisId: json['diagnosisId'] ?? '',
      sessionId: json['sessionId'] ?? '',
      possibleDiagnoses: (json['possibleDiagnoses'] as List? ?? [])
          .map((item) => DiagnosisItem.fromJson(item))
          .toList(),
      symptoms: (json['symptoms'] as List? ?? [])
          .map((item) => item.toString())
          .toList(),
      recommendations: (json['recommendations'] as List? ?? [])
          .map((item) => RecommendationItem.fromJson(item))
          .toList(),
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      riskLevel: json['riskLevel'] ?? '',
      urgencyLevel: json['urgencyLevel'] ?? '',
      createdAt: DateTime.parse(json['createdAt']),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }
}

// Diagnosis item model
class DiagnosisItem {
  final String name;
  final String description;
  final double probability;
  final String severity;
  final List<String> relatedSymptoms;

  DiagnosisItem({
    required this.name,
    required this.description,
    required this.probability,
    required this.severity,
    required this.relatedSymptoms,
  });

  factory DiagnosisItem.fromJson(Map<String, dynamic> json) {
    return DiagnosisItem(
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      probability: (json['probability'] ?? 0.0).toDouble(),
      severity: json['severity'] ?? '',
      relatedSymptoms: (json['relatedSymptoms'] as List? ?? [])
          .map((item) => item.toString())
          .toList(),
    );
  }
}

// Recommendation item model
class RecommendationItem {
  final String type;
  final String title;
  final String description;
  final String priority;
  final List<String> actions;

  RecommendationItem({
    required this.type,
    required this.title,
    required this.description,
    required this.priority,
    required this.actions,
  });

  factory RecommendationItem.fromJson(Map<String, dynamic> json) {
    return RecommendationItem(
      type: json['type'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      priority: json['priority'] ?? '',
      actions: (json['actions'] as List? ?? [])
          .map((item) => item.toString())
          .toList(),
    );
  }
}

// AI Diagnosis entity model (matches backend entity)
class AiDiagnosis {
  final String id;
  final String sessionId;
  final String userId;
  final String diagnosisResult;
  final double confidence;
  final String riskLevel;
  final String urgencyLevel;
  final DateTime createdAt;
  final DateTime? updatedAt;

  AiDiagnosis({
    required this.id,
    required this.sessionId,
    required this.userId,
    required this.diagnosisResult,
    required this.confidence,
    required this.riskLevel,
    required this.urgencyLevel,
    required this.createdAt,
    this.updatedAt,
  });

  factory AiDiagnosis.fromJson(Map<String, dynamic> json) {
    return AiDiagnosis(
      id: json['id'] ?? '',
      sessionId: json['sessionId'] ?? '',
      userId: json['userId'] ?? '',
      diagnosisResult: json['diagnosisResult'] ?? '',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      riskLevel: json['riskLevel'] ?? '',
      urgencyLevel: json['urgencyLevel'] ?? '',
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null ? DateTime.parse(json['updatedAt']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sessionId': sessionId,
      'userId': userId,
      'diagnosisResult': diagnosisResult,
      'confidence': confidence,
      'riskLevel': riskLevel,
      'urgencyLevel': urgencyLevel,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
    };
  }
}
