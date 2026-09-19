import api from "../../../api/axios";

export type Weekday =
  | "monday"
  | "tuesday"
  | "wednesday"
  | "thursday"
  | "friday"
  | "saturday"
  | "sunday";

export interface DoctorScheduleTemplate {
  id: string;
  doctor_id: string;
  weekday: Weekday;
  start_time: string;
  end_time: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DoctorScheduleTemplateCreateRequest {
  doctor_id: string;
  weekday: Weekday;
  start_time: string;
  end_time: string;
}

export interface DoctorScheduleTemplateUpdateRequest {
  weekday?: Weekday;
  start_time?: string;
  end_time?: string;
  is_active?: boolean;
}

export const getMyDoctorSchedule = async (): Promise<
  DoctorScheduleTemplate[]
> => {
  const response = await api.get<DoctorScheduleTemplate[]>(
    "/doctor-schedule-templates/my",
  );

  return response.data;
};

export const getDoctorSchedule = async (
  doctorId: string,
): Promise<DoctorScheduleTemplate[]> => {
  const response = await api.get<DoctorScheduleTemplate[]>(
    `/doctor-schedule-templates/doctor/${doctorId}`,
  );

  return response.data;
};

export const createDoctorSchedule = async (
  data: DoctorScheduleTemplateCreateRequest,
): Promise<DoctorScheduleTemplate> => {
  const response = await api.post<DoctorScheduleTemplate>(
    "/doctor-schedule-templates",
    data,
  );

  return response.data;
};

export const updateDoctorSchedule = async (
  templateId: string,
  data: DoctorScheduleTemplateUpdateRequest,
): Promise<DoctorScheduleTemplate> => {
  const response = await api.patch<DoctorScheduleTemplate>(
    `/doctor-schedule-templates/${templateId}`,
    data,
  );

  return response.data;
};

export const deleteDoctorSchedule = async (
  templateId: string,
): Promise<void> => {
  await api.delete(
    `/doctor-schedule-templates/${templateId}`,
  );
};