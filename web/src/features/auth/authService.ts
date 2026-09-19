import {
  getProfile,
  type ProfileResponse,
  type UserRole,
} from "./api/profileApi";
import {
  staffLogin,
  type LoginRequest,
} from "./api/authApi";

const ACCESS_TOKEN_KEY = "access_token";

export const login = async (
  data: LoginRequest,
): Promise<ProfileResponse> => {
  const response = await staffLogin(data);

  sessionStorage.setItem(
    ACCESS_TOKEN_KEY,
    response.access_token,
  );

  return getProfile();
};

export const getCurrentUser = async (): Promise<ProfileResponse> => {
  return getProfile();
};

export const getCurrentRole = async (): Promise<UserRole> => {
  const profile = await getProfile();

  return profile.role;
};

export const logout = (): void => {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
};

export const isAuthenticated = (): boolean => {
  return Boolean(
    sessionStorage.getItem(ACCESS_TOKEN_KEY),
  );
};