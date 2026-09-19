import 'department_model.dart';
import 'specialization_model.dart';

enum DoctorPreface { mrDoctor, femaleDoctor }

enum DoctorStatus { active, onLeave, resigned, retired }

class DoctorModel {
  const DoctorModel({
    required this.id,
    required this.profileImageUrl,
    required this.preface,
    required this.firstName,
    required this.lastName,
    required this.licenseNumber,
    required this.phoneNumber,
    required this.email,
    required this.status,
    required this.department,
    required this.specializations,
    required this.createdAt,
    required this.updatedAt,
  });

  final String id;
  final String? profileImageUrl;
  final DoctorPreface preface;
  final String firstName;
  final String lastName;
  final String licenseNumber;
  final String phoneNumber;
  final String email;
  final DoctorStatus status;

  final DepartmentModel department;
  final List<SpecializationModel> specializations;

  final DateTime createdAt;
  final DateTime updatedAt;

  factory DoctorModel.fromJson(Map<String, dynamic> json) {
    return DoctorModel(
      id: json['id'] as String,
      profileImageUrl: json['profile_image_url'] as String?,
      preface: _parsePreface(json['preface'] as String),
      firstName: json['first_name'] as String,
      lastName: json['last_name'] as String,
      licenseNumber: json['license_number'] as String,
      phoneNumber: json['phone_number'] as String,
      email: json['email'] as String,
      status: _parseStatus(json['status'] as String),
      department: DepartmentModel.fromJson(
        json['department'] as Map<String, dynamic>,
      ),
      specializations: (json['specializations'] as List<dynamic>)
          .map(
            (item) =>
                SpecializationModel.fromJson(item as Map<String, dynamic>),
          )
          .toList(),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  static DoctorPreface _parsePreface(String value) {
    switch (value) {
      case 'mr_doctor':
        return DoctorPreface.mrDoctor;
      case 'female_doctor':
        return DoctorPreface.femaleDoctor;
      default:
        throw FormatException('Unknown doctor preface: $value');
    }
  }

  static DoctorStatus _parseStatus(String value) {
    switch (value) {
      case 'active':
        return DoctorStatus.active;
      case 'on_leave':
        return DoctorStatus.onLeave;
      case 'resigned':
        return DoctorStatus.resigned;
      case 'retired':
        return DoctorStatus.retired;
      default:
        throw FormatException('Unknown doctor status: $value');
    }
  }
}
