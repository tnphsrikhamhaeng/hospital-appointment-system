import 'package:flutter/foundation.dart';

enum DoctorScheduleWeekday {
  monday,
  tuesday,
  wednesday,
  thursday,
  friday,
  saturday,
  sunday,
}

@immutable
class DoctorScheduleModel {
  const DoctorScheduleModel({
    required this.id,
    required this.doctorId,
    required this.weekday,
    required this.startTime,
    required this.endTime,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
  });

  final String id;
  final String doctorId;
  final DoctorScheduleWeekday weekday;
  final String startTime;
  final String endTime;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory DoctorScheduleModel.fromJson(
    Map<String, dynamic> json,
  ) {
    return DoctorScheduleModel(
      id: json['id'] as String,
      doctorId: json['doctor_id'] as String,
      weekday: _parseWeekday(
        json['weekday'] as String,
      ),
      startTime: _normalizeTime(
        json['start_time'] as String,
      ),
      endTime: _normalizeTime(
        json['end_time'] as String,
      ),
      isActive: json['is_active'] as bool,
      createdAt: DateTime.parse(
        json['created_at'] as String,
      ),
      updatedAt: DateTime.parse(
        json['updated_at'] as String,
      ),
    );
  }

  static DoctorScheduleWeekday _parseWeekday(
    String value,
  ) {
    switch (value.toLowerCase()) {
      case 'monday':
        return DoctorScheduleWeekday.monday;

      case 'tuesday':
        return DoctorScheduleWeekday.tuesday;

      case 'wednesday':
        return DoctorScheduleWeekday.wednesday;

      case 'thursday':
        return DoctorScheduleWeekday.thursday;

      case 'friday':
        return DoctorScheduleWeekday.friday;

      case 'saturday':
        return DoctorScheduleWeekday.saturday;

      case 'sunday':
        return DoctorScheduleWeekday.sunday;

      default:
        throw FormatException(
          'Unknown doctor schedule weekday: $value',
        );
    }
  }

  static String _normalizeTime(String value) {
    if (value.length >= 5) {
      return value.substring(0, 5);
    }

    return value;
  }
}