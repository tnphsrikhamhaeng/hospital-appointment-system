import api from "../../../api/axios";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const staffLogin = async (
  data: LoginRequest,
): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>(
    "/auth/staff-login",
    data,
  );

  return response.data;
};

export const logout = () => {
  sessionStorage.removeItem("access_token");
};