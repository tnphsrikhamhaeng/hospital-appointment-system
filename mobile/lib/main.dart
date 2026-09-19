import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';

import 'core/theme/app_theme.dart';
import 'core/notification/fcm_service.dart';

import 'features/auth/presentation/pages/login_page.dart';
import 'features/profile/presentation/pages/profile_page.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp();
  await FcmService.initialize();

  runApp(const CareFlowApp());
}

class CareFlowApp extends StatelessWidget {
  const CareFlowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'CareFlow',
      theme: AppTheme.lightTheme,

      routes: {
        '/login': (context) => const LoginPage(),
        '/profile': (context) => const ProfilePage(),
      },

      home: const LoginPage(),
    );
  }
}