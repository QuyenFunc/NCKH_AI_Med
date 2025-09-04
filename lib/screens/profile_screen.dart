import 'package:flutter/material.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text(
          'Hồ sơ',
          style: TextStyle(
            fontWeight: FontWeight.w600,
            color: Colors.black87,
          ),
        ),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings, color: Colors.black87),
            onPressed: () {
              // TODO: Navigate to settings
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Profile Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24.0),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16.0),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10.0,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                children: [
                  // Avatar
                  Container(
                    width: 80.0,
                    height: 80.0,
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor.withOpacity(0.1),
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: Theme.of(context).primaryColor.withOpacity(0.3),
                        width: 2.0,
                      ),
                    ),
                    child: Icon(
                      Icons.person,
                      size: 40.0,
                      color: Theme.of(context).primaryColor,
                    ),
                  ),
                  const SizedBox(height: 16.0),
                  
                  // Name
                  const Text(
                    'Người dùng',
                    style: TextStyle(
                      fontSize: 20.0,
                      fontWeight: FontWeight.w600,
                      color: Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 4.0),
                  
                  // Email
                  Text(
                    'user@example.com',
                    style: TextStyle(
                      fontSize: 14.0,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 16.0),
                  
                  // Edit Profile Button
                  ElevatedButton(
                    onPressed: () {
                      // TODO: Navigate to edit profile
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Theme.of(context).primaryColor,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(24.0),
                      ),
                    ),
                    child: const Text(
                      'Chỉnh sửa hồ sơ',
                      style: TextStyle(fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 24.0),
            
            // Health Stats (Coming Soon)
            _buildSectionCard(
              title: 'Thống kê sức khỏe',
              icon: Icons.bar_chart,
              items: [
                _buildStatItem('Số lần chẩn đoán', '0', Icons.healing),
                _buildStatItem('Bài viết đã đọc', '0', Icons.article),
                _buildStatItem('Ngày sử dụng', '1 ngày', Icons.calendar_today),
              ],
            ),
            
            const SizedBox(height: 16.0),
            
            // Quick Actions
            _buildSectionCard(
              title: 'Thao tác nhanh',
              icon: Icons.flash_on,
              items: [
                _buildActionItem(
                  'Lịch sử chẩn đoán',
                  'Xem lại các cuộc trò chuyện với Dia5',
                  Icons.history,
                  () {
                    // TODO: Navigate to chat history
                  },
                ),
                _buildActionItem(
                  'Bài viết đã lưu',
                  'Danh sách tin tức y tế bạn đã bookmark',
                  Icons.bookmark,
                  () {
                    // TODO: Navigate to saved articles
                  },
                ),
                _buildActionItem(
                  'Cài đặt thông báo',
                  'Quản lý thông báo về tin tức y tế mới',
                  Icons.notifications,
                  () {
                    // TODO: Navigate to notification settings
                  },
                ),
              ],
            ),
            
            const SizedBox(height: 16.0),
            
            // App Info
            _buildSectionCard(
              title: 'Thông tin ứng dụng',
              icon: Icons.info,
              items: [
                _buildActionItem(
                  'Về Dia5',
                  'Tìm hiểu về trợ lý AI chẩn đoán y tế',
                  Icons.medical_services,
                  () {
                    _showAboutDialog();
                  },
                ),
                _buildActionItem(
                  'Chính sách bảo mật',
                  'Cam kết bảo vệ thông tin cá nhân của bạn',
                  Icons.privacy_tip,
                  () {
                    // TODO: Show privacy policy
                  },
                ),
                _buildActionItem(
                  'Điều khoản sử dụng',
                  'Quy định và điều kiện sử dụng ứng dụng',
                  Icons.description,
                  () {
                    // TODO: Show terms of service
                  },
                ),
                _buildActionItem(
                  'Phiên bản',
                  'v1.0.0',
                  Icons.update,
                  null,
                ),
              ],
            ),
            
            const SizedBox(height: 32.0),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionCard({
    required String title,
    required IconData icon,
    required List<Widget> items,
  }) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16.0),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10.0,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Section Header
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Row(
              children: [
                Icon(
                  icon,
                  color: Theme.of(context).primaryColor,
                  size: 24.0,
                ),
                const SizedBox(width: 12.0),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18.0,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
              ],
            ),
          ),
          
          // Section Items
          ...items,
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(left: 20.0, right: 20.0, bottom: 16.0),
      child: Row(
        children: [
          Icon(
            icon,
            color: Colors.grey.shade600,
            size: 20.0,
          ),
          const SizedBox(width: 12.0),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 16.0,
                color: Colors.grey.shade700,
              ),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontSize: 16.0,
              fontWeight: FontWeight.w600,
              color: Colors.black87,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionItem(
    String title,
    String subtitle,
    IconData icon,
    VoidCallback? onTap,
  ) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.only(left: 20.0, right: 20.0, bottom: 16.0),
        child: Row(
          children: [
            Icon(
              icon,
              color: Colors.grey.shade600,
              size: 20.0,
            ),
            const SizedBox(width: 12.0),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16.0,
                      fontWeight: FontWeight.w500,
                      color: Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 2.0),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 14.0,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
            ),
            if (onTap != null)
              Icon(
                Icons.arrow_forward_ios,
                color: Colors.grey.shade400,
                size: 16.0,
              ),
          ],
        ),
      ),
    );
  }

  void _showAboutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.medical_services,
              color: Theme.of(context).primaryColor,
            ),
            const SizedBox(width: 8.0),
            const Text('Về Dia5'),
          ],
        ),
        content: const Text(
          'Dia5 là trợ lý AI chẩn đoán y tế được phát triển để hỗ trợ người dùng '
          'phân tích triệu chứng và đưa ra chẩn đoán sơ bộ.\n\n'
          'Lưu ý: Dia5 chỉ hỗ trợ chẩn đoán sơ bộ và không thay thế ý kiến '
          'của bác sĩ chuyên khoa.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Đóng'),
          ),
        ],
      ),
    );
  }
}
