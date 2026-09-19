import '../../data/models/login_request.dart';
import '../../data/models/login_response.dart';
import '../../data/models/register_request.dart';
import '../../data/repositories/auth_repository.dart';

enum AuthStatus {
  idle,
  loading,
  authenticated,
  registered,
  error,
}

class AuthController {
  AuthController({
    required AuthRepository authRepository,
  }) : _authRepository = authRepository;

  final AuthRepository _authRepository;

  AuthStatus _status = AuthStatus.idle;
  String? _errorMessage;

  AuthStatus get status => _status;
  String? get errorMessage => _errorMessage;

  Future<LoginResponse?> login({
    required String username,
    required String password,
  }) async {
    _setLoading();

    try {
      final response = await _authRepository.login(
        LoginRequest(
          username: username,
          password: password,
        ),
      );

      _status = AuthStatus.authenticated;
      _errorMessage = null;

      return response;
    } catch (error) {
      _setError(error);
      return null;
    }
  }

  Future<bool> register(RegisterRequest request) async {
    _setLoading();

    try {
      await _authRepository.register(request);

      _status = AuthStatus.registered;
      _errorMessage = null;

      return true;
    } catch (error) {
      _setError(error);
      return false;
    }
  }

  Future<void> logout() async {
    await _authRepository.logout();

    _status = AuthStatus.idle;
    _errorMessage = null;
  }

  Future<bool> isAuthenticated() async {
    return _authRepository.isAuthenticated();
  }

  void reset() {
    _status = AuthStatus.idle;
    _errorMessage = null;
  }

  void _setLoading() {
    _status = AuthStatus.loading;
    _errorMessage = null;
  }

  void _setError(Object error) {
    _status = AuthStatus.error;
    _errorMessage = error.toString();
  }
}