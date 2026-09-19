import '../models/appointment_model.dart';
import '../services/appointment_api_service.dart';
import '../models/doctor_schedule_appointment_model.dart';

class AppointmentRepository {
  AppointmentRepository({required AppointmentApiService appointmentApiService})
    : _appointmentApiService = appointmentApiService;

  final AppointmentApiService _appointmentApiService;

  Future<AppointmentModel> createAppointment({
    required String patientId,
    required String doctorId,
    required DateTime appointmentDate,
    required String startTime,
    String? reason,
  }) {
    return _appointmentApiService.createAppointment(
      patientId: patientId,
      doctorId: doctorId,
      appointmentDate: appointmentDate,
      startTime: startTime,
      reason: reason,
    );
  }

  Future<AppointmentModel> getAppointmentById({required String appointmentId}) {
    return _appointmentApiService.getAppointmentById(
      appointmentId: appointmentId,
    );
  }

  Future<List<AppointmentModel>> getPatientAppointments({
    required String patientId,
  }) {
    return _appointmentApiService.getPatientAppointments(patientId: patientId);
  }

  Future<List<DoctorScheduleAppointmentModel>> getDoctorSchedule({
    required String doctorId,
    required DateTime appointmentDate,
  }) {
    return _appointmentApiService.getDoctorSchedule(
      doctorId: doctorId,
      appointmentDate: appointmentDate,
    );
  }

  Future<AppointmentModel> rescheduleAppointment({
    required String appointmentId,
    required DateTime appointmentDate,
    required String startTime,
  }) {
    return _appointmentApiService.rescheduleAppointment(
      appointmentId: appointmentId,
      appointmentDate: appointmentDate,
      startTime: startTime,
    );
  }

  Future<AppointmentModel> cancelAppointment({
    required String appointmentId,
    required String cancelledReason,
  }) {
    return _appointmentApiService.cancelAppointment(
      appointmentId: appointmentId,
      cancelledReason: cancelledReason,
    );
  }
}
