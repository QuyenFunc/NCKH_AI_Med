import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../models/user_profile.dart';
import 'profile_setup_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final PageController _pageController = PageController();
  int _currentStep = 0;
  bool _isLoading = false;

  // Step 1: Account Creation
  final _step1FormKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _nameController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  // Step 2: Basic Information
  final _step2FormKey = GlobalKey<FormState>();
  int? _birthYear;
  Gender? _selectedGender;
  String? _selectedProvince;

  // Vietnamese provinces with IDs
  final Map<String, int> _provinces = {
    'An Giang': 1, 'Bà Rịa - Vũng Tàu': 2, 'Bạc Liêu': 3, 'Bắc Giang': 4, 'Bắc Kạn': 5,
    'Bắc Ninh': 6, 'Bến Tre': 7, 'Bình Dương': 8, 'Bình Định': 9, 'Bình Phước': 10,
    'Bình Thuận': 11, 'Cà Mau': 12, 'Cao Bằng': 13, 'Cần Thơ': 14, 'Đà Nẵng': 15,
    'Đắk Lắk': 16, 'Đắk Nông': 17, 'Điện Biên': 18, 'Đồng Nai': 19, 'Đồng Tháp': 20,
    'Gia Lai': 21, 'Hà Giang': 22, 'Hà Nam': 23, 'Hà Nội': 24, 'Hà Tĩnh': 25,
    'Hải Dương': 26, 'Hải Phòng': 27, 'Hậu Giang': 28, 'Hòa Bình': 29, 'Hồ Chí Minh': 30,
    'Hưng Yên': 31, 'Khánh Hòa': 32, 'Kiên Giang': 33, 'Kon Tum': 34, 'Lai Châu': 35,
    'Lạng Sơn': 36, 'Lào Cai': 37, 'Lâm Đồng': 38, 'Long An': 39, 'Nam Định': 40,
    'Nghệ An': 41, 'Ninh Bình': 42, 'Ninh Thuận': 43, 'Phú Thọ': 44, 'Phú Yên': 45,
    'Quảng Bình': 46, 'Quảng Nam': 47, 'Quảng Ngãi': 48, 'Quảng Ninh': 49, 'Quảng Trị': 50,
    'Sóc Trăng': 51, 'Sơn La': 52, 'Tây Ninh': 53, 'Thái Bình': 54, 'Thái Nguyên': 55,
    'Thanh Hóa': 56, 'Thừa Thiên Huế': 57, 'Tiền Giang': 58, 'Trà Vinh': 59, 'Tuyên Quang': 60,
    'Vĩnh Long': 61, 'Vĩnh Phúc': 62, 'Yên Bái': 63
  };

  @override
  void dispose() {
    _pageController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _nextStep() async {
    if (_currentStep == 0) {
      if (_step1FormKey.currentState!.validate()) {
        setState(() {
          _currentStep = 1;
        });
        _pageController.nextPage(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
        );
      }
    } else if (_currentStep == 1) {
      if (_step2FormKey.currentState!.validate()) {
        await _register();
      }
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() {
        _currentStep--;
      });
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  Future<void> _register() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Register user account
      final result = await AuthService.instance.register(
        _emailController.text.trim(),
        _passwordController.text,
        _confirmPasswordController.text,
        _nameController.text.trim().isNotEmpty ? _nameController.text.trim() : null,
      );

      if (result.isSuccess && mounted) {
        // Save basic profile information
        final user = AuthService.instance.currentUser!;
        final profile = UserProfile(
          userId: user.id,
          name: user.name, // Include name to help with profile completion
          birthYear: _birthYear,
          gender: _selectedGender,
          provinceId: _selectedProvince != null ? _provinces[_selectedProvince] : null,
        );

        final profileResult = await AuthService.instance.saveProfile(profile);
        
        if (profileResult.isSuccess) {
          // Navigate to profile setup for medical information
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const ProfileSetupScreen()),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Lỗi lưu profile: ${profileResult.error}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.error ?? 'Đăng ký thất bại. Vui lòng thử lại.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Lỗi đăng ký: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }

    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black87),
          onPressed: () {
            if (_currentStep > 0) {
              _previousStep();
            } else {
              Navigator.of(context).pop();
            }
          },
        ),
        title: Text(
          'Đăng ký tài khoản',
          style: const TextStyle(
            color: Colors.black87,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: Column(
        children: [
          // Progress Indicator
          Container(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                _buildStepIndicator(0, 'Tài khoản'),
                Expanded(
                  child: Container(
                    height: 2.0,
                    color: _currentStep >= 1 
                      ? Theme.of(context).primaryColor 
                      : Colors.grey.shade300,
                  ),
                ),
                _buildStepIndicator(1, 'Thông tin'),
              ],
            ),
          ),
          
          // Content
          Expanded(
            child: PageView(
              controller: _pageController,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildStep1(),
                _buildStep2(),
              ],
            ),
          ),
          
          // Bottom Button
          Container(
            padding: const EdgeInsets.all(24.0),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _nextStep,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Theme.of(context).primaryColor,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16.0),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12.0),
                  ),
                ),
                child: _isLoading
                  ? const SizedBox(
                      height: 20.0,
                      width: 20.0,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.0,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : Text(
                      _currentStep == 1 ? 'Hoàn thành đăng ký' : 'Tiếp tục',
                      style: const TextStyle(
                        fontSize: 16.0,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStepIndicator(int step, String label) {
    final isActive = _currentStep >= step;
    return Row(
      children: [
        Container(
          width: 32.0,
          height: 32.0,
          decoration: BoxDecoration(
            color: isActive ? Theme.of(context).primaryColor : Colors.grey.shade300,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              '${step + 1}',
              style: TextStyle(
                color: isActive ? Colors.white : Colors.grey.shade600,
                fontWeight: FontWeight.w600,
                fontSize: 14.0,
              ),
            ),
          ),
        ),
        const SizedBox(width: 8.0),
        Text(
          label,
          style: TextStyle(
            color: isActive ? Theme.of(context).primaryColor : Colors.grey.shade600,
            fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
            fontSize: 14.0,
          ),
        ),
      ],
    );
  }

  Widget _buildStep1() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Form(
        key: _step1FormKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Tạo tài khoản',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 8.0),
            Text(
              'Nhập thông tin để tạo tài khoản Dia5 của bạn',
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 16.0,
              ),
            ),
            const SizedBox(height: 32.0),
            
            // Name Field (Optional)
            TextFormField(
              controller: _nameController,
              textInputAction: TextInputAction.next,
              decoration: InputDecoration(
                labelText: 'Họ và tên (không bắt buộc)',
                hintText: 'Nhập họ và tên của bạn',
                prefixIcon: const Icon(Icons.person_outlined),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12.0),
                ),
              ),
            ),
            
            const SizedBox(height: 16.0),
            
            // Email Field
            TextFormField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              textInputAction: TextInputAction.next,
              decoration: InputDecoration(
                labelText: 'Email *',
                hintText: 'Nhập địa chỉ email của bạn',
                prefixIcon: const Icon(Icons.email_outlined),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12.0),
                ),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Vui lòng nhập email';
                }
                if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                  return 'Email không hợp lệ';
                }
                return null;
              },
            ),
            
            const SizedBox(height: 16.0),
            
            // Password Field
            TextFormField(
              controller: _passwordController,
              obscureText: _obscurePassword,
              textInputAction: TextInputAction.next,
              decoration: InputDecoration(
                labelText: 'Mật khẩu *',
                hintText: 'Tạo mật khẩu mạnh',
                prefixIcon: const Icon(Icons.lock_outlined),
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                  ),
                  onPressed: () {
                    setState(() {
                      _obscurePassword = !_obscurePassword;
                    });
                  },
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12.0),
                ),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Vui lòng nhập mật khẩu';
                }
                if (value.length < 6) {
                  return 'Mật khẩu phải có ít nhất 6 ký tự';
                }
                return null;
              },
            ),
            
            const SizedBox(height: 16.0),
            
            // Confirm Password Field
            TextFormField(
              controller: _confirmPasswordController,
              obscureText: _obscureConfirmPassword,
              textInputAction: TextInputAction.done,
              decoration: InputDecoration(
                labelText: 'Xác nhận mật khẩu *',
                hintText: 'Nhập lại mật khẩu',
                prefixIcon: const Icon(Icons.lock_outlined),
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscureConfirmPassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                  ),
                  onPressed: () {
                    setState(() {
                      _obscureConfirmPassword = !_obscureConfirmPassword;
                    });
                  },
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12.0),
                ),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Vui lòng xác nhận mật khẩu';
                }
                if (value != _passwordController.text) {
                  return 'Mật khẩu xác nhận không khớp';
                }
                return null;
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStep2() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Form(
        key: _step2FormKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Thông tin cơ bản',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 8.0),
            Text(
              'Những thông tin này giúp AI đưa ra chẩn đoán chính xác hơn',
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 16.0,
              ),
            ),
            const SizedBox(height: 32.0),
            
            // Birth Year
            TextFormField(
              keyboardType: TextInputType.number,
              textInputAction: TextInputAction.next,
              decoration: InputDecoration(
                labelText: 'Năm sinh *',
                hintText: 'Ví dụ: 1990',
                prefixIcon: const Icon(Icons.calendar_today_outlined),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12.0),
                ),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Vui lòng nhập năm sinh';
                }
                final year = int.tryParse(value);
                if (year == null) {
                  return 'Năm sinh không hợp lệ';
                }
                final currentYear = DateTime.now().year;
                if (year < 1900 || year > currentYear) {
                  return 'Năm sinh phải từ 1900 đến $currentYear';
                }
                return null;
              },
              onChanged: (value) {
                _birthYear = int.tryParse(value);
              },
            ),
            
            const SizedBox(height: 16.0),
            
            // Gender
            DropdownButtonFormField<Gender>(
              value: _selectedGender,
              decoration: InputDecoration(
                labelText: 'Giới tính *',
                prefixIcon: const Icon(Icons.person_outlined),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12.0),
                ),
              ),
              items: Gender.values.map((gender) {
                String label = '';
                switch (gender) {
                  case Gender.male:
                    label = 'Nam';
                    break;
                  case Gender.female:
                    label = 'Nữ';
                    break;
                  case Gender.other:
                    label = 'Khác';
                    break;
                }
                return DropdownMenuItem(
                  value: gender,
                  child: Text(label),
                );
              }).toList(),
              onChanged: (gender) {
                setState(() {
                  _selectedGender = gender;
                });
              },
              validator: (value) {
                if (value == null) {
                  return 'Vui lòng chọn giới tính';
                }
                return null;
              },
            ),
            
            const SizedBox(height: 16.0),
            
            // Province
            DropdownButtonFormField<String>(
              value: _selectedProvince,
              decoration: InputDecoration(
                labelText: 'Tỉnh/Thành phố *',
                prefixIcon: const Icon(Icons.location_on_outlined),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12.0),
                ),
              ),
              items: _provinces.keys.map((province) {
                return DropdownMenuItem(
                  value: province,
                  child: Text(province),
                );
              }).toList(),
              onChanged: (province) {
                setState(() {
                  _selectedProvince = province;
                });
              },
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Vui lòng chọn tỉnh/thành phố';
                }
                return null;
              },
            ),
            
            const SizedBox(height: 24.0),
            
            Container(
              padding: const EdgeInsets.all(16.0),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(12.0),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: Colors.blue.shade700,
                    size: 20.0,
                  ),
                  const SizedBox(width: 12.0),
                  Expanded(
                    child: Text(
                      'Những thông tin này sẽ giúp AI hiểu rõ hơn về ngữ cảnh sức khỏe của bạn để đưa ra lời khuyên chính xác.',
                      style: TextStyle(
                        color: Colors.blue.shade700,
                        fontSize: 14.0,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
