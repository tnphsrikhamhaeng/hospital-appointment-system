import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../data/models/medical_record_model.dart';
import '../../../search/data/models/doctor_model.dart';
import '../../../search/data/repositories/doctor_repository.dart';
import '../../../search/data/services/doctor_api_service.dart';

class _NoStretchScrollBehavior extends ScrollBehavior {
  const _NoStretchScrollBehavior();

  @override
  ScrollPhysics getScrollPhysics(BuildContext context) {
    return const ClampingScrollPhysics();
  }
}

class MedicalRecordDetailsPage extends StatefulWidget {
  final MedicalRecordModel record;

  const MedicalRecordDetailsPage({super.key, required this.record});

  @override
  State<MedicalRecordDetailsPage> createState() =>
      _MedicalRecordDetailsPageState();
}

class _MedicalRecordDetailsPageState extends State<MedicalRecordDetailsPage> {
  late final DoctorRepository _doctorRepository;

  DoctorModel? _doctor;
  String? _doctorErrorMessage;

  MedicalRecordModel get record => widget.record;

  @override
  void initState() {
    super.initState();

    final apiClient = ApiClient();

    _doctorRepository = DoctorRepository(
      doctorApiService: DoctorApiService(apiClient: apiClient),
    );

    _loadDoctor();
  }

  Future<void> _loadDoctor() async {
    try {
      final doctor = await _doctorRepository.getDoctorById(
        doctorId: record.doctorId,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _doctor = doctor;
      });
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _doctorErrorMessage = _getDioErrorMessage(error);
      });
    } catch (_) {
      if (!mounted) {
        return;
      }

      setState(() {
        _doctorErrorMessage = 'ไม่สามารถโหลดข้อมูลแพทย์ได้';
      });
    }
  }

  String _getDioErrorMessage(DioException error) {
    final data = error.response?.data;

    if (data is Map) {
      final detail = data['detail'];

      if (detail is String && detail.isNotEmpty) {
        return detail;
      }

      if (detail is Map) {
        final message = detail['message'];

        if (message is String && message.isNotEmpty) {
          return message;
        }
      }
    }

    return 'ไม่สามารถโหลดข้อมูลแพทย์ได้';
  }

  String _doctorDisplayName() {
    if (_doctor == null) {
      return _doctorErrorMessage ?? 'กำลังโหลดข้อมูลแพทย์...';
    }

    final preface = _doctor!.preface == DoctorPreface.mrDoctor ? 'นพ.' : 'พญ.';

    return '$preface ${_doctor!.firstName} ${_doctor!.lastName}';
  }

  String? _resolveDoctorImageUrl(String? imageUrl) {
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
        centerTitle: true,
        title: const Text(
          'รายละเอียดประวัติการรักษา',
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        leading: IconButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 19),
          color: AppTheme.textPrimaryColor,
        ),
      ),
      body: SafeArea(
        child: ScrollConfiguration(
          behavior: const _NoStretchScrollBehavior(),
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(20, 18, 20, 40),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeaderCard(),
                const SizedBox(height: 16),
                _buildMedicalInformationCard(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeaderCard() {
    final imageUrl = _resolveDoctorImageUrl(
      _doctor?.profileImageUrl,
    );

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF1976D2), Color(0xFF0D5AC7)],
        ),
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withValues(alpha: 0.16),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'วันที่บันทึกประวัติการรักษา',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 12,
              fontWeight: FontWeight.w400,
              color: Colors.white70,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            _formatDate(record.createdAt),
            style: const TextStyle(
              fontFamily: 'Kanit',
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 10),

          // Doctor information
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 10,
            ),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: Colors.white.withValues(alpha: 0.8),
                      width: 1.5,
                    ),
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: imageUrl == null
                      ? const Icon(
                          Icons.person_rounded,
                          size: 22,
                          color: AppTheme.primaryColor,
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
                              size: 22,
                              color: AppTheme.primaryColor,
                            );
                          },
                        ),
                ),
                const SizedBox(width: 11),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'แพทย์ผู้รักษา',
                        style: TextStyle(
                          fontFamily: 'Kanit',
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                          color: Colors.white70,
                        ),
                      ),
                      const SizedBox(height: 1),
                      Text(
                        _doctorDisplayName(),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontFamily: 'Kanit',
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMedicalInformationCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(16, 17, 16, 18),
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
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionHeader(
            icon: Icons.medical_information_outlined,
            title: 'ข้อมูลการรักษา',
            color: AppTheme.primaryColor,
            backgroundColor: AppTheme.primaryBackgroundColor,
          ),
          const SizedBox(height: 16),

          _buildSubTitle('อาการหลัก (CHIEF COMPLAINT)'),
          const SizedBox(height: 5),
          _buildBodyText(record.chiefComplaint),

          if (_hasText(record.presentIllness)) ...[
            const SizedBox(height: 14),
            _buildSubTitle('ประวัติปัจจุบัน (PRESENT ILLNESS)'),
            const SizedBox(height: 5),
            _buildBodyText(record.presentIllness!),
          ],

          if (_hasText(record.physicalExamination)) ...[
            const SizedBox(height: 14),
            _buildExaminationCard(),
          ],

          const SizedBox(height: 14),

          _buildDiagnosisCard(),

          if (_hasText(record.treatment)) ...[
            const SizedBox(height: 14),
            _buildTreatmentSection(),
          ],

          if (_hasText(record.recommendation)) ...[
            const SizedBox(height: 14),
            _buildRecommendationCard(),
          ],

          if (_hasText(record.note)) ...[
            const SizedBox(height: 16),
            const Divider(height: 1, color: Color(0xFFE9EDF2)),
            const SizedBox(height: 12),
            _buildSubTitle('หมายเหตุ (NOTE)'),
            const SizedBox(height: 5),
            _buildBodyText(record.note!),
          ],
        ],
      ),
    );
  }

  Widget _buildExaminationCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(12, 11, 12, 11),
      decoration: BoxDecoration(
        color: const Color(0xFFF5F3F3),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSubTitle('ผลการตรวจร่างกาย (PHYSICAL EXAMINATION)'),
          const SizedBox(height: 8),
          _buildVitalItem(
            label: 'ผลตรวจ',
            value: record.physicalExamination!,
          ),
        ],
      ),
    );
  }

  Widget _buildVitalItem({
    required String label,
    required String value,
  }) {
    return Column(
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
          style: const TextStyle(
            fontFamily: 'Kanit',
            fontSize: 14,
            fontWeight: FontWeight.w500,
            color: AppTheme.textPrimaryColor,
          ),
        ),
      ],
    );
  }

  Widget _buildDiagnosisCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(12, 11, 12, 11),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF5F5),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSubTitle(
            'การวินิจฉัย (DIAGNOSIS)',
            color: const Color(0xFFD84B4B),
          ),
          const SizedBox(height: 6),
          Text(
            record.diagnosis,
            style: const TextStyle(
              fontFamily: 'Kanit',
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: Color(0xFFC63C3C),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTreatmentSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSubTitle(
          'การรักษา (TREATMENT)',
          color: const Color(0xFF00897B),
        ),
        const SizedBox(height: 6),
        _buildBodyText(record.treatment!),
      ],
    );
  }

  Widget _buildRecommendationCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(12, 11, 12, 11),
      decoration: BoxDecoration(
        color: const Color(0xFFE8FBEA),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSubTitle(
            'คำแนะนำ (RECOMMENDATION)',
            color: const Color(0xFF2E9B49),
          ),
          const SizedBox(height: 7),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Padding(
                padding: EdgeInsets.only(top: 4),
                child: Icon(
                  Icons.check_circle_outline_rounded,
                  size: 13,
                  color: Color(0xFF2E9B49),
                ),
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  record.recommendation!,
                  style: const TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 13,
                    fontWeight: FontWeight.w400,
                    height: 1.4,
                    color: AppTheme.textSecondaryColor,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader({
    required IconData icon,
    required String title,
    required Color color,
    required Color backgroundColor,
  }) {
    return Row(
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: backgroundColor,
            borderRadius: BorderRadius.circular(9),
          ),
          child: Icon(icon, size: 20, color: color),
        ),
        const SizedBox(width: 12),
        Text(
          title,
          style: const TextStyle(
            fontFamily: 'Kanit',
            fontSize: 15,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
      ],
    );
  }

  Widget _buildSubTitle(
    String text, {
    Color color = AppTheme.textPrimaryColor,
  }) {
    return Text(
      text,
      style: TextStyle(
        fontFamily: 'Kanit',
        fontSize: 12,
        fontWeight: FontWeight.w600,
        color: color,
      ),
    );
  }

  Widget _buildBodyText(String text) {
    return Text(
      text,
      style: const TextStyle(
        fontFamily: 'Kanit',
        fontSize: 13,
        fontWeight: FontWeight.w400,
        height: 1.55,
        color: AppTheme.textSecondaryColor,
      ),
    );
  }

  bool _hasText(String? value) {
    return value != null && value.trim().isNotEmpty;
  }

  String _formatDate(DateTime date) {
    final localDate = date.toLocal();

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

    return '${localDate.day} ${thaiMonths[localDate.month - 1]} '
        '${localDate.year + 543}';
  }
}