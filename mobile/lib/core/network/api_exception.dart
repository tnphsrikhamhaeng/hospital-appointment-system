class ApiException implements Exception {
  const ApiException({
    required this.message,
    this.statusCode,
    this.data,
  });

  final String message;
  final int? statusCode;
  final dynamic data;

  factory ApiException.fromStatusCode({
    required int statusCode,
    dynamic data,
  }) {
    return ApiException(
      statusCode: statusCode,
      data: data,
      message: _messageFromStatusCode(statusCode),
    );
  }

  static String _messageFromStatusCode(int statusCode) {
    switch (statusCode) {
      case 400:
        return 'ข้อมูลที่ส่งไปไม่ถูกต้อง';
      case 401:
        return 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง';
      case 403:
        return 'ไม่มีสิทธิ์เข้าถึงข้อมูลนี้';
      case 404:
        return 'ไม่พบข้อมูลที่ร้องขอ';
      case 409:
        return 'ข้อมูลนี้มีอยู่แล้วหรือเกิดความขัดแย้ง';
      case 422:
        return 'ข้อมูลไม่ผ่านการตรวจสอบ';
      case 500:
        return 'เกิดข้อผิดพลาดที่เซิร์ฟเวอร์';
      default:
        return 'เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์';
    }
  }

  @override
  String toString() {
    return 'ApiException('
        'statusCode: $statusCode, '
        'message: $message'
        ')';
  }
}