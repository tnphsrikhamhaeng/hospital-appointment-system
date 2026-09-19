import api from "../../../api/axios";

export type SpecializationStatus = "active" | "inactive";

export interface SpecializationResponse {
  id: string;
  name: string;
  description: string | null;
  department_id: string;
  status: SpecializationStatus;
  created_at: string;
  updated_at: string;
}

export interface GetSpecializationsParams {
  status?: SpecializationStatus;
  search?: string;
}

export interface SpecializationCreateRequest {
  name: string;
  description: string | null;
  department_id: string;
}

export interface SpecializationUpdateRequest {
  name?: string;
  description?: string | null;
  department_id?: string;
  status?: SpecializationStatus;
}

export interface ReactivateSpecializationRequest {
  target_type: "specialization";
  target_id: string;
  password: string;
}

export const getSpecializations = async (
  params?: GetSpecializationsParams,
): Promise<SpecializationResponse[]> => {
  const response = await api.get<SpecializationResponse[]>(
    "/specializations",
    {
      params,
    },
  );

  return response.data;
};

export const createSpecialization = async (
  data: SpecializationCreateRequest,
): Promise<SpecializationResponse> => {
  const response = await api.post<SpecializationResponse>(
    "/specializations",
    data,
  );

  return response.data;
};

export const updateSpecialization = async (
  specializationId: string,
  data: SpecializationUpdateRequest,
): Promise<SpecializationResponse> => {
  const response = await api.patch<SpecializationResponse>(
    `/specializations/${specializationId}`,
    data,
  );

  return response.data;
};

export const deleteSpecialization = async (
  specializationId: string,
): Promise<SpecializationResponse> => {
  const response = await api.delete<SpecializationResponse>(
    `/specializations/${specializationId}`,
  );

  return response.data;
};

export const reactivateSpecialization = async (
  specializationId: string,
  password: string,
): Promise<SpecializationResponse> => {
  const response = await api.post<SpecializationResponse>(
    "/reactivate",
    {
      target_type: "specialization",
      target_id: specializationId,
      password,
    },
  );

  return response.data;
};