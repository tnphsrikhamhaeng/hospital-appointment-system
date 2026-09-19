import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../models/department_model.dart';

class DepartmentApiService {
  DepartmentApiService({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<DepartmentModel> getDepartmentById({
    required String departmentId,
  }) async {
    try {
      final response = await _apiClient.dio.get('/departments/$departmentId');

      return DepartmentModel.fromJson(response.data as Map<String, dynamic>);
    } on DioException {
      rethrow;
    }
  }

  Future<List<DepartmentModel>> getDepartments() async {
    try {
      final response = await _apiClient.dio.get('/departments');

      final data = response.data as List<dynamic>;

      return data
          .map((item) => DepartmentModel.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException {
      rethrow;
    }
  }

  
}
