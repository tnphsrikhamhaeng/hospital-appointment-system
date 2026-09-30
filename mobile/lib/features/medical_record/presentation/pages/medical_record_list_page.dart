import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../appointment/data/models/appointment_model.dart';
import '../../../search/data/models/department_model.dart';
import '../../data/models/medical_record_model.dart';
import '../../../appointment/data/repositories/appointment_repository.dart';
import '../../../search/data/repositories/department_repository.dart';
import '../../data/repositories/medical_record_repository.dart';
import '../../../appointment/data/services/appointment_api_service.dart';
import '../../../search/data/services/department_api_service.dart';
import '../../data/services/medical_record_api_service.dart';
import 'medical_record_details_page.dart';

class _NoStretchScrollBehavior extends ScrollBehavior {
  const _NoStretchScrollBehavior();

  @override
  ScrollPhysics getScrollPhysics(BuildContext context) {
    return const ClampingScrollPhysics();
  }
}

class MedicalRecordListPage extends StatefulWidget {
  const MedicalRecordListPage({super.key});

  @override
  State<MedicalRecordListPage> createState() => _MedicalRecordListPageState();
}

class _MedicalRecordListPageState extends State<MedicalRecordListPage> {
  late final MedicalRecordRepository _medicalRecordRepository;
  late final AppointmentRepository _appointmentRepository;
  late final DepartmentRepository _departmentRepository;

  DateTime? _selectedDate;
  String? _selectedDepartmentId;

  List<MedicalRecordModel> _records = [];
  List<AppointmentModel> _appointments = [];
  List<DepartmentModel> _departments = [];

  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();

    final apiClient = ApiClient();

    _medicalRecordRepository = MedicalRecordRepository(
      medicalRecordApiService: MedicalRecordApiService(apiClient: apiClient),
    );

    _appointmentRepository = AppointmentRepository(
      appointmentApiService: AppointmentApiService(apiClient: apiClient),
    );

    _departmentRepository = DepartmentRepository(
      departmentApiService: DepartmentApiService(apiClient: apiClient),
    );

    _loadMedicalRecords();
  }

  Future<void> _loadMedicalRecords() async {
    if (!mounted) {
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final records = await _medicalRecordRepository.getMedicalRecords();

      final patientIds = records
          .map((record) => record.patientId)
          .where((id) => id.isNotEmpty)
          .toSet();

      final appointmentResults = await Future.wait(
        patientIds.map(
          (patientId) => _appointmentRepository.getPatientAppointments(
            patientId: patientId,
          ),
        ),
      );

      final appointments = appointmentResults.expand((items) => items).toList();

      final departments = await _departmentRepository.getDepartments();

      if (!mounted) {
        return;
      }

      setState(() {
        _records = records;
        _appointments = appointments;
        _departments = departments;
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

    return 'ไม่สามารถโหลดประวัติการรักษาได้ กรุณาลองใหม่';
  }

  AppointmentModel? _getAppointment(MedicalRecordModel record) {
    for (final appointment in _appointments) {
      if (appointment.id == record.appointmentId) {
        return appointment;
      }
    }

    return null;
  }

  DepartmentModel? _getDepartment(MedicalRecordModel record) {
    final appointment = _getAppointment(record);

    if (appointment == null) {
      return null;
    }

    for (final department in _departments) {
      if (department.id == appointment.departmentId) {
        return department;
      }
    }

    return null;
  }

  List<MedicalRecordModel> get _filteredRecords {
    return _records.where((record) {
      final appointment = _getAppointment(record);

      final matchesDate =
          _selectedDate == null ||
          (appointment != null &&
              _isSameDate(appointment.appointmentDate, _selectedDate!));

      final matchesDepartment =
          _selectedDepartmentId == null ||
          (appointment != null &&
              appointment.departmentId == _selectedDepartmentId);

      return matchesDate && matchesDepartment;
    }).toList();
  }

  bool _isSameDate(DateTime first, DateTime second) {
    final firstLocal = first.toLocal();
    final secondLocal = second.toLocal();

    return firstLocal.year == secondLocal.year &&
        firstLocal.month == secondLocal.month &&
        firstLocal.day == secondLocal.day;
  }

  DepartmentModel? get _selectedDepartment {
    if (_selectedDepartmentId == null) {
      return null;
    }

    for (final department in _departments) {
      if (department.id == _selectedDepartmentId) {
        return department;
      }
    }

    return null;
  }

  bool get _hasActiveFilters {
    return _selectedDate != null || _selectedDepartmentId != null;
  }

  void _clearFilters() {
    setState(() {
      _selectedDate = null;
      _selectedDepartmentId = null;
    });
  }

  Future<void> _selectDate() async {
    final now = DateTime.now();

    final pickedDate = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? now,
      firstDate: DateTime(2020),
      lastDate: DateTime(now.year + 1),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppTheme.primaryColor,
              onPrimary: Colors.white,
              surface: AppTheme.surfaceColor,
              onSurface: AppTheme.textPrimaryColor,
            ),
          ),
          child: child!,
        );
      },
    );

    if (pickedDate == null || !mounted) {
      return;
    }

    setState(() {
      _selectedDate = pickedDate;
    });
  }

  Future<void> _selectDepartment() async {
    final selectedId = await showModalBottomSheet<String?>(
      context: context,
      backgroundColor: AppTheme.surfaceColor,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(22)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 14, 20, 20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(
                  child: Container(
                    width: 42,
                    height: 4,
                    decoration: BoxDecoration(
                      color: const Color(0xFFD9DEE7),
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
                const SizedBox(height: 18),
                const Text(
                  'เลือกแผนก',
                  style: TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimaryColor,
                  ),
                ),
                const SizedBox(height: 12),
                ListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 4),
                  leading: Container(
                    width: 42,
                    height: 42,
                    decoration: BoxDecoration(
                      color: AppTheme.primaryBackgroundColor,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.apps_rounded,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                  title: const Text(
                    'ทุกแผนก',
                    style: TextStyle(
                      fontFamily: 'Kanit',
                      fontSize: 14,
                      color: AppTheme.textPrimaryColor,
                    ),
                  ),
                  trailing: _selectedDepartmentId == null
                      ? const Icon(
                          Icons.check_rounded,
                          color: AppTheme.primaryColor,
                        )
                      : null,
                  onTap: () {
                    Navigator.of(context).pop(null);
                  },
                ),
                const Divider(height: 1),
                Flexible(
                  child: ListView.separated(
                    shrinkWrap: true,
                    itemCount: _departments.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (context, index) {
                      final department = _departments[index];

                      final isSelected = department.id == _selectedDepartmentId;

                      return ListTile(
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 4,
                        ),
                        leading: Container(
                          width: 42,
                          height: 42,
                          decoration: BoxDecoration(
                            color: AppTheme.primaryBackgroundColor,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(
                            Icons.medical_services_rounded,
                            color: AppTheme.primaryColor,
                          ),
                        ),
                        title: Text(
                          department.name,
                          style: const TextStyle(
                            fontFamily: 'Kanit',
                            fontSize: 14,
                            color: AppTheme.textPrimaryColor,
                          ),
                        ),
                        trailing: isSelected
                            ? const Icon(
                                Icons.check_rounded,
                                color: AppTheme.primaryColor,
                              )
                            : null,
                        onTap: () {
                          Navigator.of(context).pop(department.id);
                        },
                      );
                    },
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

    setState(() {
      _selectedDepartmentId = selectedId;
    });
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
        centerTitle: true,
        title: const Text(
          'ประวัติการรักษา',
          style: TextStyle(
            fontFamily: 'Kanit',
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1),
          child: Divider(height: 1, thickness: 1, color: Color(0xFFE8ECF2)),
        ),
      ),
      body: SafeArea(
        child: ScrollConfiguration(
          behavior: const _NoStretchScrollBehavior(),
          child: RefreshIndicator(
            onRefresh: _loadMedicalRecords,
            color: AppTheme.primaryColor,
            child: SingleChildScrollView(
              keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 100),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildFilterButtons(),
                  if (_hasActiveFilters) ...[
                    const SizedBox(height: 12),
                    _buildActiveFilters(),
                  ],
                  const SizedBox(height: 20),
                  _buildRecordList(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFilterButtons() {
    return Row(
      children: [
        Expanded(
          child: _buildFilterButton(
            icon: Icons.calendar_month_rounded,
            label: _selectedDate == null
                ? 'เลือกวันที่'
                : _formatFilterDate(_selectedDate!),
            isSelected: _selectedDate != null,
            onTap: _selectDate,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _buildFilterButton(
            icon: Icons.local_hospital_rounded,
            label: _selectedDepartment == null
                ? 'เลือกแผนก'
                : _selectedDepartment!.name,
            isSelected: _selectedDepartment != null,
            onTap: _selectDepartment,
          ),
        ),
      ],
    );
  }

  Widget _buildFilterButton({
    required IconData icon,
    required String label,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(13),
        child: Container(
          height: 46,
          padding: const EdgeInsets.symmetric(horizontal: 12),
          decoration: BoxDecoration(
            color: isSelected
                ? AppTheme.primaryBackgroundColor
                : AppTheme.surfaceColor,
            borderRadius: BorderRadius.circular(13),
            border: Border.all(
              color: isSelected
                  ? AppTheme.primaryColor.withValues(alpha: 0.35)
                  : AppTheme.textSecondaryColor.withValues(alpha: 0.12),
            ),
          ),
          child: Row(
            children: [
              Icon(
                icon,
                size: 19,
                color: isSelected
                    ? AppTheme.primaryColor
                    : AppTheme.textSecondaryColor,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontFamily: 'Kanit',
                    fontSize: 12,
                    fontWeight: isSelected ? FontWeight.w500 : FontWeight.w400,
                    color: isSelected
                        ? AppTheme.primaryColor
                        : AppTheme.textSecondaryColor,
                  ),
                ),
              ),
              Icon(
                Icons.keyboard_arrow_down_rounded,
                size: 20,
                color: isSelected
                    ? AppTheme.primaryColor
                    : AppTheme.textSecondaryColor,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildActiveFilters() {
    return Row(
      children: [
        Expanded(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                if (_selectedDate != null)
                  _buildActiveFilterChip(
                    icon: Icons.calendar_month_rounded,
                    label: _formatFilterDate(_selectedDate!),
                    onRemove: () {
                      setState(() {
                        _selectedDate = null;
                      });
                    },
                  ),
                if (_selectedDate != null && _selectedDepartment != null)
                  const SizedBox(width: 8),
                if (_selectedDepartment != null)
                  _buildActiveFilterChip(
                    icon: Icons.local_hospital_rounded,
                    label: _selectedDepartment!.name,
                    onRemove: () {
                      setState(() {
                        _selectedDepartmentId = null;
                      });
                    },
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 8),
        TextButton(
          onPressed: _clearFilters,
          style: TextButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            minimumSize: Size.zero,
            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
          child: const Text(
            'ล้าง',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 12,
              color: AppTheme.primaryColor,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildActiveFilterChip({
    required IconData icon,
    required String label,
    required VoidCallback onRemove,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
      decoration: BoxDecoration(
        color: AppTheme.primaryBackgroundColor,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 15, color: AppTheme.primaryColor),
          const SizedBox(width: 5),
          Text(
            label,
            style: const TextStyle(
              fontFamily: 'Kanit',
              fontSize: 11,
              color: AppTheme.primaryColor,
            ),
          ),
          const SizedBox(width: 4),
          GestureDetector(
            onTap: onRemove,
            child: const Icon(
              Icons.close_rounded,
              size: 15,
              color: AppTheme.primaryColor,
            ),
          ),
        ],
      ),
    );
  }

  String _formatFilterDate(DateTime date) {
    final localDate = date.toLocal();

    const thaiMonths = [
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

    return '${localDate.day} '
        '${thaiMonths[localDate.month - 1]} '
        '${localDate.year + 543}';
  }

  Widget _buildRecordList() {
    if (_isLoading) {
      return _buildLoadingState();
    }

    if (_errorMessage != null) {
      return _buildErrorState();
    }

    final records = _filteredRecords;

    if (records.isEmpty) {
      return _buildEmptyState();
    }

    return Column(
      children: records.map((record) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 14),
          child: _MedicalRecordCard(
            record: record,
            department: _getDepartment(record),
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => MedicalRecordDetailsPage(record: record),
                ),
              );
            },
          ),
        );
      }).toList(),
    );
  }

  Widget _buildLoadingState() {
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
            'กำลังโหลดประวัติการรักษา...',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 14,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState() {
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
            _errorMessage!,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontFamily: 'Kanit',
              fontSize: 13,
              color: AppTheme.textSecondaryColor,
            ),
          ),
          const SizedBox(height: 12),
          OutlinedButton(
            onPressed: _loadMedicalRecords,
            child: const Text('ลองใหม่', style: TextStyle(fontFamily: 'Kanit')),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 44),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: AppTheme.textSecondaryColor.withValues(alpha: 0.10),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.white.withValues(alpha: 0.90),
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
      child: const Column(
        children: [
          Icon(
            Icons.folder_open_outlined,
            size: 46,
            color: AppTheme.textSecondaryColor,
          ),
          SizedBox(height: 14),
          Text(
            'ไม่พบประวัติการรักษา',
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          SizedBox(height: 5),
          Text(
            'ลองเปลี่ยนวันที่หรือแผนกที่เลือก',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: 'Kanit',
              fontSize: 12,
              fontWeight: FontWeight.w400,
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ],
      ),
    );
  }
}

class _MedicalRecordCard extends StatelessWidget {
  final MedicalRecordModel record;
  final DepartmentModel? department;
  final VoidCallback? onTap;

  const _MedicalRecordCard({required this.record, this.department, this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.fromLTRB(18, 18, 18, 16),
          decoration: BoxDecoration(
            color: AppTheme.surfaceColor,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: AppTheme.textSecondaryColor.withValues(alpha: 0.10),
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.white.withValues(alpha: 0.90),
                blurRadius: 6,
                offset: const Offset(0, -2),
              ),
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.045),
                blurRadius: 12,
                offset: const Offset(0, 4),
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
                    ),
                    child: const Icon(
                      Icons.medical_information_outlined,
                      size: 26,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Expanded(
                          child: Text(
                            _formatDate(record.createdAt),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontFamily: 'Kanit',
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                              color: AppTheme.textPrimaryColor,
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        _buildStatus(),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 0),
              Padding(
                padding: const EdgeInsets.only(left: 66),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (department != null) ...[
                      _buildInfoText('แผนก', department!.name),
                      const SizedBox(height: 6),
                    ],
                    _buildInfoText('อาการหลัก', record.chiefComplaint),
                    const SizedBox(height: 6),
                    _buildInfoText('การวินิจฉัย', record.diagnosis),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              const Divider(height: 1, thickness: 1, color: Color(0xFFE9EDF2)),
              InkWell(
                onTap: onTap,
                borderRadius: BorderRadius.circular(10),
                child: Padding(
                  padding: const EdgeInsets.only(top: 11, bottom: 2),
                  child: Row(
                    children: [
                      const Text(
                        'ดูรายละเอียด',
                        style: TextStyle(
                          fontFamily: 'Kanit',
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                          color: AppTheme.primaryColor,
                        ),
                      ),
                      const Spacer(),
                      Icon(
                        Icons.chevron_right_rounded,
                        size: 22,
                        color: AppTheme.primaryColor,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatus() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFFE1FBE8),
        borderRadius: BorderRadius.circular(14),
      ),
      child: const Text(
        'เสร็จสิ้น',
        style: TextStyle(
          fontFamily: 'Kanit',
          fontSize: 10,
          fontWeight: FontWeight.w500,
          color: Color(0xFF20A84B),
        ),
      ),
    );
  }

  Widget _buildInfoText(String label, String value) {
    return RichText(
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
      text: TextSpan(
        style: const TextStyle(
          fontFamily: 'Kanit',
          fontSize: 13,
          height: 1.45,
          color: AppTheme.textSecondaryColor,
        ),
        children: [
          TextSpan(
            text: '$label: ',
            style: const TextStyle(
              fontWeight: FontWeight.w500,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          TextSpan(
            text: value,
            style: const TextStyle(fontWeight: FontWeight.w400),
          ),
        ],
      ),
    );
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
