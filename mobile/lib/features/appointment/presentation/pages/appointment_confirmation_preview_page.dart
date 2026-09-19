import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/storage/token_storage.dart';
import '../../../../core/theme/app_theme.dart';

import '../../../search/data/models/doctor_model.dart';

import '../../data/models/appointment_model.dart';
import '../../data/models/appointment_slot.dart';
import '../../data/repositories/appointment_repository.dart';
import '../../data/services/appointment_api_service.dart';

import 'appointment_booking_success_page.dart';

class AppointmentConfirmationPreviewPage extends StatefulWidget {
  final DoctorModel doctor;
  final DateTime selectedDate;
  final AppointmentSlot selectedSlot;
  final bool isEditMode;
  final String? appointmentId;
  final void Function(
    DateTime date,
    AppointmentSlot slot,
  )? onUpdated;

  const AppointmentConfirmationPreviewPage({
    super.key,
    required this.doctor,
    required this.selectedDate,
    required this.selectedSlot,
    this.isEditMode = false,
    this.appointmentId,
    this.onUpdated,
  });

  @override
  State<AppointmentConfirmationPreviewPage> createState() =>
      _AppointmentConfirmationPreviewPageState();
}

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

class _AppointmentConfirmationPreviewPageState
    extends State<AppointmentConfirmationPreviewPage>
    with SingleTickerProviderStateMixin {
  late final AnimationController _checkAnimationController;
  late final Animation<double> _checkScaleAnimation;
  late final Animation<double> _checkMoveAnimation;

  late final AppointmentRepository _appointmentRepository;
  late final TokenStorage _tokenStorage;

  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();

    _appointmentRepository = AppointmentRepository(
      appointmentApiService: AppointmentApiService(
        apiClient: ApiClient(),
      ),
    );

    _tokenStorage = TokenStorage();

    _checkAnimationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);

    _checkScaleAnimation = Tween<double>(
      begin: 0.90,
      end: 1.08,
    ).animate(
      CurvedAnimation(
        parent: _checkAnimationController,
        curve: Curves.easeInOut,
      ),
    );

    _checkMoveAnimation = Tween<double>(
      begin: 2.0,
      end: -2.0,
    ).animate(
      CurvedAnimation(
        parent: _checkAnimationController,
        curve: Curves.easeInOut,
      ),
    );
  }

  @override
  void dispose() {
    _checkAnimationController.dispose();
    super.dispose();
  }

  String _doctorName() {
    final title = widget.doctor.preface == DoctorPreface.mrDoctor
        ? 'นายแพทย์'
        : 'แพทย์หญิง';

    return '$title ${widget.doctor.firstName} ${widget.doctor.lastName}';
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

  Future<String?> _getPatientIdFromToken() async {
    final accessToken = await _tokenStorage.getAccessToken();

    if (accessToken == null || accessToken.isEmpty) {
      return null;
    }

    final parts = accessToken.split('.');

    if (parts.length != 3) {
      return null;
    }

    try {
      final payload = _decodeJwtPayload(parts[1]);

      final subject = payload['sub'];

      if (subject is String && subject.isNotEmpty) {
        return subject;
      }

      return null;
    } catch (_) {
      return null;
    }
  }

  Map<String, dynamic> _decodeJwtPayload(
    String encodedPayload,
  ) {
    final normalized = base64Url.normalize(encodedPayload);

    final decoded = utf8.decode(
      base64Url.decode(normalized),
    );

    final payload = jsonDecode(decoded);

    if (payload is! Map) {
      throw const FormatException(
        'Invalid JWT payload',
      );
    }

    return Map<String, dynamic>.from(payload);
  }

  Future<void> _createAppointment() async {
    if (_isSubmitting) {
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final patientId = await _getPatientIdFromToken();

      if (patientId == null) {
        throw Exception(
          'ไม่พบข้อมูลผู้ป่วยจากบัญชีที่เข้าสู่ระบบ',
        );
      }

      final appointment =
          await _appointmentRepository.createAppointment(
        patientId: patientId,
        doctorId: widget.doctor.id,
        appointmentDate: widget.selectedDate,
        startTime: widget.selectedSlot.startTime,
      );

      if (!mounted) {
        return;
      }

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => AppointmentBookingSuccessPage(
            doctor: widget.doctor,
            appointment: appointment,
          ),
        ),
      );
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isSubmitting = false;
      });

      _showErrorMessage(
        _getDioErrorMessage(error),
      );
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isSubmitting = false;
      });

      _showErrorMessage(
        error.toString().replaceFirst(
          'Exception: ',
          '',
        ),
      );
    }
  }

  Future<void> _rescheduleAppointment() async {
    if (_isSubmitting) {
      return;
    }

    final appointmentId = widget.appointmentId;

    if (appointmentId == null ||
        appointmentId.isEmpty) {
      _showErrorMessage(
        'ไม่พบรหัสนัดหมายสำหรับแก้ไข',
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final appointment =
          await _appointmentRepository.rescheduleAppointment(
        appointmentId: appointmentId,
        appointmentDate: widget.selectedDate,
        startTime: widget.selectedSlot.startTime,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _isSubmitting = false;
      });

      _showEditSuccessDialog(
        appointment: appointment,
      );
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isSubmitting = false;
      });

      _showErrorMessage(
        _getDioErrorMessage(error),
      );
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isSubmitting = false;
      });

      _showErrorMessage(
        error.toString().replaceFirst(
          'Exception: ',
          '',
        ),
      );
    }
  }

  String _getDioErrorMessage(
    DioException error,
  ) {
    final responseData = error.response?.data;

    if (responseData is Map) {
      final detail = responseData['detail'];

      if (detail is String &&
          detail.isNotEmpty) {
        return detail;
      }

      if (detail is Map) {
        final message = detail['message'];

        if (message is String &&
            message.isNotEmpty) {
          return message;
        }
      }
    }

    if (error.response?.statusCode == 400) {
      return 'ข้อมูลการนัดหมายไม่ถูกต้อง กรุณาตรวจสอบวันที่และเวลาอีกครั้ง';
    }

    if (error.response?.statusCode == 404) {
      return 'ไม่พบข้อมูลนัดหมาย';
    }

    if (error.response?.statusCode == 409) {
      return 'เวลานี้มีผู้จองแล้ว กรุณาเลือกเวลาอื่น';
    }

    if (error.response?.statusCode == 401) {
      return 'เซสชันหมดอายุ กรุณาเข้าสู่ระบบใหม่';
    }

    return 'ไม่สามารถดำเนินการได้ กรุณาลองใหม่อีกครั้ง';
  }

  void _showErrorMessage(
    String message,
  ) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(
            message,
            style: const TextStyle(
              fontFamily: 'Kanit',
            ),
          ),
        ),
      );
  }

  Future<void> _handleConfirm() async {
    if (widget.isEditMode) {
      await _rescheduleAppointment();
      return;
    }

    await _createAppointment();
  }

  void _showEditSuccessDialog({
    required AppointmentModel appointment,
  }) {
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.symmetric(
            horizontal: 40,
          ),
          child: Container(
            width: double.infinity,
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
                  'แก้ไขนัดหมายสำเร็จ',
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
                  'นัดหมายของคุณถูกแก้ไขเรียบร้อยแล้ว',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 16,
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

                      widget.onUpdated?.call(
                        widget.selectedDate,
                        widget.selectedSlot,
                      );

                      Navigator.of(context).pop(
                        appointment,
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      elevation: 0,
                      backgroundColor:
                          AppTheme.primaryColor,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text(
                      'ตกลง',
                      style: TextStyle(
                        fontFamily: 'Kanit',
                        fontSize: 13,
                        fontWeight:
                            FontWeight.w600,
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor:
          AppTheme.backgroundColor,
      appBar: AppBar(
        backgroundColor:
            AppTheme.surfaceColor,
        surfaceTintColor:
            Colors.transparent,
        elevation: 0,
        automaticallyImplyLeading: false,
        title: const Text(
          'ยืนยันนัดหมาย',
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 20,
            fontWeight:
                FontWeight.w600,
            color:
                AppTheme.textPrimaryColor,
          ),
        ),
        centerTitle: true,
        bottom:
            const PreferredSize(
          preferredSize:
              Size.fromHeight(1),
          child: Divider(
            height: 1,
            thickness: 1,
            color:
                Color(0xFFE8ECF2),
          ),
        ),
      ),
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return ScrollConfiguration(
              behavior:
                  const _NoStretchScrollBehavior(),
              child: SingleChildScrollView(
                physics:
                    const AlwaysScrollableScrollPhysics(),
                padding:
                    const EdgeInsets.fromLTRB(
                  20,
                  12,
                  20,
                  24,
                ),
                child: ConstrainedBox(
                  constraints:
                      BoxConstraints(
                    minHeight:
                        constraints.maxHeight -
                            36,
                  ),
                  child: Column(
                    mainAxisAlignment:
                        MainAxisAlignment.center,
                    crossAxisAlignment:
                        CrossAxisAlignment.start,
                    children: [
                      _buildConfirmationHeader(
                        context,
                      ),
                      const SizedBox(
                        height: 22,
                      ),
                      _buildAppointmentCard(
                        context,
                      ),
                      const SizedBox(
                        height: 20,
                      ),
                      _buildConfirmButton(
                        context,
                      ),
                      const SizedBox(
                        height: 10,
                      ),
                      _buildEditButton(
                        context,
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildConfirmationHeader(
    BuildContext context,
  ) {
    return Column(
      children: [
        Center(
          child: AnimatedBuilder(
            animation:
                _checkAnimationController,
            builder:
                (context, child) {
              return Container(
                width: 72,
                height: 72,
                decoration:
                    BoxDecoration(
                  color: AppTheme
                      .primaryBackgroundColor,
                  shape:
                      BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme
                          .primaryColor
                          .withValues(
                        alpha:
                            0.08 +
                                (_checkAnimationController
                                        .value *
                                    0.10),
                      ),
                      blurRadius:
                          12 +
                              (_checkAnimationController
                                      .value *
                                  8),
                      spreadRadius:
                          1 +
                              (_checkAnimationController
                                      .value *
                                  2),
                    ),
                  ],
                ),
                child: Center(
                  child:
                      Transform.translate(
                    offset: Offset(
                      0,
                      _checkMoveAnimation
                          .value,
                    ),
                    child:
                        Transform.scale(
                      scale:
                          _checkScaleAnimation
                              .value,
                      child: Container(
                        width: 44,
                        height: 44,
                        decoration:
                            const BoxDecoration(
                          color: Color(
                            0xFFE8EEF8,
                          ),
                          shape:
                              BoxShape.circle,
                        ),
                        child:
                            const Icon(
                          Icons
                              .check_circle_outline_rounded,
                          color: AppTheme
                              .primaryColor,
                          size: 27,
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 18),
        Center(
          child: Text(
            widget.isEditMode
                ? 'ตรวจสอบการแก้ไขนัดหมาย'
                : 'ตรวจสอบข้อมูลการนัดหมาย',
            textAlign:
                TextAlign.center,
            style:
                const TextStyle(
              fontFamily: 'Kanit',
              fontSize: 20,
              fontWeight:
                  FontWeight.w600,
              height: 1.3,
              color: AppTheme
                  .textPrimaryColor,
            ),
          ),
        ),
        const SizedBox(height: 6),
        const Center(
          child: Text(
            'กรุณาตรวจสอบรายละเอียดการนัดหมายของคุณ',
            textAlign:
                TextAlign.center,
            style:
                TextStyle(
              fontFamily: 'Kanit',
              fontSize: 12,
              fontWeight:
                  FontWeight.w400,
              height: 1.4,
              color: AppTheme
                  .textSecondaryColor,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildAppointmentCard(
    BuildContext context,
  ) {
    return Container(
      width: double.infinity,
      padding:
          const EdgeInsets.fromLTRB(
        16,
        16,
        16,
        18,
      ),
      decoration:
          BoxDecoration(
        color:
            AppTheme.surfaceColor,
        borderRadius:
            BorderRadius.circular(16),
        border: Border.all(
          color:
              const Color(0xFFE8ECF2),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color:
                Colors.black.withValues(
              alpha: 0.035,
            ),
            blurRadius: 12,
            offset:
                const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          _buildDoctorInfo(context),
          const SizedBox(height: 16),
          const Divider(
            height: 1,
            thickness: 1,
            color:
                Color(0xFFE9EDF2),
          ),
          const SizedBox(height: 16),
          _buildAppointmentInfo(
            context,
            icon:
                Icons.calendar_today_outlined,
            label: 'วันที่',
            value:
                _formatThaiDate(
              widget.selectedDate,
            ),
          ),
          const SizedBox(height: 13),
          _buildAppointmentInfo(
            context,
            icon:
                Icons.access_time_rounded,
            label: 'เวลา',
            value:
                '${widget.selectedSlot.startTime} – ${widget.selectedSlot.endTime} น.',
          ),
        ],
      ),
    );
  }

  Widget _buildDoctorInfo(
    BuildContext context,
  ) {
    return Row(
      crossAxisAlignment:
          CrossAxisAlignment.center,
      children: [
        _buildDoctorAvatar(),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Text(
                _doctorName(),
                maxLines: 1,
                overflow:
                    TextOverflow.ellipsis,
                style:
                    const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 16,
                  fontWeight:
                      FontWeight.w600,
                  height: 1.2,
                  color: AppTheme
                      .textPrimaryColor,
                ),
              ),
              const SizedBox(
                height: 3,
              ),
              Text(
                'แผนก: ${widget.doctor.department.name}',
                maxLines: 2,
                overflow:
                    TextOverflow.ellipsis,
                style:
                    const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 13,
                  fontWeight:
                      FontWeight.w400,
                  height: 1.3,
                  color: AppTheme
                      .textSecondaryColor,
                ),
              ),
              const SizedBox(
                height: 2,
              ),
              Text(
                _doctorSpecialization(),
                maxLines: 1,
                overflow:
                    TextOverflow.ellipsis,
                style:
                    const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 12,
                  fontWeight:
                      FontWeight.w400,
                  height: 1.3,
                  color: AppTheme
                      .textMutedColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildAppointmentInfo(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [
        Container(
          width: 32,
          height: 32,
          decoration:
              BoxDecoration(
            color: AppTheme
                .primaryBackgroundColor,
            borderRadius:
                BorderRadius.circular(
              9,
            ),
          ),
          child: Icon(
            icon,
            size: 16,
            color:
                AppTheme.primaryColor,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style:
                    const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 12,
                  fontWeight:
                      FontWeight.w400,
                  color: AppTheme
                      .textMutedColor,
                ),
              ),
              const SizedBox(
                height: 2,
              ),
              Text(
                value,
                style:
                    const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 14,
                  fontWeight:
                      FontWeight.w600,
                  height: 1.3,
                  color: AppTheme
                      .textPrimaryColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildConfirmButton(
    BuildContext context,
  ) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton(
        onPressed: _isSubmitting
            ? null
            : _handleConfirm,
        style:
            ElevatedButton.styleFrom(
          elevation: 2,
          shadowColor: AppTheme
              .primaryColor
              .withValues(
            alpha: 0.25,
          ),
          backgroundColor:
              AppTheme.primaryColor,
          disabledBackgroundColor:
              const Color(0xFFE5E9EF),
          foregroundColor:
              Colors.white,
          disabledForegroundColor:
              AppTheme.textMutedColor,
          shape:
              RoundedRectangleBorder(
            borderRadius:
                BorderRadius.circular(12),
          ),
        ),
        child: _isSubmitting
            ? const SizedBox(
                width: 22,
                height: 22,
                child:
                    CircularProgressIndicator(
                  strokeWidth: 2.5,
                  valueColor:
                      AlwaysStoppedAnimation<
                          Color>(
                    Colors.white,
                  ),
                ),
              )
            : Row(
                mainAxisAlignment:
                    MainAxisAlignment.center,
                children: [
                  Text(
                    widget.isEditMode
                        ? 'ยืนยันการแก้ไข'
                        : 'ยืนยันการจอง',
                    style:
                        const TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 14,
                      fontWeight:
                          FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(
                    width: 7,
                  ),
                  const Icon(
                    Icons
                        .arrow_forward_rounded,
                    size: 20,
                    color: Colors.white,
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildEditButton(
    BuildContext context,
  ) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: OutlinedButton(
        onPressed: _isSubmitting
            ? null
            : () =>
                Navigator.of(context)
                    .pop(),
        style:
            OutlinedButton.styleFrom(
          foregroundColor:
              AppTheme.primaryColor,
          side: BorderSide(
            color: AppTheme
                .primaryColor
                .withValues(
              alpha: 0.55,
            ),
            width: 1.2,
          ),
          shape:
              RoundedRectangleBorder(
            borderRadius:
                BorderRadius.circular(12),
          ),
        ),
        child: const Text(
          'กลับไปแก้ไขข้อมูล',
          style:
              TextStyle(
            fontFamily: 'Kanit',
            fontSize: 14,
            fontWeight:
                FontWeight.w600,
            color:
                AppTheme.primaryColor,
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

    final buddhistYear =
        date.year + 543;

    return '${date.day} '
        '${months[date.month - 1]} '
        '$buddhistYear';
  }
}