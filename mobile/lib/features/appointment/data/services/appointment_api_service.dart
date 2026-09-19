import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../models/appointment_model.dart';
import '../models/doctor_schedule_appointment_model.dart';

class AppointmentApiService {
  AppointmentApiService({required ApiClient apiClient})
    : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<AppointmentModel> createAppointment({
    required String patientId,
    required String doctorId,
    required DateTime appointmentDate,
    required String startTime,
    String? reason,
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '/appointments',
        queryParameters: {'patient_id': patientId},
        data: {
          'doctor_id': doctorId,
          'appointment_date': _formatDate(appointmentDate),
          'start_time': _normalizeTimeForApi(startTime),
          'reason': reason,
        },
      );

      return AppointmentModel.fromJson(
        Map<String, dynamic>.from(response.data as Map),
      );
    } on DioException {
      rethrow;
    }
  }

  Future<AppointmentModel> getAppointmentById({
    required String appointmentId,
  }) async {
    try {
      final response = await _apiClient.dio.get('/appointments/$appointmentId');

      return AppointmentModel.fromJson(
        Map<String, dynamic>.from(response.data as Map),
      );
    } on DioException {
      rethrow;
    }
  }

  Future<List<AppointmentModel>> getPatientAppointments({
    required String patientId,
  }) async {
    try {
      final response = await _apiClient.dio.get(
        '/appointments/patients/$patientId',
      );

      final data = response.data as List<dynamic>;

      return data
          .map(
            (item) => AppointmentModel.fromJson(item as Map<String, dynamic>),
          )
          .toList();
    } on DioException {
      rethrow;
    }
  }

  Future<List<DoctorScheduleAppointmentModel>> getDoctorSchedule({
    required String doctorId,
    required DateTime appointmentDate,
  }) async {
    try {
      final response = await _apiClient.dio.get(
        '/appointments/doctors/$doctorId/schedule',
        queryParameters: {'appointment_date': _formatDate(appointmentDate)},
      );

      final data = response.data as List<dynamic>;

      return data
          .map(
            (item) => DoctorScheduleAppointmentModel.fromJson(
              item as Map<String, dynamic>,
            ),
          )
          .toList();
    } on DioException {
      rethrow;
    }
  }

  Future<AppointmentModel> rescheduleAppointment({
    required String appointmentId,
    required DateTime appointmentDate,
    required String startTime,
  }) async {
    try {
      final response = await _apiClient.dio.patch(
        '/appointments/$appointmentId/reschedule',
        data: {
          'appointment_date': _formatDate(appointmentDate),
          'start_time': _normalizeTimeForApi(startTime),
        },
      );

      return AppointmentModel.fromJson(
        Map<String, dynamic>.from(response.data as Map),
      );
    } on DioException {
      rethrow;
    }
  }

  Future<AppointmentModel> cancelAppointment({
    required String appointmentId,
    required String cancelledReason,
  }) async {
    try {
      final response = await _apiClient.dio.patch(
        '/appointments/$appointmentId/cancel',
        data: {'cancelled_reason': cancelledReason},
      );

      return AppointmentModel.fromJson(
        Map<String, dynamic>.from(response.data as Map),
      );
    } on DioException {
      rethrow;
    }
  }

  String _formatDate(DateTime date) {
    final year = date.year.toString().padLeft(4, '0');

    final month = date.month.toString().padLeft(2, '0');

    final day = date.day.toString().padLeft(2, '0');

    return '$year-$month-$day';
  }

  String _normalizeTimeForApi(String value) {
    if (value.length == 5) {
      return '$value:00';
    }

    return value;
  }
}
