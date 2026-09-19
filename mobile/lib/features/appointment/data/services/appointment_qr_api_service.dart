import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../models/appointment_qr_model.dart';

class AppointmentQrApiService {
  AppointmentQrApiService({
    required ApiClient apiClient,
  }) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<AppointmentQrModel> getQr({
    required String appointmentId,
  }) async {
    try {
      final response = await _apiClient.dio.get(
        '/appointment-qr/$appointmentId',
      );

      return AppointmentQrModel.fromJson(
        response.data as Map<String, dynamic>,
      );
    } on DioException {
      rethrow;
    }
  }
}