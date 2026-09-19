import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../data/models/doctor_model.dart';
import '../../data/repositories/doctor_repository.dart';
import '../../data/services/doctor_api_service.dart';
import 'doctor_schedule_page.dart';

class DoctorProfilePage extends StatefulWidget {
  final DoctorModel doctor;

  const DoctorProfilePage({
    super.key,
    required this.doctor,
  });

  @override
  State<DoctorProfilePage> createState() => _DoctorProfilePageState();
}

class _DoctorProfilePageState extends State<DoctorProfilePage> {
  late final DoctorRepository _doctorRepository;

  DoctorModel? _doctor;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();

    _doctorRepository = DoctorRepository(
      doctorApiService: DoctorApiService(
        apiClient: ApiClient(),
      ),
    );

    _loadDoctor();
  }

  Future<void> _loadDoctor() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final doctor = await _doctorRepository.getDoctorById(
        doctorId: widget.doctor.id,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _doctor = doctor;
        _isLoading = false;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
        _errorMessage = 'ไม่สามารถโหลดข้อมูลแพทย์ได้';
      });
    }
  }

  String _getDoctorName(DoctorModel doctor) {
    final preface = doctor.preface == DoctorPreface.mrDoctor
        ? 'นายแพทย์'
        : 'แพทย์หญิง';

    return '$preface ${doctor.firstName} ${doctor.lastName}';
  }

  String _getPrimarySpecialization(DoctorModel doctor) {
    if (doctor.specializations.isEmpty) {
      return 'แพทย์ผู้เชี่ยวชาญ';
    }

    return doctor.specializations.first.name;
  }

  List<String> _getExpertise(DoctorModel doctor) {
    if (doctor.specializations.isEmpty) {
      return ['แพทย์ผู้เชี่ยวชาญ'];
    }

    return doctor.specializations
        .map((specialization) => specialization.name)
        .where((name) => name.trim().isNotEmpty)
        .toList();
  }

  IconData _getExpertiseIcon(String expertise) {
    final value = expertise.toLowerCase();

    if (value.contains('หัวใจ') || value.contains('cardio')) {
      return Icons.favorite_rounded;
    }

    if (value.contains('ประสาท') ||
        value.contains('สมอง') ||
        value.contains('neuro')) {
      return Icons.psychology_rounded;
    }

    if (value.contains('ทางเดินอาหาร') ||
        value.contains('gastro')) {
      return Icons.restaurant_rounded;
    }

    if (value.contains('อายุร') ||
        value.contains('internal')) {
      return Icons.medical_services_rounded;
    }

    return Icons.medical_services_rounded;
  }

  Color _getExpertiseColor(String expertise) {
    final value = expertise.toLowerCase();

    if (value.contains('หัวใจ') || value.contains('cardio')) {
      return AppTheme.errorColor;
    }

    if (value.contains('ทางเดินอาหาร') ||
        value.contains('gastro')) {
      return AppTheme.warningColor;
    }

    return AppTheme.primaryColor;
  }

  String? _resolveImageUrl(String? imageUrl) {
    final trimmedUrl = imageUrl?.trim();

    if (trimmedUrl == null || trimmedUrl.isEmpty) {
      return null;
    }

    final uri = Uri.tryParse(trimmedUrl);

    if (uri == null) {
      return trimmedUrl;
    }

    if (uri.host == 'localhost' || uri.host == '127.0.0.1') {
      return uri.replace(host: '10.0.2.2').toString();
    }

    return trimmedUrl;
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
        leading: IconButton(
          onPressed: () => Navigator.of(context).pop(),
          icon: const Icon(
            Icons.arrow_back_rounded,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        title: Text(
          'โปรไฟล์แพทย์',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimaryColor,
              ),
        ),
        centerTitle: true,
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

    if (_errorMessage != null) {
      return _buildErrorState(context);
    }

    final doctor = _doctor;

    if (doctor == null) {
      return _buildErrorState(context);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(
        20,
        20,
        20,
        32,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildDoctorIdentity(
            context,
            doctor,
          ),
          const SizedBox(height: 24),
          _buildAboutSection(
            context,
            doctor,
          ),
          const SizedBox(height: 24),
          _buildExpertiseSection(
            context,
            doctor,
          ),
          const SizedBox(height: 24),
          _buildDepartmentSection(
            context,
            doctor,
          ),
          const SizedBox(height: 24),
          _buildScheduleButton(
            context,
            doctor,
          ),
        ],
      ),
    );
  }

  Widget _buildDoctorIdentity(
    BuildContext context,
    DoctorModel doctor,
  ) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(
        20,
        26,
        20,
        28,
      ),
      decoration: BoxDecoration(
        color: AppTheme.primaryBackgroundColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppTheme.primaryColor.withValues(
            alpha: 0.08,
          ),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withValues(
              alpha: 0.06,
            ),
            blurRadius: 18,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildDoctorAvatar(doctor),
          const SizedBox(height: 18),
          Text(
            _getDoctorName(doctor),
            textAlign: TextAlign.center,
            style: theme.textTheme.headlineSmall?.copyWith(
              fontSize: 22,
              fontWeight: FontWeight.w700,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            _getPrimarySpecialization(doctor),
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppTheme.primaryColor,
            ),
          ),
          const SizedBox(height: 5),
          Text(
            doctor.department.name,
            textAlign: TextAlign.center,
            style: theme.textTheme.bodySmall?.copyWith(
              fontSize: 12,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDoctorAvatar(DoctorModel doctor) {
    final imageUrl = _resolveImageUrl(doctor.profileImageUrl);

    return Container(
      width: 104,
      height: 104,
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        shape: BoxShape.circle,
        border: Border.all(
          color: AppTheme.primaryColor.withValues(
            alpha: 0.10,
          ),
          width: 1,
        ),
      ),
      clipBehavior: Clip.antiAlias,
      child: imageUrl == null
          ? const Icon(
              Icons.person_rounded,
              color: AppTheme.primaryColor,
              size: 52,
            )
          : Image.network(
              imageUrl,
              fit: BoxFit.cover,
              errorBuilder: (
                context,
                error,
                stackTrace,
              ) {
                return const Icon(
                  Icons.person_rounded,
                  color: AppTheme.primaryColor,
                  size: 52,
                );
              },
            ),
    );
  }

  Widget _buildAboutSection(
    BuildContext context,
    DoctorModel doctor,
  ) {
    final theme = Theme.of(context);

    final departmentDescription =
        doctor.department.description?.trim() ?? '';

    final description = departmentDescription.isEmpty
        ? 'ให้บริการตรวจและดูแลรักษาผู้ป่วยตามความเชี่ยวชาญของแพทย์'
        : departmentDescription;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'เกี่ยวกับแพทย์',
          style: theme.textTheme.titleMedium?.copyWith(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          description,
          style: theme.textTheme.bodySmall?.copyWith(
            fontSize: 14,
            height: 1.6,
            color: AppTheme.textSecondaryColor,
          ),
        ),
      ],
    );
  }

  Widget _buildExpertiseSection(
    BuildContext context,
    DoctorModel doctor,
  ) {
    final theme = Theme.of(context);
    final expertise = _getExpertise(doctor);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'ความเชี่ยวชาญ',
          style: theme.textTheme.titleMedium?.copyWith(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: expertise.map((item) {
            final color = _getExpertiseColor(item);

            return Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 10,
                vertical: 7,
              ),
              decoration: BoxDecoration(
                color: color.withValues(
                  alpha: 0.10,
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    _getExpertiseIcon(item),
                    size: 14,
                    color: color,
                  ),
                  const SizedBox(width: 5),
                  Text(
                    item,
                    style: theme.textTheme.bodySmall?.copyWith(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: color,
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildDepartmentSection(
    BuildContext context,
    DoctorModel doctor,
  ) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFFE8ECF2),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: AppTheme.primaryBackgroundColor,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.local_hospital_rounded,
              color: AppTheme.primaryColor,
              size: 21,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'แผนก',
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontSize: 12,
                    color: AppTheme.textMutedColor,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  doctor.department.name,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScheduleButton(
    BuildContext context,
    DoctorModel doctor,
  ) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => DoctorSchedulePage(
                doctor: doctor,
              ),
            ),
          );
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: AppTheme.primaryColor,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(
            vertical: 14,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'ดูตารางนัดหมาย',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
            ),
            const SizedBox(width: 6),
            const Icon(
              Icons.arrow_forward_rounded,
              size: 18,
              color: Colors.white,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(BuildContext context) {
    final theme = Theme.of(context);

    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: 24,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.cloud_off_rounded,
              color: AppTheme.textMutedColor,
              size: 42,
            ),
            const SizedBox(height: 14),
            Text(
              _errorMessage ?? 'ไม่สามารถโหลดข้อมูลแพทย์ได้',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimaryColor,
              ),
            ),
            const SizedBox(height: 14),
            OutlinedButton(
              onPressed: _loadDoctor,
              child: const Text('ลองใหม่'),
            ),
          ],
        ),
      ),
    );
  }
}