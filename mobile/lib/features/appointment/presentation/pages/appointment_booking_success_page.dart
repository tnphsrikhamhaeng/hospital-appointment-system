import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import '../../../search/data/models/doctor_model.dart';
import '../../data/models/appointment_model.dart';
import 'appointment_details_page.dart';
import '../../../../core/widgets/app_shell.dart';

class AppointmentBookingSuccessPage extends StatefulWidget {
  final DoctorModel doctor;
  final AppointmentModel appointment;

  const AppointmentBookingSuccessPage({
    super.key,
    required this.doctor,
    required this.appointment,
  });

  @override
  State<AppointmentBookingSuccessPage> createState() =>
      _AppointmentBookingSuccessPageState();
}

class _AppointmentBookingSuccessPageState
    extends State<AppointmentBookingSuccessPage>
    with SingleTickerProviderStateMixin {
  late final AnimationController _successAnimationController;
  late final Animation<double> _successScaleAnimation;
  late final Animation<double> _successMoveAnimation;

  @override
  void initState() {
    super.initState();

    _successAnimationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);

    _successScaleAnimation =
        Tween<double>(begin: 0.92, end: 1.08).animate(
      CurvedAnimation(
        parent: _successAnimationController,
        curve: Curves.easeInOut,
      ),
    );

    _successMoveAnimation =
        Tween<double>(begin: 2.0, end: -2.0).animate(
      CurvedAnimation(
        parent: _successAnimationController,
        curve: Curves.easeInOut,
      ),
    );
  }

  @override
  void dispose() {
    _successAnimationController.dispose();
    super.dispose();
  }

  String _doctorName() {
    final title =
        widget.doctor.preface == DoctorPreface.mrDoctor
            ? 'นายแพทย์'
            : 'แพทย์หญิง';

    return '$title '
        '${widget.doctor.firstName} '
        '${widget.doctor.lastName}';
  }

  String _doctorSpecialization() {
    if (widget.doctor.specializations.isEmpty) {
      return 'แพทย์ผู้เชี่ยวชาญ';
    }

    return widget.doctor.specializations.first.name;
  }

  String? _resolveDoctorImageUrl(
    String? imageUrl,
  ) {
    final trimmedUrl = imageUrl?.trim();

    if (trimmedUrl == null || trimmedUrl.isEmpty) {
      return null;
    }

    final uri = Uri.tryParse(trimmedUrl);

    if (uri == null) {
      return trimmedUrl;
    }

    if (uri.host == 'localhost' ||
        uri.host == '127.0.0.1') {
      return uri.replace(
        host: '10.0.2.2',
      ).toString();
    }

    return trimmedUrl;
  }

  Widget _buildDoctorPlaceholder() {
    return Container(
      width: 48,
      height: 48,
      decoration: const BoxDecoration(
        color: AppTheme.primaryBackgroundColor,
        shape: BoxShape.circle,
      ),
      child: const Icon(
        Icons.person_rounded,
        color: AppTheme.primaryColor,
        size: 25,
      ),
    );
  }

  Widget _buildDoctorAvatar() {
    final imageUrl = _resolveDoctorImageUrl(
      widget.doctor.profileImageUrl,
    );

    if (imageUrl == null) {
      return _buildDoctorPlaceholder();
    }

    return ClipOval(
      child: Image.network(
        imageUrl,
        width: 48,
        height: 48,
        fit: BoxFit.cover,
        errorBuilder: (
          context,
          error,
          stackTrace,
        ) {
          return _buildDoctorPlaceholder();
        },
      ),
    );
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
        title: const Text(
          'การนัดหมาย',
          style: TextStyle(
            fontFamily: 'Kanit',
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
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(
                20,
                12,
                20,
                24,
              ),
              child: ConstrainedBox(
                constraints: BoxConstraints(
                  minHeight: constraints.maxHeight - 36,
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSuccessHeader(context),
                    const SizedBox(height: 22),
                    _buildAppointmentCard(context),
                    const SizedBox(height: 20),
                    _buildDetailButton(context),
                    const SizedBox(height: 8),
                    _buildHomeButton(context),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildSuccessHeader(BuildContext context) {
    return Column(
      children: [
        Center(
          child: AnimatedBuilder(
            animation: _successAnimationController,
            builder: (context, child) {
              final animationValue =
                  _successAnimationController.value;

              return SizedBox(
                width: 96,
                height: 96,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    Positioned(
                      top: 8 + (animationValue * 3),
                      left: 12,
                      child: _buildSuccessDot(
                        size: 5,
                        color: const Color(0xFF43D66B),
                      ),
                    ),
                    Positioned(
                      top: 13 - (animationValue * 3),
                      right: 12,
                      child: _buildSuccessDot(
                        size: 4,
                        color: const Color(0xFFFFB45C),
                      ),
                    ),
                    Positioned(
                      bottom: 10 + (animationValue * 4),
                      left: 18,
                      child: _buildSuccessDot(
                        size: 5,
                        color: const Color(0xFF68E88A),
                      ),
                    ),
                    Positioned(
                      bottom: 12 - (animationValue * 3),
                      right: 13,
                      child: _buildSuccessDot(
                        size: 5,
                        color: const Color(0xFF43D66B),
                      ),
                    ),
                    Transform.translate(
                      offset: Offset(
                        0,
                        _successMoveAnimation.value,
                      ),
                      child: Transform.scale(
                        scale: _successScaleAnimation.value,
                        child: Container(
                          width: 64,
                          height: 64,
                          decoration: BoxDecoration(
                            color: const Color(0xFFE7F8EC),
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: const Color(0xFF16A34A)
                                    .withValues(
                                  alpha:
                                      0.10 +
                                      (animationValue * 0.10),
                                ),
                                blurRadius:
                                    14 +
                                    (animationValue * 7),
                                spreadRadius:
                                    2 +
                                    (animationValue * 2),
                              ),
                            ],
                          ),
                          child: Center(
                            child: Container(
                              width: 48,
                              height: 48,
                              decoration: const BoxDecoration(
                                color: Color(0xFF16A34A),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(
                                Icons.check_rounded,
                                color: Colors.white,
                                size: 29,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 14),
        const Center(
          child: Text(
            'จองนัดสำเร็จ',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 20,
              fontWeight: FontWeight.w600,
              height: 1.3,
              color: AppTheme.textPrimaryColor,
            ),
          ),
        ),
        const SizedBox(height: 8),
        _buildConfirmedBadge(),
        const SizedBox(height: 10),
        const Center(
          child: Text(
            'ระบบได้บันทึกและยืนยันการนัดหมายของคุณเรียบร้อยแล้ว',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 12,
              fontWeight: FontWeight.w400,
              height: 1.4,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSuccessDot({
    required double size,
    required Color color,
  }) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
      ),
    );
  }

  Widget _buildConfirmedBadge() {
    return Center(
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: 13,
          vertical: 5,
        ),
        decoration: BoxDecoration(
          color: const Color(0xFFD9FBE2),
          borderRadius: BorderRadius.circular(20),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.check_circle_rounded,
              size: 14,
              color: Color(0xFF16A34A),
            ),
            SizedBox(width: 5),
            Text(
              'ยืนยันแล้ว',
              style: TextStyle(
                fontFamily: 'Kanit',
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: Color(0xFF15803D),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppointmentCard(
    BuildContext context,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(
        16,
        16,
        16,
        18,
      ),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFFE8ECF2),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(
              alpha: 0.035,
            ),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildDoctorInfo(),
          const SizedBox(height: 16),
          const Divider(
            height: 1,
            thickness: 1,
            color: Color(0xFFE9EDF2),
          ),
          const SizedBox(height: 16),
          _buildAppointmentInfo(
            icon: Icons.calendar_today_outlined,
            label: 'วันที่',
            value: _formatThaiDate(
              widget.appointment.appointmentDate,
            ),
          ),
          const SizedBox(height: 13),
          _buildAppointmentInfo(
            icon: Icons.access_time_rounded,
            label: 'เวลา',
            value:
                '${widget.appointment.startTime} – '
                '${widget.appointment.endTime} น.',
          ),
        ],
      ),
    );
  }

  Widget _buildDoctorInfo() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        _buildDoctorAvatar(),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _doctorName(),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  height: 1.2,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              const SizedBox(height: 3),
              Text(
                _doctorSpecialization(),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 12,
                  fontWeight: FontWeight.w400,
                  height: 1.3,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildAppointmentInfo({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: AppTheme.primaryBackgroundColor,
            borderRadius: BorderRadius.circular(9),
          ),
          child: Icon(
            icon,
            size: 16,
            color: AppTheme.primaryColor,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 12,
                  fontWeight: FontWeight.w400,
                  color: AppTheme.textMutedColor,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  height: 1.3,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDetailButton(
    BuildContext context,
  ) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton(
        onPressed: () {
          Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(
              builder: (_) => AppointmentDetailsPage(
                doctor: widget.doctor,
                appointment: widget.appointment,
              ),
            ),
            (route) => route.isFirst,
          );
        },
        style: ElevatedButton.styleFrom(
          elevation: 2,
          shadowColor: AppTheme.primaryColor.withValues(
            alpha: 0.25,
          ),
          backgroundColor: AppTheme.primaryColor,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: const Text(
          'ดูรายละเอียดการนัดหมาย',
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

  Widget _buildHomeButton(
    BuildContext context,
  ) {
    return SizedBox(
      width: double.infinity,
      height: 36,
      child: TextButton(
        onPressed: () {
          Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(
              builder: (_) => const AppShell(),
            ),
            (route) => false,
          );
        },
        style: TextButton.styleFrom(
          foregroundColor: AppTheme.primaryColor,
          padding: EdgeInsets.zero,
        ),
        child: const Text(
          'กลับหน้าหลัก',
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppTheme.primaryColor,
          ),
        ),
      ),
    );
  }

  String _formatThaiDate(
    DateTime date,
  ) {
    const months = [
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

    final buddhistYear = date.year + 543;

    return '${date.day} '
        '${months[date.month - 1]} '
        '$buddhistYear';
  }
}