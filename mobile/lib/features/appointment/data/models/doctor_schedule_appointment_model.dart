import 'package:flutter/foundation.dart';

import 'appointment_model.dart';

@immutable
class DoctorScheduleAppointmentModel {
  const DoctorScheduleAppointmentModel({
    required this.id,
    required this.patientId,
    required this.patientName,
    required this.appointmentDate,
    required this.startTime,
    required this.endTime,
    required this.status,
  });

  final String id;
  final String patientId;
  final String patientName;

  final DateTime appointmentDate;

  final String startTime;
  final String endTime;

  final AppointmentStatus status;

  factory DoctorScheduleAppointmentModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return DoctorScheduleAppointmentModel(
      id: json['id'] as String,
      patientId: json['patient_id'] as String,
      patientName: json['patient_name'] as String,
      appointmentDate: DateTime.parse(
        json['appointment_date'] as String,
      ),
      startTime: _normalizeTime(
        json['start_time'] as String,
      ),
      endTime: _normalizeTime(
        json['end_time'] as String,
      ),
      status: _parseStatus(
        json['status'] as String,
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

  static String _normalizeTime(
    String value,
  ) {
    if (value.length >= 5) {
      return value.substring(0, 5);
    }

    return value;
  }
}