import api from "../../../api/axios";

export type UserRole = "patient" | "doctor" | "hospital_staff";

export interface ProfileResponse {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  gender: string | null;
  date_of_birth: string | null;
  role: UserRole;
  status: string;
  created_at: string;
  updated_at: string;
}

export const getProfile = async (): Promise<ProfileResponse> => {
  const response = await api.get<ProfileResponse>("/profile");

  return response.data;
};