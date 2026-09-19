class ResetPasswordRequest {
  const ResetPasswordRequest({
    required this.resetToken,
    required this.newPassword,
    required this.confirmPassword,
  });

  final String resetToken;
  final String newPassword;
  final String confirmPassword;

  Map<String, dynamic> toJson() {
    return {
      'reset_token': resetToken,
      'new_password': newPassword,
      'confirm_password': confirmPassword,
    };
  }
}