import '../models/doctor_schedule_model.dart';
import '../services/doctor_schedule_api_service.dart';

class DoctorScheduleRepository {
  DoctorScheduleRepository({
    required DoctorScheduleApiService doctorScheduleApiService,
  }) : _doctorScheduleApiService = doctorScheduleApiService;

  final DoctorScheduleApiService _doctorScheduleApiService;

  Future<List<DoctorScheduleModel>> getSchedulesByDoctor({
    required String doctorId,
  }) async {
    return _doctorScheduleApiService.getSchedulesByDoctor(
      doctorId: doctorId,
    );
  }
}