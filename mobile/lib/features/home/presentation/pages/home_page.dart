import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/storage/token_storage.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/widgets/app_shell.dart';
import '../../../appointment/data/models/appointment_model.dart';
import '../../../appointment/data/repositories/appointment_repository.dart';
import '../../../appointment/data/services/appointment_api_service.dart';
import '../../../appointment/presentation/pages/appointment_details_page.dart';
import '../../../notification/data/repositories/notification_repository.dart';
import '../../../notification/data/services/notification_api_service.dart';
import '../../../notification/presentation/pages/notification_page.dart';
import '../../../profile/data/repositories/profile_repository.dart';
import '../../../profile/data/services/profile_api_service.dart';
import '../../../search/data/models/doctor_model.dart';
import '../../../search/data/repositories/doctor_repository.dart';
import '../../../search/data/services/doctor_api_service.dart';
import '../../../search/presentation/pages/search_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late final AppointmentRepository _appointmentRepository;
  late final DoctorRepository _doctorRepository;
  late final ProfileRepository _profileRepository;
  late final NotificationRepository _notificationRepository;
  late final TokenStorage _tokenStorage;

  String _firstName = 'คุณ';
  AppointmentModel? _upcomingAppointment;
  DoctorModel? _upcomingDoctor;

  bool _isLoadingAppointment = true;
  bool _isLoadingProfile = true;

  String? _appointmentErrorMessage;

  bool _isSearchPressed = false;
  bool _hasUnreadNotifications = false;

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

    _profileRepository = ProfileRepository(
      profileApiService: ProfileApiService(apiClient: apiClient),
    );

    _notificationRepository = NotificationRepository(
      apiService: NotificationApiService(apiClient: apiClient),
    );

    _tokenStorage = TokenStorage();

    _loadHomeData();
  }

  Future<void> _loadHomeData() async {
    await Future.wait([
      _loadProfile(),
      _loadUpcomingAppointment(),
      _loadNotifications(),
    ]);
  }

  Future<void> _loadNotifications() async {
    try {
      final patientId = await _getPatientIdFromToken();

      if (patientId == null) {
        return;
      }

      final notifications = await _notificationRepository
          .getPatientNotifications(patientId: patientId);

      if (!mounted) {
        return;
      }

      setState(() {
        _hasUnreadNotifications = notifications.any(
          (notification) => !notification.isRead,
        );
      });
    } on DioException {
      // Keep the last known unread state if notification loading fails.
    } catch (_) {
      // Keep the last known unread state if notification loading fails.
    }
  }

  Future<void> _loadProfile() async {
    try {
      final profile = await _profileRepository.getProfile();

      if (!mounted) {
        return;
      }

      setState(() {
        _firstName = profile.firstName;
        _isLoadingProfile = false;
      });
    } on DioException {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoadingProfile = false;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoadingProfile = false;
      });
    }
  }

  Future<void> _loadUpcomingAppointment() async {
    if (!mounted) {
      return;
    }

    setState(() {
      _isLoadingAppointment = true;
      _appointmentErrorMessage = null;
    });

    try {
      final patientId = await _getPatientIdFromToken();

      if (patientId == null) {
        throw Exception('ไม่พบข้อมูลผู้ป่วยจากบัญชีที่เข้าสู่ระบบ');
      }

      final appointments = await _appointmentRepository.getPatientAppointments(
        patientId: patientId,
      );

      final upcomingAppointments = appointments
          .where(_isUpcomingAppointment)
          .toList();

      upcomingAppointments.sort((a, b) {
        final aDateTime = _appointmentDateTime(a);
        final bDateTime = _appointmentDateTime(b);

        return aDateTime.compareTo(bDateTime);
      });

      if (!mounted) {
        return;
      }

      if (upcomingAppointments.isEmpty) {
        setState(() {
          _upcomingAppointment = null;
          _upcomingDoctor = null;
          _isLoadingAppointment = false;
        });

        return;
      }

      final upcoming = upcomingAppointments.first;

      final doctor = await _doctorRepository.getDoctorById(
        doctorId: upcoming.doctorId,
      );
    
      if (!mounted) {
        return;
      }

      setState(() {
        _upcomingAppointment = upcoming;
        _upcomingDoctor = doctor;
        _isLoadingAppointment = false;
      });
    } on DioException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoadingAppointment = false;
        _appointmentErrorMessage = _getDioErrorMessage(error);
      });
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoadingAppointment = false;
        _appointmentErrorMessage = error.toString().replaceFirst(
          'Exception: ',
          '',
        );
      });
    }
  }

  bool _isUpcomingAppointment(AppointmentModel appointment) {
    if (appointment.status == AppointmentStatus.cancelled ||
        appointment.status == AppointmentStatus.completed ||
        appointment.status == AppointmentStatus.noShow) {
      return false;
    }

    final appointmentDateTime = _appointmentDateTime(appointment);

    return appointmentDateTime.isAfter(DateTime.now());
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

    return 'ไม่สามารถโหลดข้อมูลนัดหมายได้ กรุณาลองใหม่';
  }

  Future<void> _refreshHome() async {
    await _loadHomeData();
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
    return ColoredBox(
      color: const Color(0xFFF8F9FA),
      child: SafeArea(
        child: RefreshIndicator(
          onRefresh: _refreshHome,
          color: AppTheme.primaryColor,
          child: ScrollConfiguration(
            behavior: const _NoStretchScrollBehavior(),
            child: CustomScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              slivers: [
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(20, 18, 20, 28),
                  sliver: SliverList(
                    delegate: SliverChildListDelegate([
                      _buildHeader(context),
                      const SizedBox(height: 28),
                      _buildGreeting(context),
                      const SizedBox(height: 22),
                      _buildSearchBar(context),
                      const SizedBox(height: 14),
                      _buildSearchSuggestions(context),
                      const SizedBox(height: 34),
                      _buildUpcomingAppointment(context),
                      const SizedBox(height: 28),
                      _buildHealthTip(context),
                      const SizedBox(height: 100),
                    ]),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: Image.asset(
                'assets/images/logo/LOGO.png',
                width: 60,
                height: 60,
                fit: BoxFit.contain,
              ),
            ),
            const SizedBox(width: 4),
            Text(
              'CareFlow',
              style: theme.textTheme.titleLarge?.copyWith(
                fontSize: 24,
                fontWeight: FontWeight.w800,
                color: AppTheme.primaryDarkColor,
              ),
            ),
          ],
        ),
        Material(
          color: AppTheme.surfaceColor,
          shape: const CircleBorder(),
          child: InkWell(
            customBorder: const CircleBorder(),
            onTap: () async {
              await Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const NotificationPage()),
              );

              if (!mounted) {
                return;
              }

              await _loadNotifications();
            },
            child: SizedBox(
              width: 52,
              height: 52,
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  const Center(
                    child: Icon(
                      Icons.notifications_rounded,
                      size: 30,
                      color: AppTheme.textPrimaryColor,
                    ),
                  ),
                  if (_hasUnreadNotifications)
                    Positioned(
                      top: 7,
                      right: 7,
                      child: Container(
                        width: 9,
                        height: 9,
                        decoration: BoxDecoration(
                          color: AppTheme.errorColor,
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: AppTheme.surfaceColor,
                            width: 1.5,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildGreeting(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'อรุณสวัสดิ์',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: AppTheme.textSecondaryColor,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          _isLoadingProfile ? 'สวัสดี 👋' : 'สวัสดี $_firstName 👋',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontSize: 26,
            fontWeight: FontWeight.w700,
            color: AppTheme.textPrimaryColor,
          ),
        ),
      ],
    );
  }

  Widget _buildSearchBar(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) {
        setState(() {
          _isSearchPressed = true;
        });
      },
      onTapUp: (_) {
        setState(() {
          _isSearchPressed = false;
        });

        Navigator.of(context).push(
          MaterialPageRoute(builder: (_) => const SearchPage(initialQuery: '')),
        );
      },
      onTapCancel: () {
        setState(() {
          _isSearchPressed = false;
        });
      },
      child: AnimatedScale(
        scale: _isSearchPressed ? 0.98 : 1.0,
        duration: const Duration(milliseconds: 100),
        curve: Curves.easeOut,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 100),
          curve: Curves.easeOut,
          height: 56,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: _isSearchPressed
                ? AppTheme.primaryBackgroundColor
                : AppTheme.surfaceColor,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: _isSearchPressed
                  ? AppTheme.primaryColor
                  : const Color(0xFFE3E8EF),
              width: _isSearchPressed ? 1.5 : 1,
            ),
            boxShadow: _isSearchPressed
                ? [
                    BoxShadow(
                      color: AppTheme.primaryColor.withValues(alpha: 0.10),
                      blurRadius: 10,
                      offset: const Offset(0, 3),
                    ),
                  ]
                : null,
          ),
          child: Row(
            children: [
              Icon(
                Icons.search_rounded,
                size: 22,
                color: _isSearchPressed
                    ? AppTheme.primaryColor
                    : AppTheme.textSecondaryColor,
              ),
              const SizedBox(width: 11),
              Expanded(
                child: Text(
                  'ค้นหาอาการ หรือแพทย์',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: _isSearchPressed
                        ? AppTheme.primaryDarkColor
                        : AppTheme.textMutedColor,
                    fontSize: 14,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSearchSuggestions(BuildContext context) {
    return SizedBox(
      height: 42,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.only(right: 4),
        children: [
          _buildSuggestionChip(
            context,
            label: 'ปวดหัว',
            icon: Icons.sentiment_dissatisfied_outlined,
          ),
          const SizedBox(width: 10),
          _buildSuggestionChip(
            context,
            label: 'ปวดท้อง',
            icon: Icons.sick_outlined,
          ),
          const SizedBox(width: 10),
          _buildSuggestionChip(
            context,
            label: 'ไอ เจ็บคอ',
            icon: Icons.sick_outlined,
          ),
          const SizedBox(width: 10),
          _buildSuggestionChip(
            context,
            label: 'ไข้',
            icon: Icons.thermostat_outlined,
          ),
        ],
      ),
    );
  }

  Widget _buildSuggestionChip(
    BuildContext context, {
    required String label,
    required IconData icon,
  }) {
    final theme = Theme.of(context);

    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        splashColor: AppTheme.primaryColor.withValues(alpha: 0.12),
        highlightColor: AppTheme.primaryBackgroundColor.withValues(alpha: 0.65),
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => SearchPage(initialQuery: label)),
          );
        },
        child: Ink(
          padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 8),
          decoration: BoxDecoration(
            color: AppTheme.primaryBackgroundColor,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFFDCE8F8)),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primaryColor.withValues(alpha: 0.06),
                blurRadius: 6,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 16, color: AppTheme.primaryColor),
              const SizedBox(width: 7),
              Text(
                label,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontSize: 12,
                  color: AppTheme.primaryDarkColor,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildUpcomingAppointment(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                'นัดหมายที่กำลังจะมาถึง',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
            ),
            TextButton(
              onPressed: () {
                context
                    .findAncestorStateOfType<AppShellState>()
                    ?.goToAppointments();
              },
              style: TextButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                minimumSize: Size.zero,
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'ดูทั้งหมด',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: AppTheme.primaryColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(width: 2),
                  const Icon(
                    Icons.chevron_right_rounded,
                    size: 18,
                    color: AppTheme.primaryColor,
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (_isLoadingAppointment)
          const _AppointmentLoading()
        else if (_appointmentErrorMessage != null)
          _AppointmentError(
            message: _appointmentErrorMessage!,
            onRetry: _loadUpcomingAppointment,
          )
        else if (_upcomingAppointment == null || _upcomingDoctor == null)
          const _EmptyUpcomingAppointment()
        else
          _buildUpcomingAppointmentCard(
            context,
            _upcomingAppointment!,
            _upcomingDoctor!,
          ),
      ],
    );
  }

  Widget _buildUpcomingAppointmentCard(
    BuildContext context,
    AppointmentModel appointment,
    DoctorModel doctor,
  ) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE8ECF2)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.055),
            blurRadius: 18,
            offset: const Offset(0, 7),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildDoctorHeader(context, doctor, appointment),
          const SizedBox(height: 18),
          const Divider(height: 1, thickness: 1, color: Color(0xFFE9EDF2)),
          const SizedBox(height: 18),
          _buildAppointmentDateTime(context, appointment),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => AppointmentDetailsPage(
                      doctor: doctor,
                      appointment: appointment,
                    ),
                  ),
                );
              },
              child: const Text('ดูรายละเอียดนัดหมาย'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDoctorHeader(
    BuildContext context,
    DoctorModel doctor,
    AppointmentModel appointment,
  ) {
    final theme = Theme.of(context);

    final title = doctor.preface == DoctorPreface.mrDoctor
        ? 'นายแพทย์'
        : 'แพทย์หญิง';

    final doctorName = '$title ${doctor.firstName} ${doctor.lastName}';

    final specialization = doctor.specializations.isEmpty
        ? 'แพทย์ผู้เชี่ยวชาญ'
        : doctor.specializations.first.name;

    final statusColor = _statusColor(appointment.status);
    final imageUrl = _resolveDoctorImageUrl(doctor.profileImageUrl);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
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
                  size: 27,
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
                      size: 27,
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
                doctorName,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              const SizedBox(height: 3),
              Text(
                specialization,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: AppTheme.textSecondaryColor,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
          decoration: BoxDecoration(
            color: statusColor.withValues(alpha: 0.10),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  color: statusColor,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 5),
              Text(
                _statusText(appointment.status),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: statusColor,
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _statusText(AppointmentStatus status) {
    switch (status) {
      case AppointmentStatus.confirmed:
        return 'ยืนยันแล้ว';
      case AppointmentStatus.checkedIn:
        return 'เช็คอินแล้ว';
      case AppointmentStatus.cancelled:
        return 'ยกเลิกแล้ว';
      case AppointmentStatus.completed:
        return 'เสร็จสิ้น';
      case AppointmentStatus.noShow:
        return 'ไม่มาตามนัด';
      case AppointmentStatus.inProgress:
        return 'กำลังตรวจ';
    }
  }

  Color _statusColor(AppointmentStatus status) {
    switch (status) {
      case AppointmentStatus.cancelled:
      case AppointmentStatus.noShow:
        return AppTheme.errorColor;
      case AppointmentStatus.confirmed:
      case AppointmentStatus.checkedIn:
        return AppTheme.successColor;
      case AppointmentStatus.inProgress:
      case AppointmentStatus.completed:
        return AppTheme.primaryColor;
    }
  }

  Widget _buildAppointmentDateTime(
    BuildContext context,
    AppointmentModel appointment,
  ) {
    final theme = Theme.of(context);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 32,
          child: Center(
            child: Icon(
              Icons.calendar_month_rounded,
              size: 19,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _formatThaiDate(appointment.appointmentDate),
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: AppTheme.textPrimaryColor,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                '${appointment.startTime} – ${appointment.endTime} น.',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: AppTheme.textSecondaryColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
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

    return '${date.day} ${months[date.month - 1]} ${date.year + 543}';
  }

  Widget _buildHealthTip(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.primaryBackgroundColor,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'เคล็ดลับสุขภาพวันนี้',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const SizedBox(height: 7),
                Text(
                  'ดื่มน้ำอย่างน้อย 8 แก้วต่อวัน '
                  'เพื่อช่วยดูแลสุขภาพในแต่ละวัน',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: AppTheme.textSecondaryColor,
                    height: 1.45,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
          Container(
            width: 58,
            height: 58,
            decoration: const BoxDecoration(
              color: AppTheme.primaryColor,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.water_drop_rounded,
              color: Colors.white,
              size: 30,
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

  const _AppointmentError({
    required this.message,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppTheme.errorColor.withValues(alpha: 0.20),
        ),
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

class _EmptyUpcomingAppointment extends StatelessWidget {
  const _EmptyUpcomingAppointment();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
        vertical: 38,
        horizontal: 20,
      ),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE8ECF2)),
      ),
      child: const Column(
        children: [
          Icon(
            Icons.event_available_outlined,
            size: 40,
            color: AppTheme.primaryColor,
          ),
          SizedBox(height: 12),
          Text(
            'ไม่มีนัดหมายที่กำลังจะมาถึง',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 5),
          Text(
            'คุณสามารถสร้างนัดหมายใหม่ได้จากหน้ารายการนัดหมาย',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 11,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ],
      ),
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