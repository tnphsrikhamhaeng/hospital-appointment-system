import 'dart:convert';

import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/storage/token_storage.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../appointment/data/models/appointment_model.dart';
import '../../../appointment/data/models/appointment_slot.dart';
import '../../../appointment/data/repositories/appointment_repository.dart';
import '../../../appointment/data/services/appointment_api_service.dart';
import '../../../appointment/presentation/pages/appointment_confirmation_preview_page.dart';
import '../../data/models/doctor_model.dart';
import '../../data/models/doctor_schedule_model.dart';
import '../../data/repositories/doctor_schedule_repository.dart';
import '../../data/services/doctor_schedule_api_service.dart';
import '../../../appointment/data/models/doctor_schedule_appointment_model.dart';

class DoctorSchedulePage extends StatefulWidget {
  final DoctorModel doctor;
  final bool isEditMode;
  final String? appointmentId;
  final DateTime? initialDate;
  final AppointmentSlot? initialSlot;
  final void Function(DateTime date, AppointmentSlot slot)? onUpdated;

  const DoctorSchedulePage({
    super.key,
    required this.doctor,
    this.isEditMode = false,
    this.appointmentId,
    this.initialDate,
    this.initialSlot,
    this.onUpdated,
  });

  @override
  State<DoctorSchedulePage> createState() => _DoctorSchedulePageState();
}

class _DoctorSchedulePageState extends State<DoctorSchedulePage> {
  late final DoctorScheduleRepository _repository;
  late final AppointmentRepository _appointmentRepository;
  late final TokenStorage _tokenStorage;

  DateTime _selectedDate = DateTime.now();

  List<DateTime> _dates = [];
  List<DoctorScheduleModel> _schedules = [];
  List<AppointmentSlot> _selectedDateSlots = [];
  List<DoctorScheduleAppointmentModel> _appointmentsForSelectedDate = [];
  List<AppointmentModel> _patientAppointments = [];

  AppointmentSlot? _selectedSlot;

  bool _isLoading = true;
  bool _isLoadingAppointments = false;
  bool _isAppointmentValidationReady = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();

    _repository = DoctorScheduleRepository(
      doctorScheduleApiService: DoctorScheduleApiService(
        apiClient: ApiClient(),
      ),
    );

    _appointmentRepository = AppointmentRepository(
      appointmentApiService: AppointmentApiService(apiClient: ApiClient()),
    );

    _tokenStorage = TokenStorage();

    _loadSchedules();
  }

  Future<void> _loadSchedules() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _isAppointmentValidationReady = false;
    });

    try {
      final schedules = await _repository.getSchedulesByDoctor(
        doctorId: widget.doctor.id,
      );

      if (!mounted) {
        return;
      }

      _schedules = schedules.where((schedule) => schedule.isActive).toList();

      _dates = _buildAvailableDates();

      _selectedDate = _getInitialDate();

      _selectedDateSlots = _buildSlotsForDate(_selectedDate);

      if (widget.isEditMode && widget.initialSlot != null) {
        _selectedSlot = _findMatchingSlot(widget.initialSlot!);
      }

      setState(() {
        _isLoading = false;
      });

      await _loadAppointmentsForDate(
        _selectedDate,
        preserveSelectedSlot: widget.isEditMode,
      );
    } catch (_) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
        _errorMessage = 'ไม่สามารถโหลดตารางออกตรวจของแพทย์ได้';
      });
    }
  }

  Future<void> _loadAppointmentsForDate(
    DateTime date, {
    bool preserveSelectedSlot = false,
  }) async {
    if (!preserveSelectedSlot) {
      setState(() {
        _selectedSlot = null;
      });
    }

    setState(() {
      _isLoadingAppointments = true;
      _isAppointmentValidationReady = false;
      _appointmentsForSelectedDate = [];
      _patientAppointments = [];
    });

    try {
      final doctorAppointments = await _appointmentRepository.getDoctorSchedule(
        doctorId: widget.doctor.id,
        appointmentDate: date,
      );

      if (!mounted) {
        return;
      }

      _appointmentsForSelectedDate = doctorAppointments;

      setState(() {
        _selectedDateSlots = _buildSlotsForDate(date);
      });

      final patientId = await _getPatientIdFromToken();

      if (patientId == null) {
        if (!mounted) {
          return;
        }

        setState(() {
          _isLoadingAppointments = false;
          _isAppointmentValidationReady = false;
          _selectedSlot = null;
        });

        return;
      }

      try {
        final patientAppointments = await _appointmentRepository
            .getPatientAppointments(patientId: patientId);

        if (!mounted) {
          return;
        }

        setState(() {
          _patientAppointments = patientAppointments;

          _selectedDateSlots = _buildSlotsForDate(date);

          _isLoadingAppointments = false;
          _isAppointmentValidationReady = true;
        });

        if (preserveSelectedSlot &&
            widget.initialSlot != null &&
            _isSameDate(date, widget.initialSlot!.date)) {
          final matchingSlot = _findMatchingSlot(widget.initialSlot!);

          if (matchingSlot != null &&
              !_isSlotBooked(matchingSlot, date) &&
              _isSlotWithinBookingTime(matchingSlot, date)) {
            setState(() {
              _selectedSlot = matchingSlot;
            });
          } else {
            setState(() {
              _selectedSlot = null;
            });
          }
        }
      } catch (_) {
        if (!mounted) {
          return;
        }

        setState(() {
          _patientAppointments = [];
          _selectedDateSlots = _buildSlotsForDate(date);
          _selectedSlot = null;
          _isLoadingAppointments = false;
          _isAppointmentValidationReady = false;
        });
      }
    } catch (_) {
      if (!mounted) {
        return;
      }

      setState(() {
        _appointmentsForSelectedDate = [];
        _patientAppointments = [];
        _selectedDateSlots = _buildSlotsForDate(date);
        _selectedSlot = null;
        _isLoadingAppointments = false;
        _isAppointmentValidationReady = false;
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
      final normalized = base64Url.normalize(parts[1]);

      final decoded = utf8.decode(base64Url.decode(normalized));

      final payload = jsonDecode(decoded);

      if (payload is! Map) {
        return null;
      }

      final subject = payload['sub'];

      if (subject is String && subject.isNotEmpty) {
        return subject;
      }

      return null;
    } catch (_) {
      return null;
    }
  }

  List<DateTime> _buildAvailableDates() {
    if (_schedules.isEmpty) {
      return [];
    }

    final today = DateTime.now();

    final scheduleWeekdays = _schedules
        .map((schedule) => schedule.weekday)
        .toSet();

    final dates = <DateTime>[];

    for (var index = 0; index < 60; index++) {
      final date = DateTime(today.year, today.month, today.day + index);

      final weekday = _getScheduleWeekday(date);

      if (scheduleWeekdays.contains(weekday)) {
        dates.add(date);
      }

      if (dates.length == 7) {
        break;
      }
    }

    return dates;
  }

  DoctorScheduleWeekday _getScheduleWeekday(DateTime date) {
    switch (date.weekday) {
      case DateTime.monday:
        return DoctorScheduleWeekday.monday;
      case DateTime.tuesday:
        return DoctorScheduleWeekday.tuesday;
      case DateTime.wednesday:
        return DoctorScheduleWeekday.wednesday;
      case DateTime.thursday:
        return DoctorScheduleWeekday.thursday;
      case DateTime.friday:
        return DoctorScheduleWeekday.friday;
      case DateTime.saturday:
        return DoctorScheduleWeekday.saturday;
      case DateTime.sunday:
        return DoctorScheduleWeekday.sunday;
    }

    throw StateError('Invalid weekday');
  }

  List<DoctorScheduleModel> _getSchedulesForDate(DateTime date) {
    final weekday = _getScheduleWeekday(date);

    return _schedules
        .where((schedule) => schedule.weekday == weekday && schedule.isActive)
        .toList();
  }

  List<AppointmentSlot> _buildSlotsForDate(DateTime date) {
    final schedules = _getSchedulesForDate(date);

    final slotDurationMinutes = widget.doctor.department.slotDurationMinutes;

    if (slotDurationMinutes <= 0) {
      return [];
    }

    final slots = <AppointmentSlot>[];

    for (final schedule in schedules) {
      slots.addAll(
        _generateSlots(
          date: date,
          schedule: schedule,
          slotDurationMinutes: slotDurationMinutes,
        ),
      );
    }

    return slots;
  }

  List<AppointmentSlot> _generateSlots({
    required DateTime date,
    required DoctorScheduleModel schedule,
    required int slotDurationMinutes,
  }) {
    final startParts = schedule.startTime.split(':');

    final endParts = schedule.endTime.split(':');

    if (startParts.length < 2 || endParts.length < 2) {
      return [];
    }

    var current = DateTime(
      date.year,
      date.month,
      date.day,
      int.parse(startParts[0]),
      int.parse(startParts[1]),
    );

    final end = DateTime(
      date.year,
      date.month,
      date.day,
      int.parse(endParts[0]),
      int.parse(endParts[1]),
    );

    final slots = <AppointmentSlot>[];

    while (current.add(Duration(minutes: slotDurationMinutes)).isBefore(end) ||
        current
            .add(Duration(minutes: slotDurationMinutes))
            .isAtSameMomentAs(end)) {
      final slotEnd = current.add(Duration(minutes: slotDurationMinutes));

      if (slotEnd.isAfter(end)) {
        break;
      }

      final startTime = _formatTime(current);

      final endTime = _formatTime(slotEnd);

      final slot = (date: date, startTime: startTime, endTime: endTime);

      slots.add(slot);

      current = slotEnd;
    }

    return slots;
  }

  bool _isSlotWithinBookingTime(AppointmentSlot slot, DateTime date) {
    final now = DateTime.now();

    final today = DateTime(now.year, now.month, now.day);

    final selectedDay = DateTime(date.year, date.month, date.day);

    if (selectedDay.isBefore(today)) {
      return false;
    }

    if (selectedDay.isAfter(today)) {
      return true;
    }

    final minimumBookingTime = now.add(const Duration(hours: 1));

    final startParts = slot.startTime.split(':');

    if (startParts.length < 2) {
      return false;
    }

    final slotStart = DateTime(
      date.year,
      date.month,
      date.day,
      int.parse(startParts[0]),
      int.parse(startParts[1]),
    );

    return !slotStart.isBefore(minimumBookingTime);
  }

  bool _isSlotBooked(AppointmentSlot slot, DateTime date) {
    final slotStart = _timeToMinutes(slot.startTime);

    final slotEnd = _timeToMinutes(slot.endTime);

    bool overlapsDoctorScheduleAppointment(
      DoctorScheduleAppointmentModel appointment,
    ) {
      if (appointment.status == AppointmentStatus.cancelled) {
        return false;
      }

      if (widget.isEditMode &&
          widget.appointmentId != null &&
          appointment.id == widget.appointmentId) {
        return false;
      }

      final appointmentStart = _timeToMinutes(appointment.startTime);

      final appointmentEnd = _timeToMinutes(appointment.endTime);

      return appointmentStart < slotEnd && appointmentEnd > slotStart;
    }

    bool overlapsPatientAppointment(AppointmentModel appointment) {
      if (appointment.status == AppointmentStatus.cancelled) {
        return false;
      }

      if (widget.isEditMode &&
          widget.appointmentId != null &&
          appointment.id == widget.appointmentId) {
        return false;
      }

      final appointmentStart = _timeToMinutes(appointment.startTime);

      final appointmentEnd = _timeToMinutes(appointment.endTime);

      return appointmentStart < slotEnd && appointmentEnd > slotStart;
    }

    for (final appointment in _appointmentsForSelectedDate) {
      if (overlapsDoctorScheduleAppointment(appointment)) {
        return true;
      }
    }

    for (final appointment in _patientAppointments) {
      if (!_isSameDate(appointment.appointmentDate, date)) {
        continue;
      }

      if (overlapsPatientAppointment(appointment)) {
        return true;
      }
    }

    return false;
  }

  int _timeToMinutes(String value) {
    final parts = value.split(':');

    if (parts.length < 2) {
      return 0;
    }

    return int.parse(parts[0]) * 60 + int.parse(parts[1]);
  }

  String _formatTime(DateTime value) {
    final hour = value.hour.toString().padLeft(2, '0');

    final minute = value.minute.toString().padLeft(2, '0');

    return '$hour:$minute';
  }

  DateTime _getInitialDate() {
    if (widget.isEditMode && widget.initialDate != null) {
      for (final date in _dates) {
        if (_isSameDate(date, widget.initialDate!)) {
          return date;
        }
      }
    }

    if (_dates.isNotEmpty) {
      return _dates.first;
    }

    return DateTime.now();
  }

  AppointmentSlot? _findMatchingSlot(AppointmentSlot initialSlot) {
    for (final slot in _selectedDateSlots) {
      if (slot.startTime == initialSlot.startTime &&
          slot.endTime == initialSlot.endTime) {
        return slot;
      }
    }

    return null;
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

  Widget _buildDoctorAvatar() {
    final imageUrl = _resolveDoctorImageUrl(widget.doctor.profileImageUrl);

    if (imageUrl == null) {
      return _buildDoctorPlaceholder();
    }

    return ClipOval(
      child: Image.network(
        imageUrl,
        width: 48,
        height: 48,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) {
          return _buildDoctorPlaceholder();
        },
      ),
    );
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
          widget.isEditMode ? 'แก้ไขนัดหมาย' : 'จองนัดหมาย',
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
      body: SafeArea(child: _buildBody(context)),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_errorMessage != null) {
      return _buildErrorState(context);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildDoctorHeader(context),
          const SizedBox(height: 22),
          _buildDateSection(context),
          const SizedBox(height: 22),
          _buildTimeSlotSection(context),
          const SizedBox(height: 28),
          _buildAppointmentSummary(context),
          const SizedBox(height: 20),
          _buildConfirmButton(context),
        ],
      ),
    );
  }

  Widget _buildDoctorHeader(BuildContext context) {
    final doctorName =
        '${widget.doctor.preface == DoctorPreface.mrDoctor ? 'นายแพทย์' : 'แพทย์หญิง'} '
        '${widget.doctor.firstName} ${widget.doctor.lastName}';

    final specialization = widget.doctor.specializations.isNotEmpty
        ? widget.doctor.specializations.first.name
        : 'แพทย์ผู้เชี่ยวชาญ';

    return Row(
      children: [
        _buildDoctorAvatar(),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                doctorName,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                specialization,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 13,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDateSection(BuildContext context) {
    final theme = Theme.of(context);

    if (_dates.isEmpty) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.surfaceColor,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE8ECF2)),
        ),
        child: Text(
          'ไม่พบตารางออกตรวจของแพทย์',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: AppTheme.textSecondaryColor,
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'เลือกวันที่',
          style: theme.textTheme.titleMedium?.copyWith(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 90,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: _dates.length,
            separatorBuilder: (_, index) => const SizedBox(width: 10),
            itemBuilder: (context, index) {
              return _buildDateItem(context, date: _dates[index]);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTimeSlotSection(BuildContext context) {
    final theme = Theme.of(context);

    final morningSlots = _selectedDateSlots
        .where((slot) => int.parse(slot.startTime.split(':').first) < 12)
        .toList();

    final afternoonSlots = _selectedDateSlots
        .where((slot) => int.parse(slot.startTime.split(':').first) >= 12)
        .toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'เวลาที่ว่าง',
              style: theme.textTheme.titleMedium?.copyWith(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimaryColor,
              ),
            ),
            if (_isLoadingAppointments) ...[
              const SizedBox(width: 10),
              const SizedBox(
                width: 14,
                height: 14,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ],
          ],
        ),
        const SizedBox(height: 10),
        if (morningSlots.isNotEmpty) ...[
          Text(
            'ช่วงเช้า',
            style: theme.textTheme.bodyMedium?.copyWith(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: AppTheme.textSecondaryColor,
            ),
          ),
          const SizedBox(height: 8),
          _buildSlotGrid(context, morningSlots),
        ],
        if (morningSlots.isNotEmpty && afternoonSlots.isNotEmpty)
          const SizedBox(height: 16),
        if (afternoonSlots.isNotEmpty) ...[
          Text(
            'ช่วงบ่าย',
            style: theme.textTheme.bodyMedium?.copyWith(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: AppTheme.textSecondaryColor,
            ),
          ),
          const SizedBox(height: 8),
          _buildSlotGrid(context, afternoonSlots),
        ],
        if (morningSlots.isEmpty && afternoonSlots.isEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              'ไม่มีช่วงเวลาออกตรวจในวันนี้',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: AppTheme.textMutedColor,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildSlotGrid(BuildContext context, List<AppointmentSlot> slots) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: slots.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
        childAspectRatio: 2.7,
      ),
      itemBuilder: (context, index) {
        return _buildSlotItem(context, slot: slots[index]);
      },
    );
  }

  Widget _buildSlotItem(BuildContext context, {required AppointmentSlot slot}) {
    final theme = Theme.of(context);

    final isSelected = _selectedSlot == slot;

    final isBooked = _isSlotBooked(slot, _selectedDate);

    final isWithinBookingTime = _isSlotWithinBookingTime(slot, _selectedDate);

    final isDisabled =
        isBooked || !isWithinBookingTime || !_isAppointmentValidationReady;

    return GestureDetector(
      onTap: isDisabled
          ? null
          : () {
              setState(() {
                _selectedSlot = slot;
              });
            },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: isSelected
              ? AppTheme.primaryColor
              : isDisabled
              ? const Color(0xFFF1F3F6)
              : AppTheme.surfaceColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected
                ? AppTheme.primaryColor
                : isDisabled
                ? const Color(0xFFD9DEE6)
                : const Color(0xFFE8ECF2),
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: AppTheme.primaryColor.withValues(alpha: 0.12),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ]
              : null,
        ),
        child: Text(
          slot.startTime,
          style: theme.textTheme.bodySmall?.copyWith(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: isSelected
                ? Colors.white
                : isDisabled
                ? AppTheme.textMutedColor
                : AppTheme.textPrimaryColor,
          ),
        ),
      ),
    );
  }

  Widget _buildDateItem(BuildContext context, {required DateTime date}) {
    final theme = Theme.of(context);

    final isSelected = _isSameDate(date, _selectedDate);

    return GestureDetector(
      onTap: () async {
        setState(() {
          _selectedDate = date;
          _selectedDateSlots = _buildSlotsForDate(date);
          _selectedSlot = null;
          _appointmentsForSelectedDate = [];
          _patientAppointments = [];
          _isAppointmentValidationReady = false;
        });

        await _loadAppointmentsForDate(date);
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        width: 64,
        padding: const EdgeInsets.symmetric(vertical: 9),
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.primaryColor : AppTheme.surfaceColor,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: isSelected ? AppTheme.primaryColor : const Color(0xFFE8ECF2),
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              _getThaiWeekday(date),
              style: theme.textTheme.bodySmall?.copyWith(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: isSelected ? Colors.white : AppTheme.textSecondaryColor,
              ),
            ),
            const SizedBox(height: 3),
            Text(
              '${date.day}',
              style: theme.textTheme.titleMedium?.copyWith(
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: isSelected ? Colors.white : AppTheme.textPrimaryColor,
              ),
            ),
            const SizedBox(height: 1),
            Text(
              _getThaiMonth(date),
              style: theme.textTheme.bodySmall?.copyWith(
                fontSize: 10,
                color: isSelected ? Colors.white : AppTheme.textMutedColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppointmentSummary(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8ECF2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'สรุปการนัดหมาย',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          const SizedBox(height: 14),
          _buildSummaryRow(
            context,
            icon: Icons.calendar_today_rounded,
            label: 'วันที่',
            value: _formatThaiDate(_selectedDate),
          ),
          const SizedBox(height: 12),
          _buildSummaryRow(
            context,
            icon: Icons.access_time_rounded,
            label: 'เวลา',
            value: _selectedSlot == null
                ? 'ยังไม่ได้เลือกเวลา'
                : '${_selectedSlot!.startTime} น.',
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
  }) {
    final theme = Theme.of(context);

    return Row(
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: AppTheme.primaryBackgroundColor,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, size: 18, color: AppTheme.primaryColor),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontSize: 12,
                  color: AppTheme.textMutedColor,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
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
    );
  }

  Widget _buildConfirmButton(BuildContext context) {
    final isEnabled =
        _selectedSlot != null &&
        !_isLoadingAppointments &&
        _isAppointmentValidationReady;

    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton(
        onPressed: !isEnabled
            ? null
            : () async {
                final selectedSlot = _selectedSlot;

                if (selectedSlot == null) {
                  return;
                }

                final updatedAppointment = await Navigator.of(context)
                    .push<AppointmentModel>(
                      MaterialPageRoute(
                        builder: (_) => AppointmentConfirmationPreviewPage(
                          doctor: widget.doctor,
                          selectedDate: _selectedDate,
                          selectedSlot: selectedSlot,
                          isEditMode: widget.isEditMode,
                          appointmentId: widget.appointmentId,
                        ),
                      ),
                    );

                if (!context.mounted || updatedAppointment == null) {
                  return;
                }

                Navigator.of(context).pop(updatedAppointment);
              },
        style: ElevatedButton.styleFrom(
          elevation: 0,
          backgroundColor: AppTheme.primaryColor,
          disabledBackgroundColor: const Color(0xFFE5E9EF),
          foregroundColor: Colors.white,
          disabledForegroundColor: AppTheme.textMutedColor,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              widget.isEditMode ? 'ยืนยันการแก้ไข' : 'ยืนยันเวลานัดหมาย',
              style: const TextStyle(
                fontFamily: 'Kanit',
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 8),
            const Icon(
              Icons.arrow_forward_rounded,
              size: 19,
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
        padding: const EdgeInsets.symmetric(horizontal: 24),
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
              _errorMessage ?? 'ไม่สามารถโหลดข้อมูลได้',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimaryColor,
              ),
            ),
            const SizedBox(height: 14),
            OutlinedButton(
              onPressed: _loadSchedules,
              child: const Text('ลองใหม่'),
            ),
          ],
        ),
      ),
    );
  }

  String _getThaiWeekday(DateTime date) {
    const weekdays = ['จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.', 'อา.'];

    return weekdays[date.weekday - 1];
  }

  String _getThaiMonth(DateTime date) {
    const months = [
      'ม.ค.',
      'ก.พ.',
      'มี.ค.',
      'เม.ย.',
      'พ.ค.',
      'มิ.ย.',
      'ก.ค.',
      'ส.ค.',
      'ก.ย.',
      'ต.ค.',
      'พ.ย.',
      'ธ.ค.',
    ];

    return months[date.month - 1];
  }

  bool _isSameDate(DateTime first, DateTime second) {
    return first.year == second.year &&
        first.month == second.month &&
        first.day == second.day;
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

    return '${date.day} '
        '${months[date.month - 1]} '
        '${date.year + 543}';
  }
}
