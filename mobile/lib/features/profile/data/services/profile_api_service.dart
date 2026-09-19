import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../models/profile_model.dart';

class ProfileApiService {
  ProfileApiService({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<ProfileModel> updateProfile({
  required String firstName,
  required String lastName,
  required String phoneNumber,
  required String email,
}) async {
  try {
    final response = await _apiClient.dio.patch(
      '/profile',
      data: {
        'first_name': firstName,
        'last_name': lastName,
        'phone_number': phoneNumber,
        'email': email,
      },
    );

    return ProfileModel.fromJson(
      response.data as Map<String, dynamic>,
    );
  } on DioException {
    rethrow;
  }
}

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    try {
      await _apiClient.dio.patch(
        '/profile/password',
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
          'confirm_password': confirmPassword,
        },
      );
    } on DioException {
      rethrow;
    }
  }

  Future<ProfileModel> getProfile() async {
    try {
      final response = await _apiClient.dio.get('/profile');

      return ProfileModel.fromJson(response.data as Map<String, dynamic>);
    } on DioException {
      rethrow;
    }
  }
}
