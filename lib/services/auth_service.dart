import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../models/user_profile.dart';

class AuthService {
  static const String _userKey = 'current_user';
  static const String _profileKey = 'user_profile';
  static const String _tokenKey = 'auth_token';
  
  // Backend API endpoint (use 10.0.2.2 for Android emulator)
  static const String _baseUrl = 'http://10.0.2.2:8080/api';
  
  static AuthService? _instance;
  static AuthService get instance => _instance ??= AuthService._();
  AuthService._();

  User? _currentUser;
  UserProfile? _currentProfile;

  User? get currentUser => _currentUser;
  UserProfile? get currentProfile => _currentProfile;
  bool get isLoggedIn => _currentUser != null;

  // Initialize auth service
  Future<void> initialize() async {
    await _loadUserFromStorage();
    await _loadProfileFromStorage();
  }

  // Login with email and password
  Future<bool> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final userData = data['data'];
        final token = data['token'];
        
        _currentUser = User.fromJson(userData);
        await _saveUserToStorage(_currentUser!);
        await _saveToken(token);
        
        // Load user profile if exists
        await _loadUserProfile(_currentUser!.id);
        
        return true;
      }
      return false;
    } catch (e) {
      print('Login error: $e');
      return false;
    }
  }

  // Register new user
  Future<bool> register(String email, String password, String? name) async {
    try {
      print('Attempting to register user: $email');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'name': name ?? '',
        }),
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout - Backend không phản hồi');
        },
      );
      
      print('Register response status: ${response.statusCode}');
      print('Register response body: ${response.body}');
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = json.decode(response.body);
        final userData = data['data'];
        final token = data['token'];
        
        _currentUser = User.fromJson(userData);
        await _saveUserToStorage(_currentUser!);
        await _saveToken(token);
        print('Register successful for user: ${_currentUser!.email}');
        return true;
      } else {
        print('Register failed with status: ${response.statusCode}');
        print('Error response: ${response.body}');
        return false;
      }
    } catch (e) {
      print('Register error: $e');
      return false;
    }
  }

  // Save user profile
  Future<bool> saveProfile(UserProfile profile) async {
    try {
      final token = await _getToken();
      if (token == null) return false;

      final response = await http.post(
        Uri.parse('$_baseUrl/users/profile'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode(profile.toJson()),
      );
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        _currentProfile = profile;
        await _saveProfileToStorage(profile);
        
        // Update user's profile complete status
        if (_currentUser != null && profile.isComplete) {
          _currentUser = _currentUser!.copyWith(isProfileComplete: true);
          await _saveUserToStorage(_currentUser!);
        }
        
        return true;
      }
      return false;
    } catch (e) {
      print('Save profile error: $e');
      return false;
    }
  }

  // Logout
  Future<void> logout() async {
    _currentUser = null;
    _currentProfile = null;
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
    await prefs.remove(_profileKey);
    await prefs.remove(_tokenKey);
  }

  // Private methods

  Future<void> _saveUserToStorage(User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, json.encode(user.toJson()));
  }

  Future<void> _loadUserFromStorage() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString(_userKey);
    if (userJson != null) {
      _currentUser = User.fromJson(json.decode(userJson));
    }
  }

  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  Future<void> _saveProfileToStorage(UserProfile profile) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_profileKey, json.encode(profile.toJson()));
  }

  Future<void> _loadProfileFromStorage() async {
    final prefs = await SharedPreferences.getInstance();
    final profileJson = prefs.getString(_profileKey);
    if (profileJson != null) {
      _currentProfile = UserProfile.fromJson(json.decode(profileJson));
    }
  }

  Future<void> _loadUserProfile(String userId) async {
    try {
      final token = await _getToken();
      if (token == null) return;

      final response = await http.get(
        Uri.parse('$_baseUrl/users/me'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final profileData = data['data']['profile'];
        if (profileData != null) {
          _currentProfile = UserProfile.fromJson(profileData);
          await _saveProfileToStorage(_currentProfile!);
        }
      }
    } catch (e) {
      print('Load profile error: $e');
    }
  }

}
