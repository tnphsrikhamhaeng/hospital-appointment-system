import '../models/doctor_model.dart';
import '../services/doctor_api_service.dart';

class DoctorRepository {
  DoctorRepository({
    required DoctorApiService doctorApiService,
  }) : _doctorApiService = doctorApiService;

  final DoctorApiService _doctorApiService;

  Future<DoctorModel> getDoctorById({
    required String doctorId,
  }) async {
    return _doctorApiService.getDoctorById(
      doctorId: doctorId,
    );
  }

  Future<List<DoctorModel>> getDoctorsByDepartment({
    required String departmentId,
  }) async {
    return _doctorApiService.getDoctorsByDepartment(
      departmentId: departmentId,
    );
  }
}