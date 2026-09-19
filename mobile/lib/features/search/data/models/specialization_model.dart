enum SpecializationStatus {
  active,
  inactive,
}

class SpecializationModel {
  const SpecializationModel({
    required this.id,
    required this.name,
    required this.description,
    required this.departmentId,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
  });

  final String id;
  final String name;
  final String? description;
  final String departmentId;
  final SpecializationStatus status;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory SpecializationModel.fromJson(Map<String, dynamic> json) {
    return SpecializationModel(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      departmentId: json['department_id'] as String,
      status: _parseStatus(json['status'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  static SpecializationStatus _parseStatus(String value) {
    switch (value) {
      case 'active':
        return SpecializationStatus.active;
      case 'inactive':
        return SpecializationStatus.inactive;
      default:
        throw FormatException(
          'Unknown specialization status: $value',
        );
    }
  }
}