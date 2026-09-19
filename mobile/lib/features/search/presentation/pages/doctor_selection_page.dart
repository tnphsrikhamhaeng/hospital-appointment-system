import 'dart:developer' as developer;
import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import 'doctor_profile_page.dart';
import '../../data/models/doctor_model.dart';
import '../../data/repositories/doctor_repository.dart';
import '../../data/services/doctor_api_service.dart';
import '../../../../core/network/api_client.dart';

class DoctorSelectionPage extends StatefulWidget {
  final String departmentId;
  final String departmentName;
  final String? departmentImageUrl;
  final String? departmentDescription;

  const DoctorSelectionPage({
    super.key,
    required this.departmentId,
    required this.departmentName,
    this.departmentImageUrl,
    this.departmentDescription,
  });

  @override
  State<DoctorSelectionPage> createState() => _DoctorSelectionPageState();
}

class _NoStretchScrollBehavior extends ScrollBehavior {
  const _NoStretchScrollBehavior();

  @override
  ScrollPhysics getScrollPhysics(BuildContext context) {
    return const ClampingScrollPhysics();
  }
}

class _DoctorSelectionPageState extends State<DoctorSelectionPage> {
  final DoctorRepository _doctorRepository = DoctorRepository(
    doctorApiService: DoctorApiService(apiClient: ApiClient()),
  );

  List<DoctorModel> _doctors = [];

  bool _isLoading = true;
  String? _errorMessage;

  IconData _getDepartmentIcon() {
    switch (widget.departmentName) {
      case 'ศูนย์สมองและระบบประสาท':
        return Icons.psychology_rounded;
      case 'คลินิกอายุรกรรม':
        return Icons.medical_services_rounded;
      case 'ศูนย์หัวใจ':
        return Icons.favorite_rounded;
      case 'ศูนย์ทางเดินอาหาร':
        return Icons.restaurant_rounded;
      default:
        return Icons.medical_services_rounded;
    }
  }

  Color _getDepartmentIconColor() {
    switch (widget.departmentName) {
      case 'ศูนย์สมองและระบบประสาท':
        return AppTheme.primaryColor;
      case 'คลินิกอายุรกรรม':
        return AppTheme.successColor;
      case 'ศูนย์หัวใจ':
        return AppTheme.errorColor;
      case 'ศูนย์ทางเดินอาหาร':
        return AppTheme.warningColor;
      default:
        return AppTheme.primaryColor;
    }
  }

  @override
  void initState() {
    super.initState();

    _loadDoctors();
  }

  Future<void> _loadDoctors() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final doctors = await _doctorRepository.getDoctorsByDepartment(
        departmentId: widget.departmentId,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _doctors = doctors
            .where((doctor) => doctor.status == DoctorStatus.active)
            .toList();

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

  String? _resolveDepartmentImageUrl() {
    return _resolveImageUrl(widget.departmentImageUrl);
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
          'แผนกการรักษา',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        centerTitle: true,
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1),
          child: Divider(height: 1, thickness: 1, color: Color(0xFFE8ECF2)),
        ),
      ),
      body: SafeArea(child: _buildContent(context)),
    );
  }

  Widget _buildContent(BuildContext context) {
    final theme = Theme.of(context);

    return ScrollConfiguration(
      behavior: const _NoStretchScrollBehavior(),
      child: CustomScrollView(
        slivers: [
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _buildDepartmentHeader(context),
                const SizedBox(height: 28),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Expanded(
                      child: Text(
                        'รายชื่อแพทย์',
                        textAlign: TextAlign.left,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontSize: 19,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.textPrimaryColor,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                if (_isLoading)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 40),
                      child: CircularProgressIndicator(),
                    ),
                  )
                else if (_errorMessage != null)
                  _buildErrorState(context)
                else if (_doctors.isEmpty)
                  _buildEmptyState(context)
                else
                  ..._doctors.map(
                    (doctor) => _buildDoctorCard(context, doctor: doctor),
                  ),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDepartmentHeader(BuildContext context) {
    final theme = Theme.of(context);
    final imageUrl = _resolveDepartmentImageUrl();

    developer.log(
      'Department image URL from API: ${widget.departmentImageUrl}',
      name: 'DoctorSelectionPage',
    );

    developer.log(
      'Department image URL resolved: $imageUrl',
      name: 'DoctorSelectionPage',
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.departmentName,
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      color: AppTheme.textPrimaryColor,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    widget.departmentDescription ?? '',
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.bodySmall?.copyWith(
                      fontSize: 13,
                      height: 1.45,
                      color: AppTheme.textSecondaryColor,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 14),
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: _getDepartmentIconColor().withValues(alpha: 0.12),
                shape: BoxShape.circle,
              ),
              child: Icon(
                _getDepartmentIcon(),
                color: _getDepartmentIconColor(),
                size: 24,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            const Icon(
              Icons.medical_services_outlined,
              size: 17,
              color: AppTheme.primaryColor,
            ),
            const SizedBox(width: 5),
            Text(
              'แพทย์ ${_doctors.length} ท่าน',
              style: theme.textTheme.bodySmall?.copyWith(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: AppTheme.textSecondaryColor,
              ),
            ),
            const SizedBox(width: 14),
            const Icon(
              Icons.calendar_today_outlined,
              size: 16,
              color: AppTheme.primaryColor,
            ),
            const SizedBox(width: 5),
            Text(
              'คิวว่างวันนี้',
              style: theme.textTheme.bodySmall?.copyWith(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: AppTheme.textSecondaryColor,
              ),
            ),
          ],
        ),
        const SizedBox(height: 18),
        ClipRRect(
          borderRadius: BorderRadius.circular(14),
          child: SizedBox(
            width: double.infinity,
            height: 170,
            child: imageUrl != null
                ? Image.network(
                    imageUrl,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return const Center(
                        child: Icon(
                          Icons.image_outlined,
                          size: 40,
                          color: AppTheme.textMutedColor,
                        ),
                      );
                    },
                  )
                : const Center(
                    child: Icon(
                      Icons.image_outlined,
                      size: 40,
                      color: AppTheme.textMutedColor,
                    ),
                  ),
          ),
        ),
      ],
    );
  }

  Widget _buildDoctorCard(
    BuildContext context, {
    required DoctorModel doctor,
  }) {
    final theme = Theme.of(context);
    final imageUrl = _resolveImageUrl(doctor.profileImageUrl);

    developer.log(
      'Doctor ${doctor.id} image URL from API: ${doctor.profileImageUrl}',
      name: 'DoctorSelectionPage',
    );

    developer.log(
      'Doctor ${doctor.id} image URL resolved: $imageUrl',
      name: 'DoctorSelectionPage',
    );

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE8ECF2), width: 1),
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(14),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: () {
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => DoctorProfilePage(doctor: doctor),
              ),
            );
          },
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
            child: Row(
              children: [
                _buildDoctorAvatar(imageUrl),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${doctor.preface == DoctorPreface.mrDoctor ? 'นายแพทย์' : 'แพทย์หญิง'} ${doctor.firstName} ${doctor.lastName}',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.textPrimaryColor,
                        ),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        doctor.specializations.isNotEmpty
                            ? doctor.specializations.first.name
                            : 'แพทย์ผู้เชี่ยวชาญ',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontSize: 12,
                          color: AppTheme.textSecondaryColor,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          _buildDoctorTag(context, label: 'เฉพาะทาง'),
                          const SizedBox(width: 5),
                          _buildDoctorTag(context, label: 'ให้บริการ'),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  width: 36,
                  height: 36,
                  decoration: const BoxDecoration(
                    color: Color(0xFFF1F2F5),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.chevron_right_rounded,
                    size: 21,
                    color: AppTheme.textMutedColor,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDoctorAvatar(String? imageUrl) {
    return Container(
      width: 54,
      height: 54,
      decoration: const BoxDecoration(
        color: AppTheme.primaryBackgroundColor,
        shape: BoxShape.circle,
      ),
      clipBehavior: Clip.antiAlias,
      child: imageUrl != null
          ? Image.network(
              imageUrl,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return const Icon(
                  Icons.person_rounded,
                  color: AppTheme.primaryColor,
                  size: 28,
                );
              },
            )
          : const Icon(
              Icons.person_rounded,
              color: AppTheme.primaryColor,
              size: 28,
            ),
    );
  }

  Widget _buildDoctorTag(BuildContext context, {required String label}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        color: AppTheme.primaryBackgroundColor,
        borderRadius: BorderRadius.circular(9),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
          fontSize: 10,
          fontWeight: FontWeight.w500,
          color: AppTheme.primaryColor,
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE8ECF2)),
      ),
      child: Column(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: const BoxDecoration(
              color: AppTheme.primaryBackgroundColor,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.person_off_rounded,
              color: AppTheme.primaryColor,
              size: 24,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'ไม่พบแพทย์ที่เกี่ยวข้อง',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'ลองเลือกแผนกอื่น',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodySmall?.copyWith(
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 28),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE8ECF2)),
      ),
      child: Column(
        children: [
          const Icon(
            Icons.cloud_off_rounded,
            color: AppTheme.textMutedColor,
            size: 32,
          ),
          const SizedBox(height: 12),
          Text(
            _errorMessage ?? 'ไม่สามารถโหลดข้อมูลได้',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          const SizedBox(height: 12),
          OutlinedButton(onPressed: _loadDoctors, child: const Text('ลองใหม่')),
        ],
      ),
    );
  }
}