import '../models/department_model.dart';
import '../services/department_api_service.dart';

class DepartmentRepository {
  DepartmentRepository({required DepartmentApiService departmentApiService})
    : _departmentApiService = departmentApiService;

  final DepartmentApiService _departmentApiService;

  Future<DepartmentModel> getDepartmentById({
    required String departmentId,
  }) async {
    return _departmentApiService.getDepartmentById(departmentId: departmentId);
  }

  Future<List<DepartmentModel>> getDepartments() async {
    return _departmentApiService.getDepartments();
  }
}
