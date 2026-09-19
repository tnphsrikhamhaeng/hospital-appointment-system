import '../services/profile_api_service.dart';
import '../models/profile_model.dart';

class ProfileRepository {
  ProfileRepository({required ProfileApiService profileApiService})
    : _profileApiService = profileApiService;

  final ProfileApiService _profileApiService;

  Future<ProfileModel> getProfile() async {
    return _profileApiService.getProfile();
  }

  Future<ProfileModel> updateProfile({
    required String firstName,
    required String lastName,
    required String phoneNumber,
    required String email,
  }) async {
    return _profileApiService.updateProfile(
      firstName: firstName,
      lastName: lastName,
      phoneNumber: phoneNumber,
      email: email,
    );
  }

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    await _profileApiService.changePassword(
      currentPassword: currentPassword,
      newPassword: newPassword,
      confirmPassword: confirmPassword,
    );
  }
}
