import '../models/notification_model.dart';
import '../services/notification_api_service.dart';

class NotificationRepository {
  NotificationRepository({
    required NotificationApiService apiService,
  }) : _apiService = apiService;

  final NotificationApiService _apiService;

  Future<List<NotificationModel>>
      getPatientNotifications({
    required String patientId,
  }) {
    return _apiService.getPatientNotifications(
      patientId: patientId,
    );
  }

  Future<NotificationModel>
      getNotificationById({
    required String notificationId,
  }) {
    return _apiService.getNotificationById(
      notificationId: notificationId,
    );
  }

  Future<NotificationModel>
      markNotificationAsRead({
    required String notificationId,
  }) {
    return _apiService.markNotificationAsRead(
      notificationId: notificationId,
    );
  }
}