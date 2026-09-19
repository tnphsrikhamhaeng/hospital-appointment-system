import 'package:flutter/foundation.dart';

enum AppointmentStatus {
  confirmed,
  checkedIn,
  cancelled,
  completed,
  inProgress,
  noShow,
}

@immutable
class AppointmentModel {
  const AppointmentModel({
    required this.id,
    required this.patientId,
    required this.doctorId,
    required this.departmentId,
    required this.appointmentDate,
    required this.startTime,
    required this.endTime,
    required this.reason,
    required this.status,
    this.cancelledReason,
    this.cancelledAt,
    this.confirmedAt,
    required this.createdAt,
    required this.updatedAt,
  });

  final String id;
  final String patientId;
  final String doctorId;
  final String departmentId;

  final DateTime appointmentDate;

  final String startTime;
  final String endTime;

  final String? reason;

  final AppointmentStatus status;

  final String? cancelledReason;
  final DateTime? cancelledAt;
  final DateTime? confirmedAt;

  final DateTime createdAt;
  final DateTime updatedAt;

  factory AppointmentModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return AppointmentModel(
      id: json['id'] as String,
      patientId: json['patient_id'] as String,
      doctorId: json['doctor_id'] as String,
      departmentId: json['department_id'] as String,
      appointmentDate: DateTime.parse(
        json['appointment_date'] as String,
      ),
      startTime: _normalizeTime(
        json['start_time'] as String,
      ),
      endTime: _normalizeTime(
        json['end_time'] as String,
      ),
      reason: json['reason'] as String?,
      status: _parseStatus(
        json['status'] as String,
      ),
      cancelledReason:
          json['cancelled_reason'] as String?,
      cancelledAt:
          _parseNullableDateTime(
        json['cancelled_at'],
      ),
      confirmedAt:
          _parseNullableDateTime(
        json['confirmed_at'],
      ),
      createdAt: DateTime.parse(
        json['created_at'] as String,
      ),
      updatedAt: DateTime.parse(
        json['updated_at'] as String,
      ),
    );
  }

  static AppointmentStatus _parseStatus(
    String value,
  ) {
    switch (value.toLowerCase()) {
      case 'confirmed':
        return AppointmentStatus.confirmed;

      case 'checked_in':
        return AppointmentStatus.checkedIn;

      case 'cancelled':
        return AppointmentStatus.cancelled;

      case 'completed':
        return AppointmentStatus.completed;

      case 'in_progress':
        return AppointmentStatus.inProgress;

      case 'no_show':
        return AppointmentStatus.noShow;

      default:
        throw FormatException(
          'Unknown appointment status: $value',
        );
    }
  }

  static DateTime? _parseNullableDateTime(
    dynamic value,
  ) {
    if (value == null) {
      return null;
    }

    return DateTime.parse(
      value as String,
    );
  }

  static String _normalizeTime(
    String value,
  ) {
    if (value.length >= 5) {
      return value.substring(0, 5);
    }

    return value;
  }

  String get statusValue {
    switch (status) {
      case AppointmentStatus.confirmed:
        return 'confirmed';

      case AppointmentStatus.checkedIn:
        return 'checked_in';

      case AppointmentStatus.cancelled:
        return 'cancelled';

      case AppointmentStatus.completed:
        return 'completed';

      case AppointmentStatus.inProgress:
        return 'in_progress';

      case AppointmentStatus.noShow:
        return 'no_show';
    }
  }
}