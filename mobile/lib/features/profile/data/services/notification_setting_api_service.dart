import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../models/notification_setting_model.dart';

class NotificationSettingApiService {
  NotificationSettingApiService({
    required ApiClient apiClient,
  }) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<NotificationSettingModel> getNotificationSettings({
    required String userId,
  }) async {
    try {
      final response = await _apiClient.dio.get(
        '/notification-settings/users/$userId',
      );

      return NotificationSettingModel.fromJson(
        Map<String, dynamic>.from(
          response.data as Map,
        ),
      );
    } on DioException {
      rethrow;
    }
  }

  Future<NotificationSettingModel> updateNotificationSettings({
    required String userId,
    required bool allNotifications,
    required bool appointmentNotifications,
    required bool medicalRecordNotifications,
    required bool systemNotifications,
  }) async {
    try {
      final response = await _apiClient.dio.patch(
        '/notification-settings/users/$userId',
        data: {
          'all_notifications': allNotifications,
          'appointment_notifications': appointmentNotifications,
          'medical_record_notifications': medicalRecordNotifications,
          'system_notifications': systemNotifications,
        },
      );

      return NotificationSettingModel.fromJson(
        Map<String, dynamic>.from(
          response.data as Map,
        ),
      );
    } on DioException {
      rethrow;
    }
  }
}