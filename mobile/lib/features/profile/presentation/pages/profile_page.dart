import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import 'edit_profile_page.dart';
import 'change_password_page.dart';
import 'notification_settings_page.dart';
import '../../../../core/network/api_client.dart';
import '../../data/models/profile_model.dart';
import '../../data/repositories/profile_repository.dart';
import '../../data/services/profile_api_service.dart';

class _NoStretchScrollBehavior extends ScrollBehavior {
  const _NoStretchScrollBehavior();

  @override
  ScrollPhysics getScrollPhysics(BuildContext context) {
    return const ClampingScrollPhysics();
  }
}

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  late final ProfileRepository _profileRepository;

  ProfileModel? _profile;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();

    final apiClient = ApiClient();

    final profileApiService = ProfileApiService(apiClient: apiClient);

    _profileRepository = ProfileRepository(
      profileApiService: profileApiService,
    );

    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final profile = await _profileRepository.getProfile();

      if (!mounted) {
        return;
      }

      setState(() {
        _profile = profile;
        _isLoading = false;
      });
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _errorMessage = error.toString();
        _isLoading = false;
      });
    }
  }

  String _formatDateOfBirth(DateTime date) {
    const thaiMonths = [
      'มกราคม',
      'กุมภาพันธ์',
      'มีนาคม',
      'เมษายน',
      'พฤษภาคม',
      'มิถุนายน',
      'กรกฎาคม',
      'สิงหาคม',
      'กันยายน',
      'ตุลาคม',
      'พฤศจิกายน',
      'ธันวาคม',
    ];

    final thaiYear = date.year + 543;

    return '${date.day} ${thaiMonths[date.month - 1]} $thaiYear';
  }

  String _formatGender(String gender) {
    switch (gender) {
      case 'male':
        return 'ชาย';
      case 'female':
        return 'หญิง';
      case 'other':
        return 'อื่น ๆ';
      default:
        return gender;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        backgroundColor: AppTheme.surfaceColor,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        automaticallyImplyLeading: false,
        centerTitle: true,
        title: const Text(
          'โปรไฟล์',
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1),
          child: Divider(height: 1, thickness: 1, color: Color(0xFFE8ECF2)),
        ),
      ),
      body: SafeArea(child: _buildBody(context)),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_profile == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.error_outline_rounded,
                size: 42,
                color: AppTheme.errorColor,
              ),
              const SizedBox(height: 12),
              const Text(
                'ไม่สามารถโหลดข้อมูลโปรไฟล์ได้',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                _errorMessage ?? 'กรุณาลองใหม่อีกครั้ง',
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 12,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _isLoading = true;
                    _errorMessage = null;
                  });

                  _loadProfile();
                },
                child: const Text(
                  'ลองอีกครั้ง',
                  style: TextStyle(fontFamily: 'Kanit'),
                ),
              ),
            ],
          ),
        ),
      );
    }

    return ScrollConfiguration(
      behavior: const _NoStretchScrollBehavior(),
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 22, 20, 40),
        child: Column(
          children: [
            _buildProfileHeader(),
            const SizedBox(height: 24),
            _buildSectionTitle('ข้อมูลส่วนตัว'),
            const SizedBox(height: 10),
            _buildPersonalInformationCard(),
            const SizedBox(height: 20),
            _buildSectionTitle('ข้อมูลติดต่อ'),
            const SizedBox(height: 10),
            _buildContactInformationCard(),
            const SizedBox(height: 20),
            _buildSectionTitle('การตั้งค่า'),
            const SizedBox(height: 10),
            _buildSettingsCard(context),
            const SizedBox(height: 18),
            _buildLogoutButton(context),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileHeader() {
    return Column(
      children: [
        Container(
          width: 88,
          height: 88,
          decoration: BoxDecoration(
            color: AppTheme.primaryBackgroundColor,
            shape: BoxShape.circle,
            border: Border.all(color: Colors.white, width: 4),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.08),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Icon(
            Icons.person_rounded,
            size: 50,
            color: AppTheme.primaryColor,
          ),
        ),
        const SizedBox(height: 12),
        Text(
          'คุณ ${_profile!.firstName} ${_profile!.lastName}',
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontFamily: 'Kanit',
            fontSize: 20,
            fontWeight: FontWeight.w700,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        const SizedBox(height: 4),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
          decoration: BoxDecoration(
            color: const Color(0xFFF0F1F4),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            'Username: ${_profile!.username}',
            style: const TextStyle(
              fontFamily: 'Kanit',
              fontSize: 11,
              fontWeight: FontWeight.w400,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSectionTitle(String title) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Text(
        title,
        style: const TextStyle(
          fontFamily: 'Kanit',
          fontSize: 17,
          fontWeight: FontWeight.w700,
          color: AppTheme.textPrimaryColor,
        ),
      ),
    );
  }

  Widget _buildPersonalInformationCard() {
    return _buildCard(
      child: Column(
        children: [
          _buildInformationRow(
            icon: Icons.cake_outlined,
            label: 'วันเกิด',
            value: _formatDateOfBirth(_profile!.dateOfBirth),
          ),
          const SizedBox(height: 17),
          _buildInformationRow(
            icon: Icons.male_rounded,
            label: 'เพศ',
            value: _formatGender(_profile!.gender),
          ),
        ],
      ),
    );
  }

  Widget _buildContactInformationCard() {
    return _buildCard(
      child: Column(
        children: [
          _buildInformationRow(
            icon: Icons.phone_outlined,
            label: 'เบอร์โทรศัพท์',
            value: _profile!.phoneNumber,
          ),
          const SizedBox(height: 17),
          _buildInformationRow(
            icon: Icons.email_outlined,
            label: 'อีเมล',
            value: _profile!.email,
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsCard(BuildContext context) {
    return _buildCard(
      child: Column(
        children: [
          _buildSettingItem(
            icon: Icons.person_outline_rounded,
            title: 'แก้ไขข้อมูลส่วนตัว',
            onTap: () async {
              final updatedProfile = await Navigator.of(context)
                  .push<ProfileModel>(
                    MaterialPageRoute(builder: (_) => const EditProfilePage()),
                  );

              if (!mounted || updatedProfile == null) {
                return;
              }

              setState(() {
                _profile = updatedProfile;
              });
            },
          ),
          _buildSettingDivider(),
          _buildSettingItem(
            icon: Icons.lock_outline_rounded,
            title: 'เปลี่ยนรหัสผ่าน',
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const ChangePasswordPage()),
              );
            },
          ),
          _buildSettingDivider(),
          _buildSettingItem(
            icon: Icons.notifications_none_rounded,
            title: 'ตั้งค่าการแจ้งเตือน',
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => const NotificationSettingsPage(),
                ),
              );
            },
          ),
          _buildSettingDivider(),
          _buildSettingItem(
            icon: Icons.support_agent_rounded,
            title: 'ช่วยเหลือและสนับสนุน',
            onTap: () {
              _showSupportDialog(context);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSettingItem({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 15),
        child: Row(
          children: [
            SizedBox(
              width: 25,
              child: Icon(icon, size: 20, color: AppTheme.textSecondaryColor),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
            ),
            const Icon(
              Icons.chevron_right_rounded,
              size: 21,
              color: AppTheme.textSecondaryColor,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSettingDivider() {
    return const Padding(
      padding: EdgeInsets.only(left: 49),
      child: Divider(height: 1, thickness: 1, color: Color(0xFFE9EDF2)),
    );
  }

  Widget _buildInformationRow({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      children: [
        Container(
          width: 34,
          height: 34,
          decoration: BoxDecoration(
            color: AppTheme.primaryBackgroundColor,
            shape: BoxShape.circle,
          ),
          child: Icon(icon, size: 18, color: AppTheme.primaryColor),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 11,
                  fontWeight: FontWeight.w400,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCard({
    required Widget child,
    EdgeInsetsGeometry padding = const EdgeInsets.all(15),
  }) {
    return Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: AppTheme.textSecondaryColor.withValues(alpha: 0.08),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.white.withValues(alpha: 0.9),
            blurRadius: 6,
            offset: const Offset(0, -2),
          ),
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.035),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: child,
    );
  }

  Widget _buildLogoutButton(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton.icon(
        onPressed: () {
          _showLogoutDialog(context);
        },
        icon: const Icon(Icons.logout_rounded, size: 17),
        label: const Text(
          'ออกจากระบบ',
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        style: ElevatedButton.styleFrom(
          elevation: 4,
          shadowColor: Colors.black.withValues(alpha: 0.15),
          backgroundColor: const Color(0xFFFFDCD8),
          foregroundColor: const Color.fromARGB(255, 189, 56, 47),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }

  Future<void> _showLogoutDialog(BuildContext context) async {
    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.symmetric(horizontal: 40),
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(20, 22, 20, 18),
            decoration: BoxDecoration(
              color: const Color(0xFFF8F8FC),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: const BoxDecoration(
                    color: Color(0xFFFFE8E6),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.logout_rounded,
                    size: 28,
                    color: Color(0xFFD94B42),
                  ),
                ),
                const SizedBox(height: 18),
                const Text(
                  'ออกจากระบบ',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 17,
                    fontWeight: FontWeight.w600,
                    height: 1.3,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'คุณต้องการออกจากระบบใช่หรือไม่',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 12,
                    fontWeight: FontWeight.w400,
                    height: 1.4,
                    color: AppTheme.textSecondaryColor,
                  ),
                ),
                const SizedBox(height: 20),
                Row(
                  children: [
                    Expanded(
                      child: SizedBox(
                        height: 48,
                        child: OutlinedButton(
                          onPressed: () {
                            Navigator.of(dialogContext).pop();
                          },
                          style: OutlinedButton.styleFrom(
                            foregroundColor: AppTheme.textSecondaryColor,
                            side: BorderSide(
                              color: AppTheme.textSecondaryColor.withValues(
                                alpha: 0.25,
                              ),
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: const Text(
                            'ยกเลิก',
                            style: TextStyle(
                              fontFamily: 'Kanit',
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: SizedBox(
                        height: 48,
                        child: ElevatedButton(
                          onPressed: () {
                            Navigator.of(dialogContext).pop();

                            Navigator.of(context).pushNamedAndRemoveUntil(
                              '/login',
                              (route) => false,
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            elevation: 3,
                            shadowColor: Colors.black.withValues(alpha: 0.15),
                            backgroundColor: const Color(0xFFD94B42),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: const Text(
                            'ออกจากระบบ',
                            style: TextStyle(
                              fontFamily: 'Kanit',
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

Future<void> _showSupportDialog(BuildContext context) async {
  await showDialog<void>(
    context: context,
    barrierDismissible: true,
    builder: (dialogContext) {
      return Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: const EdgeInsets.symmetric(horizontal: 40),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.fromLTRB(20, 22, 20, 18),
          decoration: BoxDecoration(
            color: const Color(0xFFF8F8FC),
            borderRadius: BorderRadius.circular(24),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: const BoxDecoration(
                  color: Color(0xFFE8EEFF),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.support_agent_rounded,
                  size: 30,
                  color: Color(0xFF5578D9),
                ),
              ),
              const SizedBox(height: 18),
              const Text(
                'ช่วยเหลือและสนับสนุน',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                  height: 1.3,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'หากพบปัญหาหรือต้องการสอบถามข้อมูล '
                'สามารถติดต่อเจ้าหน้าที่โรงพยาบาลได้',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 12,
                  fontWeight: FontWeight.w400,
                  height: 1.5,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
              const SizedBox(height: 20),

              // โทรติดต่อเจ้าหน้าที่
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton.icon(
                  onPressed: () {
                    // TODO: เชื่อมหมายเลขโทรศัพท์จริงภายหลัง
                  },
                  icon: const Icon(Icons.phone_outlined, size: 18),
                  label: const Text(
                    'โทรติดต่อเจ้าหน้าที่',
                    style: TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    elevation: 0,
                    backgroundColor: AppTheme.primaryColor,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 10),

              // ส่งอีเมล
              SizedBox(
                width: double.infinity,
                height: 48,
                child: OutlinedButton.icon(
                  onPressed: () {
                    // TODO: เชื่อมอีเมลจริงภายหลัง
                  },
                  icon: const Icon(Icons.email_outlined, size: 18),
                  label: const Text(
                    'ส่งอีเมล',
                    style: TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppTheme.primaryColor,
                    side: BorderSide(
                      color: AppTheme.primaryColor.withValues(alpha: 0.35),
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 10),

              SizedBox(
                width: double.infinity,
                height: 40,
                child: TextButton(
                  onPressed: () {
                    Navigator.of(dialogContext).pop();
                  },
                  style: TextButton.styleFrom(
                    foregroundColor: AppTheme.textSecondaryColor,
                  ),
                  child: const Text(
                    'ปิด',
                    style: TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    },
  );
}
