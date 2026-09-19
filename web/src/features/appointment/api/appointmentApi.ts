import api from "../../../api/axios";

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  department_id: string;
  appointment_date: string;
  start_time: string;
  end_time: string;
  reason: string | null;
  status: string;
  cancelled_reason: string | null;
  cancelled_at: string | null;
  confirmed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DoctorSchedule {
  id: string;
  patient_id: string;
  patient_name: string;
  appointment_date: string;
  start_time: string;
  end_time: string;
  status: string;
}

export const getMyAppointments = async (): Promise<Appointment[]> => {
  const response = await api.get<Appointment[]>("/appointments/my");

  return response.data;
};

export const getMySchedule = async (
  appointmentDate: string,
): Promise<DoctorSchedule[]> => {
  const response = await api.get<DoctorSchedule[]>(
    "/appointments/my/schedule",
    {
      params: {
        appointment_date: appointmentDate,
      },
    },
  );

  return response.data;
};

export interface UpdateAppointmentStatusRequest {
  status: string;
  room_number: string;
}

export const updateAppointmentStatus = async (
  appointmentId: string,
  data: UpdateAppointmentStatusRequest,
): Promise<Appointment> => {
  const response = await api.patch<Appointment>(
    `/appointments/${appointmentId}/status`,
    data,
  );

  return response.data;
};

export interface AppointmentPatient {
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

export const getAppointmentPatient = async (
  appointmentId: string,
): Promise<AppointmentPatient> => {
  const response = await api.get<AppointmentPatient>(
    `/appointments/${appointmentId}/patient`,
  );

  return response.data;
};