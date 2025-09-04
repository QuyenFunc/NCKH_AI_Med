enum Gender { male, female, other }

enum SmokingStatus { never, former, current }

enum DrinkingFrequency { never, occasionally, regularly }

class UserProfile {
  final String userId;
  final int? birthYear;
  final Gender? gender;
  final String? province;
  
  // Medical History
  final List<String> chronicDiseases;
  final List<String> allergies;
  final List<String> currentMedications;
  
  // Lifestyle
  final SmokingStatus? smokingStatus;
  final DrinkingFrequency? drinkingFrequency;
  
  final DateTime? updatedAt;

  UserProfile({
    required this.userId,
    this.birthYear,
    this.gender,
    this.province,
    this.chronicDiseases = const [],
    this.allergies = const [],
    this.currentMedications = const [],
    this.smokingStatus,
    this.drinkingFrequency,
    this.updatedAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      userId: json['user_id'] ?? '',
      birthYear: json['birth_year'],
      gender: json['gender'] != null ? _parseGender(json['gender']) : null,
      province: json['province'],
      chronicDiseases: List<String>.from(json['chronic_diseases'] ?? []),
      allergies: List<String>.from(json['allergies'] ?? []),
      currentMedications: List<String>.from(json['current_medications'] ?? []),
      smokingStatus: json['smoking_status'] != null 
        ? _parseSmokingStatus(json['smoking_status']) 
        : null,
      drinkingFrequency: json['drinking_frequency'] != null 
        ? _parseDrinkingFrequency(json['drinking_frequency']) 
        : null,
      updatedAt: json['updated_at'] != null 
        ? DateTime.tryParse(json['updated_at'])
        : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'birth_year': birthYear,
      'gender': gender?.name,
      'province': province,
      'chronic_diseases': chronicDiseases,
      'allergies': allergies,
      'current_medications': currentMedications,
      'smoking_status': smokingStatus?.name,
      'drinking_frequency': drinkingFrequency?.name,
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  static Gender _parseGender(String gender) {
    switch (gender.toLowerCase()) {
      case 'male':
        return Gender.male;
      case 'female':
        return Gender.female;
      case 'other':
        return Gender.other;
      default:
        return Gender.other;
    }
  }

  static SmokingStatus _parseSmokingStatus(String status) {
    switch (status.toLowerCase()) {
      case 'never':
        return SmokingStatus.never;
      case 'former':
        return SmokingStatus.former;
      case 'current':
        return SmokingStatus.current;
      default:
        return SmokingStatus.never;
    }
  }

  static DrinkingFrequency _parseDrinkingFrequency(String frequency) {
    switch (frequency.toLowerCase()) {
      case 'never':
        return DrinkingFrequency.never;
      case 'occasionally':
        return DrinkingFrequency.occasionally;
      case 'regularly':
        return DrinkingFrequency.regularly;
      default:
        return DrinkingFrequency.never;
    }
  }

  // Helper methods
  int? get age {
    if (birthYear == null) return null;
    return DateTime.now().year - birthYear!;
  }

  String get genderDisplay {
    switch (gender) {
      case Gender.male:
        return 'Nam';
      case Gender.female:
        return 'Nữ';
      case Gender.other:
        return 'Khác';
      default:
        return 'Chưa cập nhật';
    }
  }

  String get smokingDisplay {
    switch (smokingStatus) {
      case SmokingStatus.never:
        return 'Không hút thuốc';
      case SmokingStatus.former:
        return 'Đã từng hút';
      case SmokingStatus.current:
        return 'Đang hút thuốc';
      default:
        return 'Chưa cập nhật';
    }
  }

  String get drinkingDisplay {
    switch (drinkingFrequency) {
      case DrinkingFrequency.never:
        return 'Không uống rượu';
      case DrinkingFrequency.occasionally:
        return 'Thỉnh thoảng';
      case DrinkingFrequency.regularly:
        return 'Thường xuyên';
      default:
        return 'Chưa cập nhật';
    }
  }

  UserProfile copyWith({
    String? userId,
    int? birthYear,
    Gender? gender,
    String? province,
    List<String>? chronicDiseases,
    List<String>? allergies,
    List<String>? currentMedications,
    SmokingStatus? smokingStatus,
    DrinkingFrequency? drinkingFrequency,
    DateTime? updatedAt,
  }) {
    return UserProfile(
      userId: userId ?? this.userId,
      birthYear: birthYear ?? this.birthYear,
      gender: gender ?? this.gender,
      province: province ?? this.province,
      chronicDiseases: chronicDiseases ?? this.chronicDiseases,
      allergies: allergies ?? this.allergies,
      currentMedications: currentMedications ?? this.currentMedications,
      smokingStatus: smokingStatus ?? this.smokingStatus,
      drinkingFrequency: drinkingFrequency ?? this.drinkingFrequency,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  bool get isComplete {
    return birthYear != null && 
           gender != null && 
           province != null;
  }
}
