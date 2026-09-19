import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import '../../../../core/network/api_client.dart';

import '../../../search/data/models/department_model.dart';
import '../../../search/data/repositories/department_repository.dart';
import '../../../search/data/services/department_api_service.dart';
import '../../data/config/symptom_config.dart';

import 'doctor_selection_page.dart';

class SearchPage extends StatefulWidget {
  final String initialQuery;

  const SearchPage({super.key, this.initialQuery = ''});

  @override
  State<SearchPage> createState() => _SearchPageState();
}

class _NoStretchScrollBehavior extends ScrollBehavior {
  const _NoStretchScrollBehavior();

  @override
  ScrollPhysics getScrollPhysics(BuildContext context) {
    return const ClampingScrollPhysics();
  }
}

class _SearchPageState extends State<SearchPage> {
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _searchFocusNode = FocusNode();

  final DepartmentRepository _departmentRepository = DepartmentRepository(
    departmentApiService: DepartmentApiService(apiClient: ApiClient()),
  );

  String _selectedSymptom = '';

  List<String> _filteredSymptoms = [];
  List<DepartmentModel> _departments = [];

  bool _isLoadingDepartments = true;
  String? _departmentErrorMessage;

  @override
  void initState() {
    super.initState();

    _searchController.text = widget.initialQuery;

    _loadDepartments();

    if (widget.initialQuery.trim().isNotEmpty) {
      _updateSearchResults(widget.initialQuery, autoSelect: true);
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    _searchFocusNode.dispose();
    super.dispose();
  }

  Future<void> _loadDepartments() async {
    setState(() {
      _isLoadingDepartments = true;
      _departmentErrorMessage = null;
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

        _isLoadingDepartments = false;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoadingDepartments = false;
        _departmentErrorMessage = 'ไม่สามารถโหลดข้อมูลแผนกได้';
      });
    }
  }

  void _updateSearchResults(String query, {bool autoSelect = false}) {
    final normalizedQuery = query.trim();

    setState(() {
      if (normalizedQuery.isEmpty) {
        _filteredSymptoms = [];
        _selectedSymptom = '';
        return;
      }

      _filteredSymptoms = SymptomConfig.symptoms
          .where((symptom) => symptom.contains(normalizedQuery))
          .toList();

      if (autoSelect && _filteredSymptoms.isNotEmpty) {
        _selectedSymptom = _filteredSymptoms.first;
      } else {
        _selectedSymptom = '';
      }
    });
  }

  void _selectSymptom(String symptom) {
    setState(() {
      _selectedSymptom = symptom;
      _searchController.text = symptom;
      _searchController.selection = TextSelection.fromPosition(
        TextPosition(offset: _searchController.text.length),
      );
    });
  }

  void _clearSearch() {
    setState(() {
      _searchController.clear();
      _selectedSymptom = '';
    });
  }

  DepartmentModel? _findDepartmentByName(String departmentName) {
    for (final department in _departments) {
      if (department.name.trim() == departmentName.trim()) {
        return department;
      }
    }

    return null;
  }

  List<DepartmentModel> _getRelatedDepartments() {
    final departmentNames =
        SymptomConfig.symptomDepartmentNames[_selectedSymptom] ?? [];

    return departmentNames
        .map(_findDepartmentByName)
        .whereType<DepartmentModel>()
        .toList();
  }

  void _openDoctorSelection(String departmentName) {
    if (_isLoadingDepartments) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('กำลังโหลดข้อมูลแผนก กรุณารอสักครู่')),
      );
      return;
    }

    if (_departmentErrorMessage != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_departmentErrorMessage!),
          action: SnackBarAction(label: 'ลองใหม่', onPressed: _loadDepartments),
        ),
      );
      return;
    }

    final department = _findDepartmentByName(departmentName);

    if (department == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('ไม่พบข้อมูลแผนกจากระบบ')));
      return;
    }

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => DoctorSelectionPage(
          departmentId: department.id,
          departmentName: department.name,
          departmentImageUrl: department.imageUrl,
          departmentDescription: department.description,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: SafeArea(
        child: ScrollConfiguration(
          behavior: const _NoStretchScrollBehavior(),
          child: CustomScrollView(
            slivers: [
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(20, 18, 20, 28),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    _buildHeader(context),
                    const SizedBox(height: 28),
                    _buildSearchField(context),
                    const SizedBox(height: 30),
                    _buildSymptomSection(context),
                    if (_selectedSymptom.isNotEmpty) ...[
                      const SizedBox(height: 30),
                      _buildDepartmentSection(context),
                    ],
                  ]),
                ),
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: _buildBottomNavigation(context),
    );
  }

  Widget _buildHeader(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(16),
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
    );
  }

  Widget _buildSearchField(BuildContext context) {
    return Container(
      height: 52,
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.035),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: TextField(
        controller: _searchController,
        focusNode: _searchFocusNode,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
          color: AppTheme.textPrimaryColor,
          fontWeight: FontWeight.w500,
        ),
        decoration: InputDecoration(
          hintText: 'ค้นหาอาการ แผนก หรือแพทย์',
          hintStyle: Theme.of(
            context,
          ).textTheme.bodyMedium?.copyWith(color: AppTheme.textMutedColor),
          prefixIcon: const Icon(
            Icons.search_rounded,
            size: 21,
            color: AppTheme.primaryColor,
          ),
          suffixIcon: _searchController.text.isNotEmpty
              ? IconButton(
                  onPressed: _clearSearch,
                  icon: const Icon(
                    Icons.close_rounded,
                    size: 19,
                    color: AppTheme.textMutedColor,
                  ),
                )
              : null,
          filled: true,
          fillColor: AppTheme.surfaceColor,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 14,
            vertical: 13,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(
              color: AppTheme.primaryColor,
              width: 1.2,
            ),
          ),
        ),
        onChanged: _updateSearchResults,
      ),
    );
  }

  Widget _buildEmptySymptomState(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 22),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8ECF2)),
      ),
      child: Column(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: AppTheme.primaryBackgroundColor,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.search_off_rounded,
              color: AppTheme.primaryColor,
              size: 23,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'ไม่พบอาการที่ตรงกับคำค้นหา',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: AppTheme.textPrimaryColor,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'ลองค้นหาด้วยคำอื่น',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodySmall?.copyWith(
              color: AppTheme.textSecondaryColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSymptomSection(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'อาการที่เกี่ยวข้อง',
          style: theme.textTheme.titleMedium?.copyWith(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        const SizedBox(height: 12),
        if (_searchController.text.trim().isNotEmpty &&
            _filteredSymptoms.isEmpty)
          _buildEmptySymptomState(context)
        else if (_filteredSymptoms.isNotEmpty)
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _filteredSymptoms.map((symptom) {
              final isSelected = symptom == _selectedSymptom;

              return _buildSymptomChip(
                context,
                label: symptom,
                isSelected: isSelected,
                onTap: () => _selectSymptom(symptom),
              );
            }).toList(),
          ),
      ],
    );
  }

  Widget _buildSymptomChip(
    BuildContext context, {
    required String label,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);

    return Material(
      color: isSelected ? AppTheme.primaryColor : AppTheme.surfaceColor,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? Colors.transparent : const Color(0xFFE5E8ED),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (isSelected) ...[
                const Icon(
                  Icons.check_circle_rounded,
                  size: 14,
                  color: Colors.white,
                ),
                const SizedBox(width: 6),
              ],
              Text(
                label,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontSize: 12,
                  color: isSelected
                      ? Colors.white
                      : AppTheme.textSecondaryColor,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDepartmentSection(BuildContext context) {
    final theme = Theme.of(context);

    final departments = _getRelatedDepartments();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'แผนกที่เกี่ยวข้อง',
          style: theme.textTheme.titleMedium?.copyWith(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        const SizedBox(height: 12),
        if (_isLoadingDepartments)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 20),
            child: Center(child: CircularProgressIndicator()),
          )
        else if (_departmentErrorMessage != null)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
            decoration: BoxDecoration(
              color: AppTheme.surfaceColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFE8ECF2)),
            ),
            child: Column(
              children: [
                Text(
                  _departmentErrorMessage!,
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textSecondaryColor,
                  ),
                ),
                const SizedBox(height: 10),
                TextButton(
                  onPressed: _loadDepartments,
                  child: const Text('ลองใหม่'),
                ),
              ],
            ),
          )
        else if (departments.isEmpty)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
            decoration: BoxDecoration(
              color: AppTheme.surfaceColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFE8ECF2)),
            ),
            child: Text(
              'ไม่พบแผนกที่เกี่ยวข้อง',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: AppTheme.textSecondaryColor,
              ),
            ),
          )
        else
          ...departments.map(
            (department) => _buildDepartmentCard(
              context,
              title: department.name,
              description: department.description ?? '',
              icon: Icons.medical_services_rounded,
              iconColor: AppTheme.primaryColor,
              iconBackgroundColor: AppTheme.primaryBackgroundColor,
              onTap: () => _openDoctorSelection(department.name),
            ),
          ),
      ],
    );
  }

  Widget _buildDepartmentCard(
    BuildContext context, {
    required IconData icon,
    required Color iconBackgroundColor,
    required Color iconColor,
    required String title,
    required String description,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE8ECF2), width: 1),
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: iconBackgroundColor,
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Icon(icon, color: iconColor, size: 25),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.textPrimaryColor,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Text(
                        description,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontSize: 12,
                          height: 1.4,
                          color: AppTheme.textSecondaryColor,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 10),
                const Icon(
                  Icons.chevron_right_rounded,
                  size: 22,
                  color: AppTheme.textMutedColor,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildBottomNavigation(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.06),
            blurRadius: 16,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: NavigationBar(
        selectedIndex: 0,
        onDestinationSelected: (index) {
          if (index == 0) {
            Navigator.of(context).pop();
          }
        },
        backgroundColor: AppTheme.surfaceColor,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        height: 76,
        indicatorColor: AppTheme.primaryBackgroundColor,
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: 'หน้าแรก',
          ),
          NavigationDestination(
            icon: Icon(Icons.calendar_month_outlined),
            selectedIcon: Icon(Icons.calendar_month_rounded),
            label: 'นัดหมาย',
          ),
          NavigationDestination(
            icon: Icon(Icons.description_outlined),
            selectedIcon: Icon(Icons.description_rounded),
            label: 'ประวัติ',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline_rounded),
            selectedIcon: Icon(Icons.person_rounded),
            label: 'โปรไฟล์',
          ),
        ],
      ),
    );
  }
}
