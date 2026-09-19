import '../../../../core/storage/token_storage.dart';
import '../models/login_request.dart';
import '../models/login_response.dart';
import '../models/register_request.dart';
import '../services/auth_api_service.dart';

import '../models/forgot_password_request.dart';
import '../models/reset_password_request.dart';

class AuthRepository {
  AuthRepository({
    required AuthApiService authApiService,
    required TokenStorage tokenStorage,
  }) : _authApiService = authApiService,
       _tokenStorage = tokenStorage;

  final AuthApiService _authApiService;
  final TokenStorage _tokenStorage;

  Future<LoginResponse> login(LoginRequest request) async {
    final response = await _authApiService.login(request);

    await _tokenStorage.saveAccessToken(response.accessToken);

    return response;
  }

  Future<Map<String, dynamic>> register(RegisterRequest request) async {
    return _authApiService.register(request);
  }

  Future<Map<String, dynamic>> forgotPassword(
    ForgotPasswordRequest request,
  ) async {
    return _authApiService.forgotPassword(request);
  }

  Future<void> resetPassword(ResetPasswordRequest request) async {
    await _authApiService.resetPassword(request);
  }

  Future<void> logout() async {
    await _tokenStorage.clearAccessToken();
  }

  Future<bool> isAuthenticated() async {
    return _tokenStorage.hasAccessToken();
  }
}
