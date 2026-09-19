import '../models/medical_record_model.dart';
import '../services/medical_record_api_service.dart';

class MedicalRecordRepository {
  MedicalRecordRepository({
    required MedicalRecordApiService medicalRecordApiService,
  }) : _medicalRecordApiService = medicalRecordApiService;

  final MedicalRecordApiService _medicalRecordApiService;

  Future<List<MedicalRecordModel>> getMedicalRecords() {
    return _medicalRecordApiService.getMedicalRecords();
  }

  Future<MedicalRecordModel> getMedicalRecordById({
    required String medicalRecordId,
  }) {
    return _medicalRecordApiService.getMedicalRecordById(
      medicalRecordId: medicalRecordId,
    );
  }
}