import 'package:onesignal_flutter/onesignal_flutter.dart';

import '../../features/profile/data/repositories/profile_repository.dart';
import '../../features/profile/data/services/profile_api_service.dart';
import '../network/api_client.dart';

class OneSignalService {
  OneSignalService._();

  static const String _appId =
      'f7879269-a060-4105-bcff-bcfc928a9c75';

  static Future<void> initialize() async {
    try {
      OneSignal.Debug.setLogLevel(OSLogLevel.verbose);

      OneSignal.initialize(_appId);

      await OneSignal.Notifications.requestPermission(true);

      print('OneSignal initialized successfully');
    } catch (error) {
      print(
        'OneSignal initialization failed: $error',
      );
    }
  }

  static Future<void> identifyCurrentUser() async {
    try {
      final apiClient = ApiClient();

      final profileApiService = ProfileApiService(
        apiClient: apiClient,
      );

      final profileRepository = ProfileRepository(
        profileApiService: profileApiService,
      );

      final profile = await profileRepository.getProfile();

      await OneSignal.login(profile.id);

      print(
        'OneSignal user identified: ${profile.id}',
      );
    } catch (error) {
      print(
        'OneSignal user identification failed: $error',
      );
    }
  }
}