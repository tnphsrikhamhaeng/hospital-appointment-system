import api from "../../../api/axios";

export type DepartmentStatus = "active" | "inactive";

export interface DepartmentResponse {
  id: string;
  name: string;
  description: string | null;
  image_url: string | null;
  slot_duration_minutes: number;
  status: DepartmentStatus;
  created_at: string;
  updated_at: string;
}

export interface DepartmentImageUploadResponse {
  image_url: string;
}

export interface GetDepartmentsParams {
  status?: DepartmentStatus;
  search?: string;
}

export interface DepartmentCreateRequest {
  name: string;
  description: string | null;
  image_url: string | null;
  slot_duration_minutes: number;
}

export interface DepartmentUpdateRequest {
  name?: string;
  description?: string | null;
  image_url?: string | null;
  slot_duration_minutes?: number;
  status?: DepartmentStatus;
}

export interface ReactivateRequest {
  target_type: "department";
  target_id: string;
  password: string;
}

export const getDepartments = async (
  params?: GetDepartmentsParams,
): Promise<DepartmentResponse[]> => {
  const response = await api.get<DepartmentResponse[]>(
    "/departments",
    {
      params,
    },
  );

  return response.data;
};

export const createDepartment = async (
  data: DepartmentCreateRequest,
): Promise<DepartmentResponse> => {
  const response = await api.post<DepartmentResponse>(
    "/departments",
    data,
  );

  return response.data;
};

export const updateDepartment = async (
  departmentId: string,
  data: DepartmentUpdateRequest,
): Promise<DepartmentResponse> => {
  const response = await api.patch<DepartmentResponse>(
    `/departments/${departmentId}`,
    data,
  );

  return response.data;
};

export const deleteDepartment = async (
  departmentId: string,
  password: string,
): Promise<DepartmentResponse> => {
  const response = await api.delete<DepartmentResponse>(
    `/departments/${departmentId}`,
    {
      data: {
        password,
      },
    },
  );

  return response.data;
};

export const reactivateDepartment = async (
  departmentId: string,
  password: string,
): Promise<DepartmentResponse> => {
  const response = await api.post<DepartmentResponse>(
    "/reactivate",
    {
      target_type: "department",
      target_id: departmentId,
      password,
    },
  );

  return response.data;
};

export const uploadDepartmentImage = async (
  file: File,
): Promise<DepartmentImageUploadResponse> => {
  const formData = new FormData();

  formData.append("file", file);

  const response =
    await api.post<DepartmentImageUploadResponse>(
      "/uploads/department-image",
      formData,
    );

  return response.data;
};