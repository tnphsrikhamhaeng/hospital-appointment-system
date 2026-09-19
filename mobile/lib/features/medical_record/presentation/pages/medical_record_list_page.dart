import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../data/models/medical_record_model.dart';
import '../../data/repositories/medical_record_repository.dart';
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
  State<MedicalRecordListPage> createState() =>
      _MedicalRecordListPageState();
}

class _MedicalRecordListPageState
    extends State<MedicalRecordListPage> {
  late final MedicalRecordRepository _medicalRecordRepository;

  final TextEditingController _searchController =
      TextEditingController();

  String _selectedFilter = 'ทั้งหมด';

  final List<String> _filters = const [
    'ทั้งหมด',
    '2569',
    '2568',
  ];

  List<MedicalRecordModel> _records = [];

  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();

    final apiClient = ApiClient();

    _medicalRecordRepository = MedicalRecordRepository(
      medicalRecordApiService:
          MedicalRecordApiService(
        apiClient: apiClient,
      ),
    );

    _loadMedicalRecords();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
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
      final records =
          await _medicalRecordRepository.getMedicalRecords();

      if (!mounted) {
        return;
      }

      setState(() {
        _records = records;
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
        _errorMessage =
            error.toString().replaceFirst(
              'Exception: ',
              '',
            );
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

  List<MedicalRecordModel> get _filteredRecords {
    final query =
        _searchController.text.trim().toLowerCase();

    return _records.where((record) {
      final matchesSearch =
          query.isEmpty ||
          record.chiefComplaint
              .toLowerCase()
              .contains(query) ||
          record.diagnosis
              .toLowerCase()
              .contains(query) ||
          record.doctorId
              .toLowerCase()
              .contains(query);

      final year =
          (record.createdAt.toLocal().year + 543).toString();

      final matchesYear =
          _selectedFilter == 'ทั้งหมด' ||
          year == _selectedFilter;

      return matchesSearch && matchesYear;
    }).toList();
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
          child: RefreshIndicator(
            onRefresh: _loadMedicalRecords,
            color: AppTheme.primaryColor,
            child: SingleChildScrollView(
            keyboardDismissBehavior:
                ScrollViewKeyboardDismissBehavior.onDrag,
            physics:
                const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(
              20,
              20,
              20,
              100,
            ),
            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                _buildSearchField(),
                const SizedBox(height: 16),
                _buildFilterChips(),
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

  Widget _buildSearchField() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppTheme.textSecondaryColor
              .withValues(alpha: 0.10),
        ),
        boxShadow: [
          BoxShadow(
            color:
                Colors.white.withValues(alpha: 0.90),
            blurRadius: 6,
            offset: const Offset(0, -2),
          ),
          BoxShadow(
            color:
                Colors.black.withValues(alpha: 0.04),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: TextField(
        controller: _searchController,
        onChanged: (_) {
          setState(() {});
        },
        style: const TextStyle(
          fontFamily: 'Kanit',
          fontSize: 14,
          fontWeight: FontWeight.w400,
          color: AppTheme.textPrimaryColor,
        ),
        decoration: InputDecoration(
          hintText: 'ค้นหาประวัติการรักษา...',
          hintStyle: const TextStyle(
            fontFamily: 'Kanit',
            fontSize: 14,
            fontWeight: FontWeight.w400,
            color: AppTheme.textSecondaryColor,
          ),
          prefixIcon: const Icon(
            Icons.search_rounded,
            size: 22,
            color: AppTheme.primaryColor,
          ),
          suffixIcon: _searchController.text.isEmpty
              ? null
              : IconButton(
                  onPressed: () {
                    _searchController.clear();
                    setState(() {});
                  },
                  icon: const Icon(
                    Icons.close_rounded,
                    size: 18,
                  ),
                ),
          filled: true,
          fillColor: Colors.transparent,
          contentPadding:
              const EdgeInsets.symmetric(
            horizontal: 14,
            vertical: 15,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide.none,
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide(
              color: AppTheme.primaryColor
                  .withValues(alpha: 0.45),
              width: 1.2,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFilterChips() {
    return SizedBox(
      height: 44,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: _filters.length,
        separatorBuilder: (_, __) =>
            const SizedBox(width: 9),
        itemBuilder: (context, index) {
          final filter = _filters[index];
          final isSelected =
              filter == _selectedFilter;

          return GestureDetector(
            onTap: () {
              setState(() {
                _selectedFilter = filter;
              });
            },
            child: AnimatedContainer(
              duration:
                  const Duration(milliseconds: 180),
              padding:
                  const EdgeInsets.symmetric(
                horizontal: 15,
                vertical: 10,
              ),
              decoration: BoxDecoration(
                color: isSelected
                    ? AppTheme.primaryColor
                    : AppTheme.surfaceColor,
                borderRadius:
                    BorderRadius.circular(12),
                border: Border.all(
                  color: isSelected
                      ? AppTheme.primaryColor
                      : AppTheme.textSecondaryColor
                          .withValues(alpha: 0.12),
                ),
                boxShadow: isSelected
                    ? [
                        BoxShadow(
                          color: AppTheme.primaryColor
                              .withValues(alpha: 0.18),
                          blurRadius: 8,
                          offset:
                              const Offset(0, 3),
                        ),
                      ]
                    : [
                        BoxShadow(
                          color: Colors.white
                              .withValues(alpha: 0.80),
                          blurRadius: 5,
                          offset:
                              const Offset(0, -1),
                        ),
                        BoxShadow(
                          color: Colors.black
                              .withValues(alpha: 0.025),
                          blurRadius: 6,
                          offset:
                              const Offset(0, 2),
                        ),
                      ],
              ),
              child: Text(
                filter,
                style: TextStyle(
                  fontFamily: 'Kanit',
                  fontSize: 13,
                  fontWeight: isSelected
                      ? FontWeight.w500
                      : FontWeight.w400,
                  color: isSelected
                      ? Colors.white
                      : AppTheme.textSecondaryColor,
                ),
              ),
            ),
          );
        },
      ),
    );
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
          padding:
              const EdgeInsets.only(bottom: 14),
          child: _MedicalRecordCard(
            record: record,
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) =>
                      MedicalRecordDetailsPage(
                    record: record,
                  ),
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
      padding:
          const EdgeInsets.symmetric(vertical: 48),
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
        border: Border.all(
          color:
              AppTheme.errorColor.withValues(
            alpha: 0.20,
          ),
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
            child: const Text(
              'ลองใหม่',
              style: TextStyle(
                fontFamily: 'Kanit',
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      width: double.infinity,
      padding:
          const EdgeInsets.symmetric(
        horizontal: 24,
        vertical: 44,
      ),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: AppTheme.textSecondaryColor
              .withValues(alpha: 0.10),
        ),
        boxShadow: [
          BoxShadow(
            color:
                Colors.white.withValues(alpha: 0.90),
            blurRadius: 6,
            offset: const Offset(0, -2),
          ),
          BoxShadow(
            color:
                Colors.black.withValues(alpha: 0.035),
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
            'ลองค้นหาด้วยคำอื่นหรือเปลี่ยนตัวกรอง',
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
  final VoidCallback? onTap;

  const _MedicalRecordCard({
    required this.record,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Container(
          width: double.infinity,
          padding:
              const EdgeInsets.fromLTRB(
            18,
            18,
            18,
            16,
          ),
          decoration: BoxDecoration(
            color: AppTheme.surfaceColor,
            borderRadius:
                BorderRadius.circular(14),
            border: Border.all(
              color: AppTheme.textSecondaryColor
                  .withValues(alpha: 0.10),
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.white
                    .withValues(alpha: 0.90),
                blurRadius: 6,
                offset: const Offset(0, -2),
              ),
              BoxShadow(
                color: Colors.black
                    .withValues(alpha: 0.045),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment:
                    CrossAxisAlignment.center,
                children: [
                  Container(
                    width: 52,
                    height: 52,
                    decoration: BoxDecoration(
                      color: AppTheme
                          .primaryBackgroundColor,
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
                    child: Column(
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [
                        Row(
                          crossAxisAlignment:
                              CrossAxisAlignment.center,
                          children: [
                            Expanded(
                              child: Text(
                                'ประวัติการรักษา',
                                maxLines: 1,
                                overflow:
                                    TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontFamily: 'Kanit',
                                  fontSize: 17,
                                  fontWeight:
                                      FontWeight.w600,
                                  color: AppTheme
                                      .textPrimaryColor,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            _buildStatus(),
                          ],
                        ),
                        const SizedBox(height: 3),
                        Text(
                          _formatDate(
                            record.createdAt,
                          ),
                          style: const TextStyle(
                            fontFamily: 'Kanit',
                            fontSize: 13,
                            fontWeight:
                                FontWeight.w400,
                            color: AppTheme
                                .textSecondaryColor,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Padding(
                padding:
                    const EdgeInsets.only(left: 66),
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    _buildInfoText(
                      'อาการหลัก',
                      record.chiefComplaint,
                    ),
                    const SizedBox(height: 6),
                    _buildInfoText(
                      'การวินิจฉัย',
                      record.diagnosis,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              const Divider(
                height: 1,
                thickness: 1,
                color: Color(0xFFE9EDF2),
              ),
              InkWell(
                onTap: onTap,
                borderRadius:
                    BorderRadius.circular(10),
                child: Padding(
                  padding:
                      const EdgeInsets.only(
                    top: 11,
                    bottom: 2,
                  ),
                  child: Row(
                    children: [
                      const Text(
                        'ดูรายละเอียด',
                        style: TextStyle(
                          fontFamily: 'Kanit',
                          fontSize: 13,
                          fontWeight:
                              FontWeight.w500,
                          color:
                              AppTheme.primaryColor,
                        ),
                      ),
                      const Spacer(),
                      Icon(
                        Icons.chevron_right_rounded,
                        size: 22,
                        color:
                            AppTheme.primaryColor,
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
      padding:
          const EdgeInsets.symmetric(
        horizontal: 9,
        vertical: 4,
      ),
      decoration: BoxDecoration(
        color: const Color(0xFFE1FBE8),
        borderRadius:
            BorderRadius.circular(14),
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

  Widget _buildInfoText(
    String label,
    String value,
  ) {
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
            style: const TextStyle(
              fontWeight: FontWeight.w400,
            ),
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