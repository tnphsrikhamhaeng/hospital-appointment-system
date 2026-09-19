import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/theme/app_theme.dart';

import '../../../search/data/models/doctor_model.dart';
import '../../../search/presentation/pages/doctor_schedule_page.dart';

import '../../data/models/appointment_model.dart';
import '../../data/models/appointment_qr_model.dart';
import '../../data/repositories/appointment_qr_repository.dart';
import '../../data/services/appointment_api_service.dart';
import '../../data/services/appointment_qr_api_service.dart';

class _NoStretchScrollBehavior extends ScrollBehavior {
  const _NoStretchScrollBehavior();

  @override
  Widget buildOverscrollIndicator(
    BuildContext context,
    Widget child,
    ScrollableDetails details,
  ) {
    return child;
  }
}

class AppointmentDetailsPage extends StatefulWidget {
  final AppointmentModel appointment;
  final DoctorModel doctor;

  const AppointmentDetailsPage({
    super.key,
    required this.appointment,
    required this.doctor,
  });

  @override
  State<AppointmentDetailsPage> createState() => _AppointmentDetailsPageState();
}

class _AppointmentDetailsPageState extends State<AppointmentDetailsPage> {
  late AppointmentModel _appointment;

  late final AppointmentApiService _appointmentApiService;
  late final AppointmentQrRepository _appointmentQrRepository;

  bool _isCancelling = false;
  bool _isLoadingQr = false;

  @override
  void initState() {
    super.initState();

    _appointment = widget.appointment;

    final apiClient = ApiClient();

    _appointmentApiService = AppointmentApiService(apiClient: apiClient);

    _appointmentQrRepository = AppointmentQrRepository(
      apiService: AppointmentQrApiService(apiClient: apiClient),
    );
  }

  String _doctorName() {
    final title = widget.doctor.preface == DoctorPreface.mrDoctor
        ? 'นายแพทย์'
        : 'แพทย์หญิง';

    return '$title ${widget.doctor.firstName} '
        '${widget.doctor.lastName}';
  }

  String _doctorSpecialization() {
    if (widget.doctor.specializations.isEmpty) {
      return 'แพทย์ผู้เชี่ยวชาญ';
    }

    return widget.doctor.specializations.first.name;
  }

  String _departmentName() {
    return widget.doctor.department.name;
  }

  String _statusText() {
    switch (_appointment.status) {
      case AppointmentStatus.confirmed:
        return 'ยืนยันแล้ว';

      case AppointmentStatus.checkedIn:
        return 'เช็คอินแล้ว';

      case AppointmentStatus.inProgress:
        return 'กำลังตรวจ';

      case AppointmentStatus.completed:
        return 'เสร็จสิ้น';

      case AppointmentStatus.cancelled:
        return 'ยกเลิกแล้ว';

      case AppointmentStatus.noShow:
        return 'ไม่มาตามนัด';
    }
  }

  Color _statusColor() {
    switch (_appointment.status) {
      case AppointmentStatus.cancelled:
      case AppointmentStatus.noShow:
        return AppTheme.errorColor;

      case AppointmentStatus.confirmed:
        return AppTheme.successColor;

      case AppointmentStatus.checkedIn:
        return AppTheme.checkInColor;

      case AppointmentStatus.inProgress:
        return AppTheme.primaryColor;

      case AppointmentStatus.completed:
        return AppTheme.primaryColor;
    }
  }

  bool get _canManageAppointment {
    return _appointment.status == AppointmentStatus.confirmed;
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
        leading: IconButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
        ),
        title: const Text(
          'รายละเอียดการนัดหมาย',
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
        child: ScrollConfiguration(
          behavior: const _NoStretchScrollBehavior(),
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(20, 18, 20, 40),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildDoctorCard(),
                const SizedBox(height: 24),
                const Text(
                  'รายละเอียดการนัดหมาย',
                  style: TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const SizedBox(height: 12),
                _buildAppointmentInfoCard(),
                const SizedBox(height: 24),
                if (_canManageAppointment) ...[
                  _buildQrButton(context),
                  const SizedBox(height: 12),
                  _buildActionButtons(),
                ],
              ],
            ),
          ),
        ),
      ),
    );
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

  Widget _buildDoctorCard() {
    final statusColor = _statusColor();
    final imageUrl = _resolveDoctorImageUrl(
      widget.doctor.profileImageUrl,
    );

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8ECF2)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.035),
            blurRadius: 12,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 58,
            height: 58,
            decoration: BoxDecoration(
              color: AppTheme.primaryBackgroundColor,
              shape: BoxShape.circle,
              border: Border.all(
                color: const Color(0xFFDDE8F7),
                width: 2,
              ),
            ),
            clipBehavior: Clip.antiAlias,
            child: imageUrl == null
                ? const Icon(
                    Icons.person_rounded,
                    color: AppTheme.primaryColor,
                    size: 30,
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
                        size: 30,
                      );
                    },
                  ),
          ),
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
                    fontSize: 13,
                    fontWeight: FontWeight.w400,
                    color: AppTheme.textSecondaryColor,
                  ),
                ),
                const SizedBox(height: 7),
                Row(
                  children: [
                    _buildSmallBadge(
                      icon: Icons.local_hospital_outlined,
                      text: _departmentName(),
                    ),
                    const SizedBox(width: 6),
                    _buildStatusBadge(statusColor),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSmallBadge({
    required IconData icon,
    required String text,
  }) {
    return Flexible(
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: 7,
          vertical: 4,
        ),
        decoration: BoxDecoration(
          color: AppTheme.primaryBackgroundColor,
          borderRadius: BorderRadius.circular(10),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 11,
              color: AppTheme.primaryColor,
            ),
            const SizedBox(width: 4),
            Flexible(
              child: Text(
                text,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: AppTheme.primaryDarkColor,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(Color statusColor) {
    final isCancelled =
        _appointment.status == AppointmentStatus.cancelled;

    return Flexible(
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: 7,
          vertical: 4,
        ),
        decoration: BoxDecoration(
          color: statusColor.withValues(alpha: 0.10),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              isCancelled
                  ? Icons.cancel_outlined
                  : Icons.check_circle_outline_rounded,
              size: 11,
              color: statusColor,
            ),
            const SizedBox(width: 4),
            Flexible(
              child: Text(
                _statusText(),
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: statusColor,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppointmentInfoCard() {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFFE8ECF2),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.035),
            blurRadius: 12,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          _buildInfoRow(
            icon: Icons.calendar_month_rounded,
            label: 'วันที่และเวลา',
            value: _formatThaiDate(
              _appointment.appointmentDate,
            ),
            secondaryValue:
                '${_appointment.startTime} – '
                '${_appointment.endTime} น.',
          ),
          if (_appointment.reason != null &&
              _appointment.reason!.trim().isNotEmpty) ...[
            const Divider(
              height: 1,
              thickness: 1,
              color: Color(0xFFE9EDF2),
            ),
            _buildInfoRow(
              icon: Icons.notes_rounded,
              label: 'เหตุผลการนัดหมาย',
              value: _appointment.reason!,
            ),
          ],
          if (_appointment.cancelledReason != null &&
              _appointment.cancelledReason!.trim().isNotEmpty) ...[
            const Divider(
              height: 1,
              thickness: 1,
              color: Color(0xFFE9EDF2),
            ),
            _buildInfoRow(
              icon: Icons.info_outline_rounded,
              label: 'เหตุผลที่ยกเลิก',
              value: _appointment.cancelledReason!,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow({
    required IconData icon,
    required String label,
    required String value,
    String? secondaryValue,
  }) {
    return Padding(
      padding: const EdgeInsets.all(14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: AppTheme.primaryBackgroundColor,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              icon,
              color: AppTheme.primaryColor,
              size: 19,
            ),
          ),
          const SizedBox(width: 11),
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
                const SizedBox(height: 3),
                Text(
                  value,
                  style: const TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    height: 1.4,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                if (secondaryValue != null) ...[
                  const SizedBox(height: 2),
                  Text(
                    secondaryValue,
                    style: const TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 12,
                      fontWeight: FontWeight.w400,
                      height: 1.4,
                      color: AppTheme.textSecondaryColor,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQrButton(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton.icon(
        onPressed: _isLoadingQr ? null : _showQrCode,
        icon: _isLoadingQr
            ? const SizedBox(
                width: 19,
                height: 19,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : const Icon(
                Icons.qr_code_2_rounded,
                size: 19,
              ),
        label: Text(
          _isLoadingQr
              ? 'กำลังโหลด QR Code...'
              : 'ดู QR Code สำหรับเช็คอิน',
          style: const TextStyle(
            fontFamily: 'Kanit',
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: AppTheme.primaryColor,
          foregroundColor: Colors.white,
          disabledBackgroundColor:
              AppTheme.primaryColor.withValues(alpha: 0.65),
          disabledForegroundColor: Colors.white,
          elevation: 2,
          shadowColor:
              AppTheme.primaryColor.withValues(alpha: 0.22),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }

  Future<void> _showQrCode() async {
    if (_isLoadingQr) {
      return;
    }

    setState(() {
      _isLoadingQr = true;
    });

    try {
      final qr = await _appointmentQrRepository.getQr(
        appointmentId: _appointment.id,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _isLoadingQr = false;
      });

      await showDialog<void>(
        context: context,
        barrierDismissible: true,
        builder: (dialogContext) {
          return Dialog(
            backgroundColor: Colors.transparent,
            elevation: 0,
            insetPadding:
                const EdgeInsets.symmetric(horizontal: 24),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(
                20,
                24,
                20,
                20,
              ),
              decoration: BoxDecoration(
                color: AppTheme.surfaceColor,
                borderRadius: BorderRadius.circular(24),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: const BoxDecoration(
                      color: AppTheme.primaryBackgroundColor,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.qr_code_2_rounded,
                      color: AppTheme.primaryColor,
                      size: 30,
                    ),
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    'QR Code สำหรับเช็คอิน',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.primaryDarkColor,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'แสดง QR Code นี้ให้เจ้าหน้าที่สแกน',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 12,
                      color: AppTheme.textSecondaryColor,
                    ),
                  ),
                  const SizedBox(height: 18),
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: const Color(0xFFE8ECF2),
                      ),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        QrImageView(
                          data: qr.token,
                          version: QrVersions.auto,
                          size: 220,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          qr.token,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontFamily: 'Kanit',
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 1.2,
                            color: AppTheme.textPrimaryColor,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildQrExpiryInfo(qr),
                  const SizedBox(height: 18),
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.of(dialogContext).pop();
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.primaryColor,
                        foregroundColor: Colors.white,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text(
                        'ตกลง',
                        style: TextStyle(
                          fontFamily: 'Kanit',
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
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
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoadingQr = false;
      });

      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: Text(
              _getQrErrorMessage(error),
              style: const TextStyle(fontFamily: 'Kanit'),
            ),
          ),
        );
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoadingQr = false;
      });

      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: Text(
              error.toString().replaceFirst(
                'Exception: ',
                '',
              ),
              style: const TextStyle(fontFamily: 'Kanit'),
            ),
          ),
        );
    }
  }

  Widget _buildQrExpiryInfo(AppointmentQrModel qr) {
    final localExpiredAt = qr.expiredAt.toLocal();

    return Column(
      children: [
        const Text(
          'QR Code หมดอายุ',
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 10,
            color: AppTheme.textMutedColor,
          ),
        ),
        const SizedBox(height: 3),
        Text(
          '${_formatThaiDate(localExpiredAt)} '
          '${_formatTime(localExpiredAt)} น.',
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontFamily: 'Kanit',
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: AppTheme.errorColor,
          ),
        ),
        const SizedBox(height: 5),
        const Text(
          'สามารถเช็คอินได้ตั้งแต่ 1 ชั่วโมงก่อนเวลานัด '
          'จนถึง 15 นาทีหลังเวลานัด',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 10,
            height: 1.4,
            color: AppTheme.textSecondaryColor,
          ),
        ),
      ],
    );
  }

  String _getQrErrorMessage(DioException error) {
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

    if (error.response?.statusCode == 404) {
      return 'ไม่พบ QR Code สำหรับนัดหมายนี้';
    }

    if (error.response?.statusCode == 400) {
      return 'ไม่สามารถสร้าง QR Code สำหรับนัดหมายนี้ได้';
    }

    return 'ไม่สามารถโหลด QR Code ได้ กรุณาลองใหม่';
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          height: 52,
          child: OutlinedButton(
            onPressed: _openReschedulePage,
            style: OutlinedButton.styleFrom(
              foregroundColor: AppTheme.primaryColor,
              side: const BorderSide(
                color: AppTheme.primaryColor,
                width: 1.2,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              padding: const EdgeInsets.symmetric(
                horizontal: 16,
              ),
            ),
            child: const Text(
              'แก้ไขนัดหมาย',
              style: TextStyle(
                fontFamily: 'Kanit',
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          height: 52,
          child: OutlinedButton(
            onPressed:
                _isCancelling ? null : _showCancelDialog,
            style: OutlinedButton.styleFrom(
              foregroundColor: AppTheme.errorColor,
              disabledForegroundColor:
                  AppTheme.errorColor.withValues(alpha: 0.55),
              side: BorderSide(
                color: _isCancelling
                    ? AppTheme.errorColor.withValues(alpha: 0.35)
                    : AppTheme.errorColor,
                width: 1.2,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              padding: const EdgeInsets.symmetric(
                horizontal: 16,
              ),
            ),
            child: _isCancelling
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                    ),
                  )
                : const Text(
                    'ยกเลิกนัดหมาย',
                    style: TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
          ),
        ),
      ],
    );
  }

  Future<void> _openReschedulePage() async {
    final initialSlot = (
      date: _appointment.appointmentDate,
      startTime: _appointment.startTime,
      endTime: _appointment.endTime,
    );

    final updatedAppointment =
        await Navigator.of(context).push<AppointmentModel>(
      MaterialPageRoute(
        builder: (_) => DoctorSchedulePage(
          doctor: widget.doctor,
          isEditMode: true,
          appointmentId: _appointment.id,
          initialDate: _appointment.appointmentDate,
          initialSlot: initialSlot,
        ),
      ),
    );

    if (!mounted || updatedAppointment == null) {
      return;
    }

    setState(() {
      _appointment = updatedAppointment;
    });
  }

  Future<void> _showCancelDialog() async {
    final reasonController = TextEditingController();
    final reasonFocusNode = FocusNode();

    try {
      final shouldCancel = await showDialog<bool>(
        context: context,
        barrierDismissible: true,
        builder: (dialogContext) {
          String? reasonError;

          return StatefulBuilder(
            builder: (context, setDialogState) {
              return Dialog(
                backgroundColor: Colors.transparent,
                elevation: 0,
                insetPadding:
                    const EdgeInsets.symmetric(horizontal: 24),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.fromLTRB(
                    20,
                    22,
                    20,
                    20,
                  ),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceColor,
                    borderRadius: BorderRadius.circular(22),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment:
                        CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'ยืนยันการยกเลิกนัดหมาย',
                        style: TextStyle(
                          fontFamily: 'Kanit',
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.textPrimaryColor,
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: reasonController,
                        focusNode: reasonFocusNode,
                        maxLines: 3,
                        maxLength: 500,
                        onChanged: (value) {
                          if (reasonError != null &&
                              value.trim().isNotEmpty) {
                            setDialogState(() {
                              reasonError = null;
                            });
                          }
                        },
                        decoration: InputDecoration(
                          hintText: 'ระบุเหตุผลการยกเลิก',
                          hintStyle: const TextStyle(
                            fontFamily: 'Kanit',
                            fontSize: 13,
                            color: AppTheme.textSecondaryColor,
                          ),
                          errorText: reasonError,
                          errorStyle: const TextStyle(
                            fontFamily: 'Kanit',
                            fontSize: 11,
                            color: AppTheme.errorColor,
                          ),
                          filled: true,
                          fillColor: AppTheme.backgroundColor,
                          border: OutlineInputBorder(
                            borderRadius:
                                BorderRadius.circular(14),
                            borderSide: const BorderSide(
                              color: Color(0xFFE3E8EF),
                            ),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius:
                                BorderRadius.circular(14),
                            borderSide: const BorderSide(
                              color: Color(0xFFE3E8EF),
                            ),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius:
                                BorderRadius.circular(14),
                            borderSide: const BorderSide(
                              color: AppTheme.primaryColor,
                              width: 1.2,
                            ),
                          ),
                          errorBorder: OutlineInputBorder(
                            borderRadius:
                                BorderRadius.circular(14),
                            borderSide: const BorderSide(
                              color: AppTheme.errorColor,
                              width: 1.2,
                            ),
                          ),
                          focusedErrorBorder:
                              OutlineInputBorder(
                            borderRadius:
                                BorderRadius.circular(14),
                            borderSide: const BorderSide(
                              color: AppTheme.errorColor,
                              width: 1.2,
                            ),
                          ),
                          contentPadding:
                              const EdgeInsets.all(14),
                          counterStyle: const TextStyle(
                            fontFamily: 'Kanit',
                            fontSize: 11,
                            color:
                                AppTheme.textSecondaryColor,
                          ),
                        ),
                        style: const TextStyle(
                          fontFamily: 'Kanit',
                          fontSize: 14,
                          color:
                              AppTheme.textPrimaryColor,
                        ),
                      ),
                      const SizedBox(height: 8),
                      SizedBox(
                        width: double.infinity,
                        height: 50,
                        child: ElevatedButton(
                          onPressed: () {
                            if (reasonController.text
                                .trim()
                                .isEmpty) {
                              setDialogState(() {
                                reasonError =
                                    'กรุณากรอกเหตุผลการยกเลิก';
                              });

                              reasonFocusNode.requestFocus();
                              return;
                            }

                            reasonFocusNode.unfocus();
                            Navigator.of(dialogContext).pop(true);
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor:
                                AppTheme.primaryColor,
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                              borderRadius:
                                  BorderRadius.circular(12),
                            ),
                          ),
                          child: const Text(
                            'ยืนยันการยกเลิก',
                            style: TextStyle(
                              fontFamily: 'Kanit',
                              fontSize: 14,
                              fontWeight:
                                  FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 10),
                      SizedBox(
                        width: double.infinity,
                        height: 50,
                        child: OutlinedButton(
                          onPressed: () {
                            Navigator.of(dialogContext)
                                .pop(false);
                          },
                          style:
                              OutlinedButton.styleFrom(
                            foregroundColor:
                                AppTheme.textSecondaryColor,
                            side: const BorderSide(
                              color: Color(0xFFD8DEE7),
                              width: 1.1,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius:
                                  BorderRadius.circular(12),
                            ),
                          ),
                          child: const Text(
                            'กลับ',
                            style: TextStyle(
                              fontFamily: 'Kanit',
                              fontSize: 14,
                              fontWeight:
                                  FontWeight.w600,
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
        },
      );

      if (shouldCancel != true ||
          reasonController.text.trim().isEmpty ||
          !mounted) {
        return;
      }

      await _cancelAppointment(
        reasonController.text.trim(),
      );
    } finally {
      reasonFocusNode.dispose();
      reasonController.dispose();
    }
  }

  Future<void> _cancelAppointment(String reason) async {
    if (_isCancelling) {
      return;
    }

    setState(() {
      _isCancelling = true;
    });

    try {
      final response =
          await _appointmentApiService.cancelAppointment(
        appointmentId: _appointment.id,
        cancelledReason: reason,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _appointment = response;
        _isCancelling = false;
      });

      await _showCancelSuccessDialog();
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isCancelling = false;
      });

      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: Text(
              _getErrorMessage(error),
              style: const TextStyle(
                fontFamily: 'Kanit',
              ),
            ),
          ),
        );
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isCancelling = false;
      });

      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: Text(
              error.toString().replaceFirst(
                'Exception: ',
                '',
              ),
              style: const TextStyle(
                fontFamily: 'Kanit',
              ),
            ),
          ),
        );
    }
  }

  Future<void> _showCancelSuccessDialog() async {
    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return Dialog(
          backgroundColor: Colors.transparent,
          elevation: 0,
          insetPadding:
              const EdgeInsets.symmetric(horizontal: 24),
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(
              20,
              22,
              20,
              18,
            ),
            decoration: BoxDecoration(
              color: AppTheme.surfaceColor,
              borderRadius: BorderRadius.circular(22),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 54,
                  height: 54,
                  decoration: const BoxDecoration(
                    color: Color(0xFFE8F6EA),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.check_rounded,
                    color: Color(0xFF3FA456),
                    size: 32,
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'ยกเลิกนัดหมายสำเร็จ',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const SizedBox(height: 7),
                const Text(
                  'นัดหมายของคุณถูกยกเลิกเรียบร้อยแล้ว',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 12,
                    color: AppTheme.textSecondaryColor,
                  ),
                ),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor:
                          AppTheme.primaryColor,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text(
                      'ตกลง',
                      style: TextStyle(
                        fontFamily: 'Kanit',
                        fontSize: 14,
                        fontWeight:
                            FontWeight.w600,
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

  String _getErrorMessage(DioException error) {
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

    if (error.response?.statusCode == 409) {
      return 'ไม่สามารถยกเลิกนัดหมายนี้ได้';
    }

    if (error.response?.statusCode == 404) {
      return 'ไม่พบข้อมูลนัดหมาย';
    }

    return 'ไม่สามารถยกเลิกนัดหมายได้ กรุณาลองใหม่';
  }

  String _formatThaiDate(DateTime date) {
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

  String _formatTime(DateTime dateTime) {
    final hour =
        dateTime.hour.toString().padLeft(2, '0');
    final minute =
        dateTime.minute.toString().padLeft(2, '0');

    return '$hour:$minute';
  }
}