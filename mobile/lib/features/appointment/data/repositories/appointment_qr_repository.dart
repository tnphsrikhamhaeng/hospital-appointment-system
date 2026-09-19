import '../models/appointment_qr_model.dart';
import '../services/appointment_qr_api_service.dart';

class AppointmentQrRepository {
  AppointmentQrRepository({
    required AppointmentQrApiService apiService,
  }) : _apiService = apiService;

  final AppointmentQrApiService _apiService;

  Future<AppointmentQrModel> getQr({
    required String appointmentId,
  }) {
    return _apiService.getQr(
      appointmentId: appointmentId,
    );
  }
}