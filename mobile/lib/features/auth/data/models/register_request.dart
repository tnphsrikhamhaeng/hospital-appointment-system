class RegisterRequest {
  const RegisterRequest({
    required this.username,
    required this.firstName,
    required this.lastName,
    required this.dateOfBirth,
    required this.gender,
    required this.phoneNumber,
    required this.email,
    required this.password,
    required this.confirmPassword,
  });

  final String username;
  final String firstName;
  final String lastName;
  final String dateOfBirth;
  final String gender;
  final String phoneNumber;
  final String email;
  final String password;
  final String confirmPassword;

  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'first_name': firstName,
      'last_name': lastName,
      'date_of_birth': dateOfBirth,
      'gender': gender,
      'phone_number': phoneNumber,
      'email': email,
      'password': password,
      'confirm_password': confirmPassword,
    };
  }
}