class NotificationSettingModel {
  final String id;
  final String userId;
  final bool allNotifications;
  final bool appointmentNotifications;
  final bool medicalRecordNotifications;
  final bool systemNotifications;
  final DateTime createdAt;
  final DateTime updatedAt;

  const NotificationSettingModel({
    required this.id,
    required this.userId,
    required this.allNotifications,
    required this.appointmentNotifications,
    required this.medicalRecordNotifications,
    required this.systemNotifications,
    required this.createdAt,
    required this.updatedAt,
  });

  factory NotificationSettingModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return NotificationSettingModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      allNotifications: json['all_notifications'] as bool,
      appointmentNotifications:
          json['appointment_notifications'] as bool,
      medicalRecordNotifications:
          json['medical_record_notifications'] as bool,
      systemNotifications:
          json['system_notifications'] as bool,
      createdAt: DateTime.parse(
        json['created_at'] as String,
      ),
      updatedAt: DateTime.parse(
        json['updated_at'] as String,
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'all_notifications': allNotifications,
      'appointment_notifications': appointmentNotifications,
      'medical_record_notifications': medicalRecordNotifications,
      'system_notifications': systemNotifications,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}