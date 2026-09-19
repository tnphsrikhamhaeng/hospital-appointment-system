import api from "../../../api/axios";

export interface StaffCreateRequest {
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  email: string;
}

export interface StaffUpdateRequest {
  username: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  email: string;
}

export interface StaffDeactivateRequest {
  password: string;
}

export interface StaffResponse {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  gender: string | null;
  date_of_birth: string | null;
  role: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export const createStaff = async (
  data: StaffCreateRequest,
): Promise<StaffResponse> => {
  const response = await api.post<StaffResponse>("/staff", data);
  return response.data;
};

export const getStaff = async (
  search?: string,
  status?: string,
): Promise<StaffResponse[]> => {
  const response = await api.get<StaffResponse[]>("/staff", {
    params: {
      ...(search ? { search } : {}),
      ...(status ? { status } : {}),
    },
  });

  return response.data;
};

export const updateStaff = async (
  staffId: string,
  data: StaffUpdateRequest,
): Promise<StaffResponse> => {
  const response = await api.put<StaffResponse>(
    `/staff/${staffId}`,
    data,
  );

  return response.data;
};

export const deactivateStaff = async (
  staffId: string,
  password: string,
): Promise<StaffResponse> => {
  const response = await api.delete<StaffResponse>(
    `/staff/${staffId}`,
    {
      data: {
        password,
      },
    },
  );

  return response.data;
};

export const reactivateStaff = async (
  staffId: string,
  password: string,
): Promise<StaffResponse> => {
  const response = await api.post<StaffResponse>(
    "/reactivate",
    {
      target_type: "staff",
      target_id: staffId,
      password,
    },
  );

  return response.data;
};