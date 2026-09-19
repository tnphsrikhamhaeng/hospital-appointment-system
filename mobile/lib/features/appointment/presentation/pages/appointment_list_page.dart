import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/storage/token_storage.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../search/data/models/doctor_model.dart';
import '../../../search/data/repositories/doctor_repository.dart';
import '../../../search/data/services/doctor_api_service.dart';
import '../../data/models/appointment_model.dart';
import '../../data/repositories/appointment_repository.dart';
import '../../data/services/appointment_api_service.dart';
import 'appointment_details_page.dart';
import '../../../search/presentation/pages/department_selection_page.dart';

enum _AppointmentFilter { upcoming, cancelled, all }

class AppointmentListPage extends StatefulWidget {
  const AppointmentListPage({super.key});

  @override
  State<AppointmentListPage> createState() => _AppointmentListPageState();
}

class _AppointmentListPageState extends State<AppointmentListPage> {
  late final AppointmentRepository _appointmentRepository;
  late final DoctorRepository _doctorRepository;
  late final TokenStorage _tokenStorage;

  final Map<String, DoctorModel> _doctorCache = {};

  List<AppointmentModel> _appointments = [];

  bool _isLoading = true;
  String? _errorMessage;
  _AppointmentFilter _selectedFilter = _AppointmentFilter.upcoming;

  @override
  void initState() {
    super.initState();

    final apiClient = ApiClient();

    _appointmentRepository = AppointmentRepository(
      appointmentApiService: AppointmentApiService(apiClient: apiClient),
    );

    _doctorRepository = DoctorRepository(
      doctorApiService: DoctorApiService(apiClient: apiClient),
    );

    _tokenStorage = TokenStorage();

    _loadAppointments();
  }

  Future<void> _loadAppointments() async {
    if (!mounted) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final patientId = await _getPatientIdFromToken();

      if (patientId == null) {
        throw Exception('ไม่พบข้อมูลผู้ป่วยจากบัญชีที่เข้าสู่ระบบ');
      }

      final appointments = await _appointmentRepository.getPatientAppointments(
        patientId: patientId,
      );

      final doctors = <String, DoctorModel>{};

      for (final appointment in appointments) {
        if (doctors.containsKey(appointment.doctorId)) {
          continue;
        }

        final cachedDoctor = _doctorCache[appointment.doctorId];

        if (cachedDoctor != null) {
          doctors[appointment.doctorId] = cachedDoctor;
          continue;
        }

        final doctor = await _doctorRepository.getDoctorById(
          doctorId: appointment.doctorId,
        );

        doctors[appointment.doctorId] = doctor;

        _doctorCache[appointment.doctorId] = doctor;
      }

      if (!mounted) {
        return;
      }

      setState(() {
        _appointments = appointments;
        _isLoading = false;
      });
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
        _errorMessage = _getDioErrorMessage(error);
      });
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
        _errorMessage = error.toString().replaceFirst('Exception: ', '');
      });
    }
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

  Map<String, dynamic> _decodeJwtPayload(String encodedPayload) {
    final normalized = base64Url.normalize(encodedPayload);

    final decoded = utf8.decode(base64Url.decode(normalized));

    final payload = jsonDecode(decoded);

    if (payload is! Map) {
      throw const FormatException('Invalid JWT payload');
    }

    return Map<String, dynamic>.from(payload);
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

    if (error.response?.statusCode == 401) {
      return 'เซสชันหมดอายุ กรุณาเข้าสู่ระบบใหม่';
    }

    return 'ไม่สามารถโหลดรายการนัดหมายได้ กรุณาลองใหม่';
  }

  DoctorModel? _doctorFor(AppointmentModel appointment) {
    return _doctorCache[appointment.doctorId];
  }

  List<AppointmentModel> _upcomingAppointments() {
    final appointments = _appointments.where(_isUpcomingAppointment).toList();

    appointments.sort((a, b) {
      return _appointmentDateTime(a).compareTo(_appointmentDateTime(b));
    });

    return appointments;
  }

  List<AppointmentModel> _cancelledAppointments() {
    final appointments = _appointments
        .where(
          (appointment) =>
              appointment.status == AppointmentStatus.cancelled ||
              appointment.status == AppointmentStatus.noShow,
        )
        .toList();

    appointments.sort((a, b) {
      return _appointmentDateTime(b).compareTo(_appointmentDateTime(a));
    });

    return appointments;
  }

  List<AppointmentModel> _allActiveAppointments() {
    final appointments = _appointments
        .where(
          (appointment) =>
              appointment.status != AppointmentStatus.cancelled &&
              appointment.status != AppointmentStatus.noShow,
        )
        .toList();

    appointments.sort((a, b) {
      return _appointmentDateTime(b).compareTo(_appointmentDateTime(a));
    });

    return appointments;
  }

  bool _isUpcomingAppointment(AppointmentModel appointment) {
    if (appointment.status == AppointmentStatus.cancelled ||
        appointment.status == AppointmentStatus.completed ||
        appointment.status == AppointmentStatus.noShow) {
      return false;
    }

    final appointmentStart = _appointmentDateTime(appointment);

    final checkInExpired = appointmentStart.add(
      const Duration(minutes: 15),
    );

    return DateTime.now().isBefore(checkInExpired);
  }

  DateTime _appointmentDateTime(AppointmentModel appointment) {
    final timeParts = appointment.startTime.split(':');

    final hour = timeParts.isNotEmpty ? int.tryParse(timeParts[0]) ?? 0 : 0;
    final minute = timeParts.length > 1 ? int.tryParse(timeParts[1]) ?? 0 : 0;

    return DateTime(
      appointment.appointmentDate.year,
      appointment.appointmentDate.month,
      appointment.appointmentDate.day,
      hour,
      minute,
    );
  }

  @override
  Widget build(BuildContext context) {
    final upcomingAppointments = _upcomingAppointments();
    final cancelledAppointments = _cancelledAppointments();
    final allActiveAppointments = _allActiveAppointments();

    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadAppointments,
          color: AppTheme.primaryColor,
          child: ScrollConfiguration(
            behavior: const _NoStretchScrollBehavior(),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 100),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'นัดหมายของฉัน',
                    style: TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 24,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textPrimaryColor,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'จัดการและติดตามนัดหมายของคุณได้ที่นี่',
                    style: TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 13,
                      fontWeight: FontWeight.w400,
                      color: AppTheme.textSecondaryColor,
                    ),
                  ),
                  const SizedBox(height: 18),
                  SizedBox(
                    width: double.infinity,
                    height: 46,
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => const DepartmentSelectionPage(),
                          ),
                        );
                      },
                      icon: const Icon(Icons.add_rounded, size: 20),
                      label: const Text('สร้างนัดหมายใหม่'),
                    ),
                  ),
                  const SizedBox(height: 22),
                  _buildFilterSelector(context),
                  const SizedBox(height: 26),
                  if (_isLoading)
                    const _AppointmentLoading()
                  else if (_errorMessage != null)
                    _AppointmentError(
                      message: _errorMessage!,
                      onRetry: _loadAppointments,
                    )
                  else
                    _buildAppointmentContent(
                      context,
                      upcomingAppointments: upcomingAppointments,
                      cancelledAppointments: cancelledAppointments,
                      allActiveAppointments: allActiveAppointments,
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFilterSelector(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE3E8EF)),
      ),
      child: Row(
        children: [
          _buildFilterButton(
            context,
            label: 'กำลังจะมาถึง',
            filter: _AppointmentFilter.upcoming,
          ),
          _buildFilterButton(
            context,
            label: 'ยกเลิก',
            filter: _AppointmentFilter.cancelled,
          ),
          _buildFilterButton(
            context,
            label: 'ดูทั้งหมด',
            filter: _AppointmentFilter.all,
          ),
        ],
      ),
    );
  }

  Widget _buildFilterButton(
    BuildContext context, {
    required String label,
    required _AppointmentFilter filter,
  }) {
    final isSelected = _selectedFilter == filter;

    return Expanded(
      child: GestureDetector(
        onTap: () {
          if (_selectedFilter == filter) {
            return;
          }

          setState(() {
            _selectedFilter = filter;
          });
        },
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 160),
          curve: Curves.easeOut,
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 10),
          decoration: BoxDecoration(
            color: isSelected ? AppTheme.primaryColor : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: isSelected ? Colors.white : AppTheme.textSecondaryColor,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAppointmentContent(
    BuildContext context, {
    required List<AppointmentModel> upcomingAppointments,
    required List<AppointmentModel> cancelledAppointments,
    required List<AppointmentModel> allActiveAppointments,
  }) {
    switch (_selectedFilter) {
      case _AppointmentFilter.upcoming:
        return _buildSection(
          context,
          title: 'นัดหมายที่กำลังจะมาถึง',
          appointments: upcomingAppointments,
          emptyChild: const _EmptyAppointment(),
        );

      case _AppointmentFilter.cancelled:
        return _buildSection(
          context,
          title: 'นัดหมายที่ยกเลิก',
          appointments: cancelledAppointments,
          emptyChild: const _EmptyCancelledAppointment(),
        );

      case _AppointmentFilter.all:
        return _buildSection(
          context,
          title: 'นัดหมายทั้งหมด',
          appointments: allActiveAppointments,
          emptyChild: const _EmptyAppointment(),
        );
    }
  }

  Widget _buildSection(
    BuildContext context, {
    required String title,
    required List<AppointmentModel> appointments,
    required Widget emptyChild,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontFamily: 'Kanit',
            fontSize: 17,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        const SizedBox(height: 12),
        if (appointments.isEmpty)
          emptyChild
        else
          ...appointments.map((appointment) {
            final doctor = _doctorFor(appointment);

            if (doctor == null) {
              return const SizedBox.shrink();
            }

            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: _AppointmentCard(
                appointment: appointment,
                doctor: doctor,
                onOpenDetails: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => AppointmentDetailsPage(
                        doctor: doctor,
                        appointment: appointment,
                      ),
                    ),
                  );
                },
              ),
            );
          }),
      ],
    );
  }
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

class _AppointmentCard extends StatelessWidget {
  final AppointmentModel appointment;
  final DoctorModel doctor;
  final VoidCallback? onOpenDetails;

  const _AppointmentCard({
    required this.appointment,
    required this.doctor,
    this.onOpenDetails,
  });

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

  String _doctorName() {
    final title = doctor.preface == DoctorPreface.mrDoctor
        ? 'นายแพทย์'
        : 'แพทย์หญิง';

    return '$title ${doctor.firstName} ${doctor.lastName}';
  }

  String _specialization() {
    if (doctor.specializations.isEmpty) {
      return 'แพทย์ผู้เชี่ยวชาญ';
    }

    return doctor.specializations.first.name;
  }

  String _statusText() {
    switch (appointment.status) {
      case AppointmentStatus.confirmed:
        return 'ยืนยันแล้ว';

      case AppointmentStatus.checkedIn:
        return 'เช็คอินแล้ว';

      case AppointmentStatus.inProgress:
        return 'กำลังตรวจ';

      case AppointmentStatus.cancelled:
        return 'ยกเลิกแล้ว';

      case AppointmentStatus.completed:
        return 'เสร็จสิ้น';

      case AppointmentStatus.noShow:
        return 'ไม่มาตามนัด';
    }
  }

  Color _statusColor() {
    switch (appointment.status) {
      case AppointmentStatus.cancelled:
      case AppointmentStatus.noShow:
        return AppTheme.errorColor;

      case AppointmentStatus.confirmed:
        return AppTheme.successColor;

      case AppointmentStatus.checkedIn:
        return AppTheme.checkInColor;

      case AppointmentStatus.inProgress:
      case AppointmentStatus.completed:
        return AppTheme.primaryColor;
    }
  }

  String _formatDate(DateTime date) {
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

    return '${date.day} ${months[date.month - 1]} ${date.year + 543}';
  }

  @override
  Widget build(BuildContext context) {
    final statusColor = _statusColor();
    final imageUrl = _resolveDoctorImageUrl(doctor.profileImageUrl);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: AppTheme.textSecondaryColor.withValues(alpha: 0.12),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Container(
                width: 52,
                height: 52,
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
                        size: 28,
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
                            size: 28,
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
                      _specialization(),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'Kanit',
                        fontSize: 12,
                        fontWeight: FontWeight.w400,
                        color: AppTheme.textSecondaryColor,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.10),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  _statusText(),
                  style: TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 10,
                    fontWeight: FontWeight.w500,
                    color: statusColor,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          const Divider(height: 1),
          const SizedBox(height: 14),
          _AppointmentInfoRow(
            icon: Icons.calendar_today_rounded,
            text: _formatDate(appointment.appointmentDate),
          ),
          const SizedBox(height: 12),
          _AppointmentInfoRow(
            icon: Icons.access_time_rounded,
            text: '${appointment.startTime} - ${appointment.endTime}',
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 42,
            child: OutlinedButton(
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(double.infinity, 44),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                side: BorderSide(
                  color: AppTheme.primaryColor.withValues(alpha: 0.55),
                ),
              ),
              onPressed: onOpenDetails,
              child: const Text(
                'ดูรายละเอียดนัดหมาย',
                style: TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _AppointmentInfoRow extends StatelessWidget {
  final IconData icon;
  final String text;

  const _AppointmentInfoRow({required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: 22,
          child: Icon(icon, size: 18, color: AppTheme.primaryColor),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              fontFamily: 'Kanit',
              fontSize: 13,
              fontWeight: FontWeight.w400,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ),
      ],
    );
  }
}

class _EmptyCancelledAppointment extends StatelessWidget {
  const _EmptyCancelledAppointment();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 38, horizontal: 20),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8ECF2)),
      ),
      child: const Column(
        children: [
          Icon(
            Icons.event_busy_outlined,
            size: 42,
            color: AppTheme.textSecondaryColor,
          ),
          SizedBox(height: 12),
          Text(
            'ไม่มีนัดหมายที่ยกเลิกหรือไม่มาตามนัด',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 5),
          Text(
            'ยังไม่มีรายการนัดหมายในหมวดนี้',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 12,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ],
      ),
    );
  }
}

class _AppointmentLoading extends StatelessWidget {
  const _AppointmentLoading();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 48),
      child: const Column(
        children: [
          SizedBox(
            width: 28,
            height: 28,
            child: CircularProgressIndicator(
              strokeWidth: 2.5,
              color: AppTheme.primaryColor,
            ),
          ),
          SizedBox(height: 14),
          Text(
            'กำลังโหลดนัดหมาย...',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 13,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ],
      ),
    );
  }
}

class _AppointmentError extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _AppointmentError({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.errorColor.withValues(alpha: 0.20)),
      ),
      child: Column(
        children: [
          const Icon(
            Icons.error_outline_rounded,
            color: AppTheme.errorColor,
            size: 34,
          ),
          const SizedBox(height: 10),
          Text(
            message,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontFamily: 'Kanit',
              fontSize: 12,
              color: AppTheme.textSecondaryColor,
            ),
          ),
          const SizedBox(height: 12),
          OutlinedButton(
            onPressed: onRetry,
            child: const Text(
              'ลองใหม่',
              style: TextStyle(fontFamily: 'Kanit'),
            ),
          ),
        ],
      ),
    );
  }
}

class _EmptyAppointment extends StatelessWidget {
  const _EmptyAppointment();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 48, horizontal: 20),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8ECF2)),
      ),
      child: const Column(
        children: [
          Icon(
            Icons.event_available_outlined,
            size: 42,
            color: AppTheme.primaryColor,
          ),
          SizedBox(height: 12),
          Text(
            'ยังไม่มีนัดหมาย',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 5),
          Text(
            'สร้างนัดหมายใหม่เพื่อเริ่มต้น',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 12,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ],
      ),
    );
  }
}