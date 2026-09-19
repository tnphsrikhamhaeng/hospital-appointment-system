import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import 'doctor_selection_page.dart';
import '../../data/models/department_model.dart';
import '../../data/repositories/department_repository.dart';
import '../../data/services/department_api_service.dart';
import '../../../../core/network/api_client.dart';

class DepartmentSelectionPage extends StatefulWidget {
  const DepartmentSelectionPage({super.key});

  @override
  State<DepartmentSelectionPage> createState() =>
      _DepartmentSelectionPageState();
}

class _DepartmentSelectionPageState extends State<DepartmentSelectionPage> {
  final TextEditingController _searchController = TextEditingController();
  final DepartmentRepository _departmentRepository = DepartmentRepository(
    departmentApiService: DepartmentApiService(apiClient: ApiClient()),
  );

  List<DepartmentModel> _departments = [];
  List<DepartmentModel> _filteredDepartments = [];

  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();

    _searchController.addListener(_filterDepartments);

    _loadDepartments();
  }

  void _filterDepartments() {
    final query = _searchController.text.trim().toLowerCase();

    setState(() {
      if (query.isEmpty) {
        _filteredDepartments = _departments;
        return;
      }

      _filteredDepartments = _departments
          .where((department) => department.name.toLowerCase().contains(query))
          .toList();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadDepartments() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final departments = await _departmentRepository.getDepartments();

      if (!mounted) {
        return;
      }

      setState(() {
        _departments = departments
            .where((department) => department.status == DepartmentStatus.active)
            .toList();

        _filteredDepartments = _departments;
        _isLoading = false;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
        _errorMessage = 'ไม่สามารถโหลดข้อมูลแผนกได้';
      });
    }
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
          'เลือกแผนก',
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

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'เลือกแผนกที่ต้องการ',
            style: theme.textTheme.headlineSmall?.copyWith(
              fontSize: 22,
              fontWeight: FontWeight.w700,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'ค้นหาหรือเลือกแผนกเพื่อทำการนัดหมาย',
            style: theme.textTheme.bodySmall?.copyWith(
              fontSize: 12,
              height: 1.4,
              color: AppTheme.textSecondaryColor,
            ),
          ),
          const SizedBox(height: 20),
          _buildSearchField(context),
          const SizedBox(height: 24),
          Text(
            'แผนกทั้งหมด',
            style: theme.textTheme.titleMedium?.copyWith(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimaryColor,
            ),
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
          else if (_filteredDepartments.isEmpty)
            _buildEmptyState(context)
          else
            _buildDepartmentGrid(context),
        ],
      ),
    );
  }

  Widget _buildSearchField(BuildContext context) {
    return TextField(
      controller: _searchController,
      textInputAction: TextInputAction.search,
      decoration: InputDecoration(
        hintText: 'ค้นหาแผนก...',
        hintStyle: Theme.of(context).textTheme.bodyMedium?.copyWith(
          fontSize: 13,
          color: AppTheme.textMutedColor,
        ),
        prefixIcon: const Icon(
          Icons.search_rounded,
          size: 21,
          color: AppTheme.textMutedColor,
        ),
        filled: true,
        fillColor: AppTheme.surfaceColor,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 14,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFFE8ECF2)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFFE8ECF2)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(
            color: AppTheme.primaryColor,
            width: 1.2,
          ),
        ),
      ),
    );
  }

  Widget _buildDepartmentGrid(BuildContext context) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: _filteredDepartments.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 0.95,
      ),
      itemBuilder: (context, index) {
        final department = _filteredDepartments[index];

        return _buildDepartmentCard(context, department: department);
      },
    );
  }

  IconData _getDepartmentIcon(String department) {
    switch (department) {
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

  Color _getDepartmentIconColor(String department) {
    switch (department) {
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

  Widget _buildDepartmentCard(
    BuildContext context, {
    required DepartmentModel department,
  }) {
    final theme = Theme.of(context);
    final iconColor = _getDepartmentIconColor(department.name);

    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => DoctorSelectionPage(
                departmentId: department.id,
                departmentName: department.name,
                departmentDescription: department.description,
                departmentImageUrl: department.imageUrl,
              ),
            ),
          );
        },
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
          decoration: BoxDecoration(
            color: AppTheme.surfaceColor,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: const Color(0xFFE8ECF2)),
            boxShadow: const [
              BoxShadow(
                blurRadius: 8,
                offset: Offset(0, 2),
                color: Color(0x08000000),
              ),
            ],
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: iconColor.withValues(alpha: 0.12),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  _getDepartmentIcon(department.name),
                  color: iconColor,
                  size: 27,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                department.name,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimaryColor,
                ),
              ),
              const SizedBox(height: 5),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
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
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: AppTheme.primaryBackgroundColor,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.search_off_rounded,
              color: AppTheme.primaryColor,
              size: 27,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'ไม่พบแผนกที่ค้นหา',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimaryColor,
            ),
          ),
          const SizedBox(height: 5),
          Text(
            'ลองค้นหาด้วยชื่อแผนกอื่น',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodySmall?.copyWith(
              fontSize: 11,
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
          OutlinedButton(
            onPressed: _loadDepartments,
            child: const Text('ลองใหม่'),
          ),
        ],
      ),
    );
  }
}
