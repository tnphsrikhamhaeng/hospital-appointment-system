import api from "../../../api/axios";

export interface StaffCheckInRequest {
  token: string;
}

export interface StaffCheckInResponse {
  message: string;
}

export interface StaffCheckInPreviewResponse {
  appointment_id: string;
  patient_name: string;
  appointment_date: string;
  start_time: string;
  end_time: string;
  doctor_name: string;
  department_name: string;
}

export const staffCheckInPreview = async (
  data: StaffCheckInRequest,
): Promise<StaffCheckInPreviewResponse> => {
  const response =
    await api.post<StaffCheckInPreviewResponse>(
      "/appointment-qr/staff-check-in-preview",
      data,
    );

  return response.data;
};

export const staffCheckIn = async (
  data: StaffCheckInRequest,
): Promise<StaffCheckInResponse> => {
  const response = await api.post<StaffCheckInResponse>(
    "/appointment-qr/staff-check-in",
    data,
  );

  return response.data;
};