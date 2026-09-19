import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import '../../../../core/network/api_client.dart';
import '../../data/models/profile_model.dart';
import '../../data/repositories/profile_repository.dart';
import '../../data/services/profile_api_service.dart';

class EditProfilePage extends StatefulWidget {
  const EditProfilePage({super.key});

  @override
  State<EditProfilePage> createState() => _EditProfilePageState();
}

class _EditProfilePageState extends State<EditProfilePage> {
  late final TextEditingController _firstNameController;
  late final TextEditingController _lastNameController;
  late final TextEditingController _phoneController;
  late final TextEditingController _emailController;

  late final ProfileRepository _profileRepository;

  ProfileModel? _profile;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();

    _firstNameController = TextEditingController();
    _lastNameController = TextEditingController();
    _phoneController = TextEditingController();
    _emailController = TextEditingController();

    final apiClient = ApiClient();

    final profileApiService = ProfileApiService(
      apiClient: apiClient,
    );

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

      _firstNameController.text = profile.firstName;
      _lastNameController.text = profile.lastName;
      _phoneController.text = profile.phoneNumber;
      _emailController.text = profile.email;

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

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
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
          icon: const Icon(
            Icons.arrow_back_ios_new_rounded,
            size: 19,
          ),
          color: AppTheme.textPrimaryColor,
        ),
        title: const Text(
          'แก้ไขข้อมูลส่วนตัว',
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1),
          child: Divider(
            height: 1,
            thickness: 1,
            color: Color(0xFFE8ECF2),
          ),
        ),
      ),
      body: SafeArea(
        child: _buildBody(context),
      ),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
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
            ],
          ),
        ),
      );
    }

    return SingleChildScrollView(
      keyboardDismissBehavior:
          ScrollViewKeyboardDismissBehavior.onDrag,
      padding: const EdgeInsets.fromLTRB(
        20,
        22,
        20,
        40,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'แก้ไขข้อมูลส่วนตัวของคุณให้เป็นปัจจุบัน',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 13,
              fontWeight: FontWeight.w400,
              color: AppTheme.textSecondaryColor,
            ),
          ),
          const SizedBox(height: 22),

          _buildSectionTitle('ข้อมูลส่วนตัว'),
          const SizedBox(height: 10),
          _buildPersonalInformationCard(),

          const SizedBox(height: 20),

          _buildSectionTitle('ข้อมูลติดต่อ'),
          const SizedBox(height: 10),
          _buildContactInformationCard(),

          const SizedBox(height: 28),

          _buildSaveButton(),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontFamily: 'Kanit',
        fontSize: 15,
        fontWeight: FontWeight.w600,
        color: AppTheme.textPrimaryColor,
      ),
    );
  }

  Widget _buildPersonalInformationCard() {
    return _buildCard(
      child: Column(
        children: [
          _buildTextField(
            controller: _firstNameController,
            label: 'ชื่อ',
            hintText: 'กรอกชื่อ',
            icon: Icons.person_outline_rounded,
          ),
          const SizedBox(height: 16),
          _buildTextField(
            controller: _lastNameController,
            label: 'นามสกุล',
            hintText: 'กรอกนามสกุล',
            icon: Icons.person_outline_rounded,
          ),
        ],
      ),
    );
  }

  Widget _buildContactInformationCard() {
    return _buildCard(
      child: Column(
        children: [
          _buildTextField(
            controller: _phoneController,
            label: 'เบอร์โทรศัพท์',
            hintText: '08X-XXX-XXXX',
            icon: Icons.phone_outlined,
            keyboardType: TextInputType.phone,
          ),
          const SizedBox(height: 16),
          _buildTextField(
            controller: _emailController,
            label: 'อีเมล',
            hintText: 'example@email.com',
            icon: Icons.email_outlined,
            keyboardType: TextInputType.emailAddress,
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hintText,
    required IconData icon,
    TextInputType? keyboardType,
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
            keyboardType: keyboardType,
            style: const TextStyle(
              fontFamily: 'Kanit',
              fontSize: 13,
              fontWeight: FontWeight.w400,
              color: AppTheme.textPrimaryColor,
            ),
            decoration: InputDecoration(
              prefixIcon: Icon(
                icon,
                size: 19,
                color: AppTheme.textSecondaryColor,
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
                  color: AppTheme.textSecondaryColor.withValues(
                    alpha: 0.12,
                  ),
                ),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(13),
                borderSide: BorderSide(
                  color: AppTheme.textSecondaryColor.withValues(
                    alpha: 0.12,
                  ),
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(13),
                borderSide: BorderSide(
                  color: AppTheme.primaryColor.withValues(
                    alpha: 0.55,
                  ),
                  width: 1.2,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCard({
    required Widget child,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(17),
        border: Border.all(
          color: AppTheme.textSecondaryColor.withValues(
            alpha: 0.08,
          ),
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

  Widget _buildSaveButton() {
  return SizedBox(
    width: double.infinity,
    height: 52,
    child: ElevatedButton(
      onPressed: _saveProfile,
      style: ElevatedButton.styleFrom(
        elevation: 4,
        shadowColor: Colors.black.withValues(alpha: 0.15),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      child: const Text(
        'บันทึกการเปลี่ยนแปลง',
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

  Future<void> _saveProfile() async {
  FocusScope.of(context).unfocus();

  final firstName = _firstNameController.text.trim();
  final lastName = _lastNameController.text.trim();
  final phoneNumber = _phoneController.text.trim();
  final email = _emailController.text.trim();

  if (firstName.isEmpty ||
      lastName.isEmpty ||
      phoneNumber.isEmpty ||
      email.isEmpty) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          'กรุณากรอกข้อมูลให้ครบถ้วน',
          style: TextStyle(
            fontFamily: 'Kanit',
          ),
        ),
      ),
    );
    return;
  }

  try {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final updatedProfile = await _profileRepository.updateProfile(
      firstName: firstName,
      lastName: lastName,
      phoneNumber: phoneNumber,
      email: email,
    );

    if (!mounted) {
      return;
    }

    setState(() {
      _profile = updatedProfile;
      _isLoading = false;
    });

    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.symmetric(
            horizontal: 40,
          ),
          child: Container(
            padding: const EdgeInsets.fromLTRB(
              20,
              22,
              20,
              18,
            ),
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
                    color: Color(0xFFE8F5E9),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.check_rounded,
                    size: 30,
                    color: Color(0xFF43A047),
                  ),
                ),
                const SizedBox(height: 18),
                const Text(
                  'บันทึกข้อมูลสำเร็จ',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 17,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'ข้อมูลส่วนตัวของคุณถูกบันทึกเรียบร้อยแล้ว',
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

    if (!mounted) {
      return;
    }

    Navigator.of(context).pop(updatedProfile);
  } catch (error) {
    if (!mounted) {
      return;
    }

    setState(() {
      _isLoading = false;
      _errorMessage = error.toString();
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'ไม่สามารถบันทึกข้อมูลได้\n$error',
          style: const TextStyle(
            fontFamily: 'Kanit',
          ),
        ),
      ),
    );
  }
}
}