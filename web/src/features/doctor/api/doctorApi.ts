import api from "../../../api/axios";

export type DoctorPreface =
  | "mr_doctor"
  | "female_doctor";

export type DoctorStatus =
  | "active"
  | "on_leave"
  | "resigned"
  | "retired"
  | "inactive";

export interface DoctorCreateRequest {
  employee_id: string;
  password: string;
  profile_image_url: string | null;
  preface: DoctorPreface;
  first_name: string;
  last_name: string;
  license_number: string;
  phone_number: string;
  email: string;
  department_id: string;
  specialization_ids: string[];
}

export interface Department {
  id: string;
  name: string;
  description: string | null;
  status: string;
}

export interface Specialization {
  id: string;
  name: string;
  description: string | null;
  status: string;
}

export interface DoctorResponse {
  id: string;
  profile_image_url: string | null;
  preface: DoctorPreface;
  first_name: string;
  last_name: string;
  license_number: string;
  phone_number: string;
  email: string;
  status: DoctorStatus;
  department: Department;
  specializations: Specialization[];
  created_at: string;
  updated_at: string;
}

export const createDoctor = async (
  data: DoctorCreateRequest,
): Promise<DoctorResponse> => {
  const response = await api.post<DoctorResponse>(
    "/doctors",
    data,
  );

  return response.data;
};

export interface GetDoctorsParams {
  status?: DoctorStatus;
  search?: string;
}

export const getDoctors = async (
  params?: GetDoctorsParams,
): Promise<DoctorResponse[]> => {
  const response = await api.get<DoctorResponse[]>(
    "/doctors",
    {
      params,
    },
  );

  return response.data;
};

export interface DoctorUpdateRequest {
  profile_image_url?: string | null;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  email?: string;
  status?: DoctorStatus;
  department_id?: string;
  specialization_ids?: string[];
}

export const updateDoctor = async (
  doctorId: string,
  data: DoctorUpdateRequest,
): Promise<DoctorResponse> => {
  const response = await api.patch<DoctorResponse>(
    `/doctors/${doctorId}`,
    data,
  );

  return response.data;
};

export const getDoctorById = async (
  doctorId: string,
): Promise<DoctorResponse> => {
  const response = await api.get<DoctorResponse>(
    `/doctors/${doctorId}`,
  );

  return response.data;
};

export const deleteDoctor = async (
  doctorId: string,
  password: string,
): Promise<DoctorResponse> => {
  const response = await api.delete<DoctorResponse>(
    `/doctors/${doctorId}`,
    {
      data: {
        password,
      },
    },
  );

  return response.data;
};

export const reactivateDoctor = async (
  doctorId: string,
  password: string,
): Promise<DoctorResponse> => {
  const response = await api.post<DoctorResponse>(
    "/reactivate",
    {
      target_type: "doctor",
      target_id: doctorId,
      password,
    },
  );

  return response.data;
};

export interface DoctorImageUploadResponse {
  image_url: string;
}
export const uploadDoctorImage = async (
  file: File,
): Promise<DoctorImageUploadResponse> => {
  const formData = new FormData();

  formData.append("file", file);

  const response =
    await api.post<DoctorImageUploadResponse>(
      "/uploads/doctor-image",
      formData,
    );

  return response.data;
};