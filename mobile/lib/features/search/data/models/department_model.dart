enum DepartmentStatus {
  active,
  inactive,
}

class DepartmentModel {
  const DepartmentModel({
    required this.id,
    required this.name,
    required this.description,
    required this.imageUrl,
    required this.slotDurationMinutes,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
  });

  final String id;
  final String name;
  final String? description;
  final String? imageUrl;
  final int slotDurationMinutes;
  final DepartmentStatus status;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory DepartmentModel.fromJson(Map<String, dynamic> json) {
    return DepartmentModel(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String?,
      slotDurationMinutes:
          json['slot_duration_minutes'] as int,
      status: _parseStatus(json['status'] as String),
      createdAt: DateTime.parse(
        json['created_at'] as String,
      ),
      updatedAt: DateTime.parse(
        json['updated_at'] as String,
      ),
    );
  }

  static DepartmentStatus _parseStatus(String value) {
    switch (value) {
      case 'active':
        return DepartmentStatus.active;
      case 'inactive':
        return DepartmentStatus.inactive;
      default:
        throw FormatException(
          'Unknown department status: $value',
        );
    }
  }
}