import 'package:firebase_messaging/firebase_messaging.dart';

import '../../features/notification/data/services/user_device_api_service.dart';
import '../network/api_client.dart';

class FcmService {
  FcmService._();

  static final FirebaseMessaging _messaging =
      FirebaseMessaging.instance;

  static final ApiClient _apiClient = ApiClient();

  static final UserDeviceApiService _userDeviceApiService =
      UserDeviceApiService(
    apiClient: _apiClient,
  );

  static Future<void> initialize() async {
    await _requestPermission();

    final token = await _messaging.getToken();

    if (token != null) {
      print('FCM Token: $token');

      await _registerDeviceToken(token);
    }

    _messaging.onTokenRefresh.listen(
      (newToken) async {
        print('FCM Token refreshed: $newToken');

        await _registerDeviceToken(newToken);
      },
    );

    FirebaseMessaging.onMessage.listen(
      (RemoteMessage message) {
        print(
          'FCM foreground message: '
          '${message.notification?.title}',
        );
      },
    );
  }

  static Future<void> _registerDeviceToken(
    String token,
  ) async {
    await _userDeviceApiService.registerOrUpdateDevice(
      deviceToken: token,
      platform: 'android',
      deviceName: 'CareFlow Mobile',
    );
  }

  static Future<void> _requestPermission() async {
    await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
  }
}