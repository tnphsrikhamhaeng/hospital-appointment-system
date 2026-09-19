import '../models/notification_setting_model.dart';
import '../services/notification_setting_api_service.dart';

class NotificationSettingRepository {
  NotificationSettingRepository({
    required NotificationSettingApiService apiService,
  }) : _apiService = apiService;

  final NotificationSettingApiService _apiService;

  Future<NotificationSettingModel> getNotificationSettings({
    required String userId,
  }) {
    return _apiService.getNotificationSettings(
      userId: userId,
    );
  }

  Future<NotificationSettingModel> updateNotificationSettings({
    required String userId,
    required bool allNotifications,
    required bool appointmentNotifications,
    required bool medicalRecordNotifications,
    required bool systemNotifications,
  }) {
    return _apiService.updateNotificationSettings(
      userId: userId,
      allNotifications: allNotifications,
      appointmentNotifications: appointmentNotifications,
      medicalRecordNotifications: medicalRecordNotifications,
      systemNotifications: systemNotifications,
    );
  }
}