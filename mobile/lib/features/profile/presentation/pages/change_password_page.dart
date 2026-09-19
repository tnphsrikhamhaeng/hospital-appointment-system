import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import '../../../../core/network/api_client.dart';
import '../../data/repositories/profile_repository.dart';
import '../../data/services/profile_api_service.dart';

class ChangePasswordPage extends StatefulWidget {
  const ChangePasswordPage({super.key});

  @override
  State<ChangePasswordPage> createState() => _ChangePasswordPageState();
}

class _ChangePasswordPageState extends State<ChangePasswordPage> {
  final TextEditingController _currentPasswordController =
      TextEditingController();

  final TextEditingController _newPasswordController = TextEditingController();

  final TextEditingController _confirmPasswordController =
      TextEditingController();

  late final ProfileRepository _profileRepository;

  bool _obscureCurrentPassword = true;
  bool _obscureNewPassword = true;
  bool _obscureConfirmPassword = true;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();

    final apiClient = ApiClient();

    final profileApiService = ProfileApiService(apiClient: apiClient);

    _profileRepository = ProfileRepository(
      profileApiService: profileApiService,
    );
  }

  @override
  void dispose() {
    _currentPasswordController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
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
        centerTitle: true,
        leading: IconButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 19),
          color: AppTheme.textPrimaryColor,
        ),
        title: const Text(
          'เปลี่ยนรหัสผ่าน',
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
      body: SafeArea(
        child: SingleChildScrollView(
          keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
          padding: const EdgeInsets.fromLTRB(20, 22, 20, 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDescription(),
              const SizedBox(height: 22),
              _buildPasswordCard(),
              const SizedBox(height: 28),
              _buildChangePasswordButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDescription() {
    return const Text(
      'กรอกรหัสผ่านเดิมและตั้งรหัสผ่านใหม่ของคุณ',
      style: TextStyle(
        fontFamily: 'Kanit',
        fontSize: 13,
        fontWeight: FontWeight.w400,
        color: AppTheme.textSecondaryColor,
      ),
    );
  }

  Widget _buildPasswordCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(17),
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
      child: Column(
        children: [
          _buildPasswordField(
            controller: _currentPasswordController,
            label: 'รหัสผ่านปัจจุบัน',
            hintText: 'กรอกรหัสผ่านปัจจุบัน',
            obscureText: _obscureCurrentPassword,
            onToggleVisibility: () {
              setState(() {
                _obscureCurrentPassword = !_obscureCurrentPassword;
              });
            },
          ),
          const SizedBox(height: 18),
          _buildPasswordField(
            controller: _newPasswordController,
            label: 'รหัสผ่านใหม่',
            hintText: 'กรอกรหัสผ่านใหม่',
            obscureText: _obscureNewPassword,
            onToggleVisibility: () {
              setState(() {
                _obscureNewPassword = !_obscureNewPassword;
              });
            },
          ),
          const SizedBox(height: 18),
          _buildPasswordField(
            controller: _confirmPasswordController,
            label: 'ยืนยันรหัสผ่านใหม่',
            hintText: 'กรอกรหัสผ่านใหม่อีกครั้ง',
            obscureText: _obscureConfirmPassword,
            onToggleVisibility: () {
              setState(() {
                _obscureConfirmPassword = !_obscureConfirmPassword;
              });
            },
          ),
          const SizedBox(height: 16),
          _buildPasswordHint(),
        ],
      ),
    );
  }

  Widget _buildPasswordField({
    required TextEditingController controller,
    required String label,
    required String hintText,
    required bool obscureText,
    required VoidCallback onToggleVisibility,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontFamily: 'Kanit',
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        const SizedBox(height: 7),
        Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(13),
            boxShadow: [
              BoxShadow(
                color: Colors.white.withValues(alpha: 0.9),
                blurRadius: 6,
                offset: const Offset(0, -2),
              ),
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.035),
                blurRadius: 8,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: TextField(
            controller: controller,
            obscureText: obscureText,
            style: const TextStyle(
              fontFamily: 'Kanit',
              fontSize: 13,
              fontWeight: FontWeight.w400,
              color: AppTheme.textPrimaryColor,
            ),
            decoration: InputDecoration(
              prefixIcon: const Icon(
                Icons.lock_outline_rounded,
                size: 19,
                color: AppTheme.textSecondaryColor,
              ),
              suffixIcon: IconButton(
                onPressed: onToggleVisibility,
                icon: Icon(
                  obscureText
                      ? Icons.visibility_off_outlined
                      : Icons.visibility_outlined,
                  size: 19,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
              hintText: hintText,
              hintStyle: const TextStyle(
                fontFamily: 'Kanit',
                fontSize: 13,
                fontWeight: FontWeight.w400,
                color: AppTheme.textSecondaryColor,
              ),
              filled: true,
              fillColor: AppTheme.surfaceColor,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 14,
                vertical: 14,
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(13),
                borderSide: BorderSide(
                  color: AppTheme.textSecondaryColor.withValues(alpha: 0.12),
                ),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(13),
                borderSide: BorderSide(
                  color: AppTheme.textSecondaryColor.withValues(alpha: 0.12),
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(13),
                borderSide: BorderSide(
                  color: AppTheme.primaryColor.withValues(alpha: 0.55),
                  width: 1.2,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPasswordHint() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(11),
      decoration: BoxDecoration(
        color: AppTheme.primaryBackgroundColor,
        borderRadius: BorderRadius.circular(11),
      ),
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.info_outline_rounded,
            size: 17,
            color: AppTheme.primaryColor,
          ),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              'รหัสผ่านควรมีความยาวอย่างน้อย 8 ตัวอักษร',
              style: TextStyle(
                fontFamily: 'Kanit',
                fontSize: 11,
                fontWeight: FontWeight.w400,
                height: 1.4,
                color: AppTheme.textSecondaryColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChangePasswordButton() {
  return SizedBox(
    width: double.infinity,
    height: 52,
    child: ElevatedButton(
      onPressed: _isLoading ? null : _changePassword,
      style: ElevatedButton.styleFrom(
        elevation: 4,
        shadowColor: Colors.black.withValues(alpha: 0.15),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      child: _isLoading
          ? const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            )
          : const Text(
              'เปลี่ยนรหัสผ่าน',
              style: TextStyle(
                fontFamily: 'Kanit',
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
    ),
  );
}
  Future<void> _changePassword() async {
    FocusScope.of(context).unfocus();

    if (_isLoading) {
      return;
    }

    final currentPassword = _currentPasswordController.text.trim();

    final newPassword = _newPasswordController.text.trim();

    final confirmPassword = _confirmPasswordController.text.trim();

    if (currentPassword.isEmpty ||
        newPassword.isEmpty ||
        confirmPassword.isEmpty) {
      await _showMessageDialog(
        title: 'กรุณากรอกข้อมูล',
        message: 'กรุณากรอกข้อมูลให้ครบทุกช่อง',
        icon: Icons.info_outline_rounded,
        iconColor: AppTheme.primaryColor,
        iconBackground: AppTheme.primaryBackgroundColor,
      );
      return;
    }

    if (newPassword.length < 8 || newPassword.length > 20) {
      await _showMessageDialog(
        title: 'รหัสผ่านไม่ถูกต้อง',
        message: 'รหัสผ่านใหม่ต้องมีความยาว 8–20 ตัวอักษร',
        icon: Icons.warning_amber_rounded,
        iconColor: const Color(0xFFE39A18),
        iconBackground: const Color(0xFFFFF3D9),
      );
      return;
    }

    if (!RegExp(r'[@$!%*?&]').hasMatch(newPassword)) {
      await _showMessageDialog(
        title: 'รหัสผ่านไม่ถูกต้อง',
        message: 'รหัสผ่านต้องมีอักขระพิเศษอย่างน้อย 1 ตัว',
        icon: Icons.warning_amber_rounded,
        iconColor: const Color(0xFFE39A18),
        iconBackground: const Color(0xFFFFF3D9),
      );
      return;
    }

    if (newPassword != confirmPassword) {
      await _showMessageDialog(
        title: 'รหัสผ่านไม่ตรงกัน',
        message: 'กรุณากรอกรหัสผ่านใหม่และยืนยันรหัสผ่านให้ตรงกัน',
        icon: Icons.warning_amber_rounded,
        iconColor: const Color(0xFFE39A18),
        iconBackground: const Color(0xFFFFF3D9),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      await _profileRepository.changePassword(
        currentPassword: currentPassword,
        newPassword: newPassword,
        confirmPassword: confirmPassword,
      );

      if (!mounted) {
        return;
      }

      await _showMessageDialog(
        title: 'เปลี่ยนรหัสผ่านสำเร็จ',
        message: 'รหัสผ่านของคุณถูกเปลี่ยนเรียบร้อยแล้ว',
        icon: Icons.check_rounded,
        iconColor: const Color(0xFF43A047),
        iconBackground: const Color(0xFFE8F5E9),
      );

      if (!mounted) {
        return;
      }

      Navigator.of(context).pop();
    } catch (error) {
      if (!mounted) {
        return;
      }

      await _showMessageDialog(
        title: 'เปลี่ยนรหัสผ่านไม่สำเร็จ',
        message: error.toString(),
        icon: Icons.error_outline_rounded,
        iconColor: AppTheme.errorColor,
        iconBackground: const Color(0xFFFFE8E6),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _showMessageDialog({
    required String title,
    required String message,
    required IconData icon,
    required Color iconColor,
    required Color iconBackground,
  }) async {
    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.symmetric(horizontal: 40),
          child: Container(
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
                  decoration: BoxDecoration(
                    color: iconBackground,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(icon, size: 30, color: iconColor),
                ),
                const SizedBox(height: 18),
                Text(
                  title,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 17,
                    fontWeight: FontWeight.w600,
                    height: 1.3,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  message,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 12,
                    fontWeight: FontWeight.w400,
                    height: 1.4,
                    color: AppTheme.textSecondaryColor,
                  ),
                ),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  height: 44,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                    },
                    style: ElevatedButton.styleFrom(
                      elevation: 0,
                      backgroundColor: AppTheme.primaryColor,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(24),
                      ),
                    ),
                    child: const Text(
                      'ตกลง',
                      style: TextStyle(
                        fontFamily: 'Kanit',
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
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
}
