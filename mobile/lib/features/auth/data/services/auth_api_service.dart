import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/network/api_exception.dart';
import '../models/login_request.dart';
import '../models/login_response.dart';
import '../models/register_request.dart';

import '../models/forgot_password_request.dart';
import '../models/reset_password_request.dart';

class AuthApiService {
  AuthApiService({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<LoginResponse> login(LoginRequest request) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/login',
        data: request.toJson(),
      );

      return LoginResponse.fromJson(
        Map<String, dynamic>.from(response.data as Map),
      );
    } on DioException catch (error) {
      throw _toApiException(error);
    }
  }

  Future<Map<String, dynamic>> register(RegisterRequest request) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/register',
        data: request.toJson(),
      );

      return Map<String, dynamic>.from(response.data as Map);
    } on DioException catch (error) {
      throw _toApiException(error);
    }
  }

  Future<Map<String, dynamic>> forgotPassword(
    ForgotPasswordRequest request,
  ) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/forgot-password',
        data: request.toJson(),
      );

      return Map<String, dynamic>.from(response.data as Map);
    } on DioException catch (error) {
      throw _toApiException(error);
    }
  }

  Future<void> resetPassword(ResetPasswordRequest request) async {
    try {
      await _apiClient.dio.post('/auth/reset-password', data: request.toJson());
    } on DioException catch (error) {
      throw _toApiException(error);
    }
  }

  ApiException _toApiException(DioException error) {
    final response = error.response;

    if (response != null) {
      return ApiException.fromStatusCode(
        statusCode: response.statusCode ?? 500,
        data: response.data,
      );
    }

    return const ApiException(message: 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
  }
}
