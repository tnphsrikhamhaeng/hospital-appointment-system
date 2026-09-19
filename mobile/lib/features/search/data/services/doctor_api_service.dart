import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../models/doctor_model.dart';

class DoctorApiService {
  DoctorApiService({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<DoctorModel> getDoctorById({required String doctorId}) async {
    try {
      final response = await _apiClient.dio.get('/doctors/$doctorId');

      return DoctorModel.fromJson(response.data as Map<String, dynamic>);
    } on DioException {
      rethrow;
    }
  }

 Future<List<DoctorModel>> getDoctorsByDepartment({
  required String departmentId,
}) async {
  try {
    final response = await _apiClient.dio.get(
      '/doctors',
      queryParameters: {
        'department_id': departmentId,
      },
    );

    final data = response.data as List<dynamic>;

    return data
        .map(
          (item) => DoctorModel.fromJson(
            item as Map<String, dynamic>,
          ),
        )
        .toList();
  } on DioException {
    rethrow;
  }
}
  
}
