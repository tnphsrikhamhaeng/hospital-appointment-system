enum NotificationType {
  appointmentConfirmed,
  reminder3Days,
  reminder1Day,
  reminder30Minutes,
  readyForConsultation,
  consultationDelayed,
  appointmentCancelled,
  appointmentRescheduled,

}

enum NotificationStatus {
  sent,
  failed,
  read,
}

class NotificationModel {
  final String id;
  final String appointmentId;
  final String patientId;
  final NotificationType type;
  final NotificationStatus status;
  final String title;
  final String body;
  final DateTime? sentAt;
  final DateTime? readAt;
  final DateTime createdAt;

  const NotificationModel({
    required this.id,
    required this.appointmentId,
    required this.patientId,
    required this.type,
    required this.status,
    required this.title,
    required this.body,
    required this.sentAt,
    required this.readAt,
    required this.createdAt,
  });

  factory NotificationModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return NotificationModel(
      id: json['id'] as String,
      appointmentId: json['appointment_id'] as String,
      patientId: json['patient_id'] as String,
      type: _parseType(
        json['notification_type'] as String,
      ),
      status: _parseStatus(
        json['notification_status'] as String,
      ),
      title: json['title'] as String,
      body: json['body'] as String,
      sentAt: _parseDateTime(json['sent_at']),
      readAt: _parseDateTime(json['read_at']),
      createdAt: DateTime.parse(
        json['created_at'] as String,
      ),
    );
  }

  static NotificationType _parseType(
    String value,
  ) {
    switch (value) {
      case 'appointment_confirmed':
        return NotificationType.appointmentConfirmed;

      case 'reminder_3_days':
        return NotificationType.reminder3Days;

      case 'reminder_1_day':
        return NotificationType.reminder1Day;

      case 'reminder_30_minutes':
        return NotificationType.reminder30Minutes;

      case 'ready_for_consultation':
        return NotificationType.readyForConsultation;

      case 'consultation_delayed':
        return NotificationType.consultationDelayed;

      case 'appointment_cancelled':
        return NotificationType.appointmentCancelled;

      case 'appointment_rescheduled':
        return NotificationType.appointmentRescheduled;

      default:
        throw ArgumentError(
          'Unknown notification type: $value',
        );
    }
  }

  static NotificationStatus _parseStatus(
    String value,
  ) {
    switch (value) {
      case 'sent':
        return NotificationStatus.sent;

      case 'failed':
        return NotificationStatus.failed;

      case 'read':
        return NotificationStatus.read;

      default:
        throw ArgumentError(
          'Unknown notification status: $value',
        );
    }
  }

  static DateTime? _parseDateTime(
    dynamic value,
  ) {
    if (value == null) {
      return null;
    }

    return DateTime.parse(
      value as String,
    );
  }

  bool get isRead {
    return status == NotificationStatus.read ||
        readAt != null;
  }
}