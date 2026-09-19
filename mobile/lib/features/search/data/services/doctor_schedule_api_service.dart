import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../models/doctor_schedule_model.dart';

class DoctorScheduleApiService {
  DoctorScheduleApiService({
    required ApiClient apiClient,
  }) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<List<DoctorScheduleModel>> getSchedulesByDoctor({
    required String doctorId,
  }) async {
    try {
      final response = await _apiClient.dio.get(
        '/doctor-schedule-templates/doctor/$doctorId',
      );

      final data = response.data as List<dynamic>;

      return data
          .map(
            (item) => DoctorScheduleModel.fromJson(
              item as Map<String, dynamic>,
            ),
          )
          .toList();
    } on DioException {
      rethrow;
    }
  }
}