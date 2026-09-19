import api from "../../../api/axios";

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export const changePassword = async (
  data: ChangePasswordRequest,
): Promise<void> => {
  await api.patch("/profile/password", data);
};