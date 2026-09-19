import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../models/notification_model.dart';

class NotificationApiService {
  NotificationApiService({
    required ApiClient apiClient,
  }) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<List<NotificationModel>>
      getPatientNotifications({
    required String patientId,
  }) async {
    try {
      final response = await _apiClient.dio.get(
        '/notifications',
      );

      final data =
          response.data as List<dynamic>;

      return data
          .map(
            (item) =>
                NotificationModel.fromJson(
              item as Map<String, dynamic>,
            ),
          )
          .toList();
    } on DioException {
      rethrow;
    }
  }

  Future<NotificationModel>
      getNotificationById({
    required String notificationId,
  }) async {
    try {
      final response = await _apiClient.dio.get(
        '/notifications/$notificationId',
      );

      return NotificationModel.fromJson(
        Map<String, dynamic>.from(
          response.data as Map,
        ),
      );
    } on DioException {
      rethrow;
    }
  }

  Future<NotificationModel>
      markNotificationAsRead({
    required String notificationId,
  }) async {
    try {
      final response = await _apiClient.dio.patch(
        '/notifications/$notificationId/read',
      );

      return NotificationModel.fromJson(
        Map<String, dynamic>.from(
          response.data as Map,
        ),
      );
    } on DioException {
      rethrow;
    }
  }
}