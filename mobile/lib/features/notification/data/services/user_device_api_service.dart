import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';

class UserDeviceApiService {
  UserDeviceApiService({
    required ApiClient apiClient,
  }) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<void> registerOrUpdateDevice({
    required String deviceToken,
    required String platform,
    required String deviceName,
  }) async {
    try {
      await _apiClient.dio.post(
        '/user-devices',
        data: {
          'device_token': deviceToken,
          'platform': platform,
          'device_name': deviceName,
        },
      );
    } on DioException {
      rethrow;
    }
  }
}