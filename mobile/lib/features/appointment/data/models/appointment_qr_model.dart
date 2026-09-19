class AppointmentQrModel {
  final String token;
  final DateTime expiredAt;

  const AppointmentQrModel({
    required this.token,
    required this.expiredAt,
  });

  factory AppointmentQrModel.fromJson(Map<String, dynamic> json) {
    return AppointmentQrModel(
      token: json['token'] as String,
      expiredAt: DateTime.parse(
        json['expired_at'] as String,
      ),
    );
  }
}