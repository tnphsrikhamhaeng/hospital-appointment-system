import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../../features/home/presentation/pages/home_page.dart';
import '../../features/appointment/presentation/pages/appointment_list_page.dart';
import '../../features/profile/presentation/pages/profile_page.dart';
import '../../features/medical_record/presentation/pages/medical_record_list_page.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => AppShellState();
}

class AppShellState extends State<AppShell> {
  int _currentIndex = 0;

  final List<Widget> _pages = const [
    HomePage(),
    AppointmentListPage(),
    MedicalRecordListPage(),
    ProfilePage(),
  ];

  void _onNavigationItemTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  void goToHome() {
    setState(() {
      _currentIndex = 0;
    });
  }
  void goToAppointments() {
  setState(() {
    _currentIndex = 1;
  });
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: Container(
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
          selectedIndex: _currentIndex,
          onDestinationSelected: _onNavigationItemTapped,
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
              label: 'ประวัติการรักษา',
            ),
            NavigationDestination(
              icon: Icon(Icons.person_outline_rounded),
              selectedIcon: Icon(Icons.person_rounded),
              label: 'โปรไฟล์',
            ),
          ],
        ),
      ),
    );
  }
}
