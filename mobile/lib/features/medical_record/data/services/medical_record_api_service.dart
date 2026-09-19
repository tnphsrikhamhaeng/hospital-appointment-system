import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../models/medical_record_model.dart';

class MedicalRecordApiService {
  MedicalRecordApiService({
    required ApiClient apiClient,
  }) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<List<MedicalRecordModel>>
      getMedicalRecords() async {
    try {
      final response = await _apiClient.dio.get(
        '/medical-records',
      );

      final data =
          response.data as List<dynamic>;

      return data
          .map(
            (item) =>
                MedicalRecordModel.fromJson(
              item as Map<String, dynamic>,
            ),
          )
          .toList();
    } on DioException {
      rethrow;
    }
  }

  Future<MedicalRecordModel>
      getMedicalRecordById({
    required String medicalRecordId,
  }) async {
    try {
      final response = await _apiClient.dio.get(
        '/medical-records/$medicalRecordId',
      );

      return MedicalRecordModel.fromJson(
        Map<String, dynamic>.from(
          response.data as Map,
        ),
      );
    } on DioException {
      rethrow;
    }
  }
}