import api from "../../../api/axios";

export interface MedicalRecordCreateRequest {
  appointment_id: string;
  chief_complaint: string;
  present_illness: string | null;
  physical_examination: string | null;
  diagnosis: string;
  treatment: string | null;
  recommendation: string | null;
  note: string | null;
}

export interface MedicalRecord {
  id: string;
  appointment_id: string;
  patient_id: string;
  doctor_id: string;
  chief_complaint: string;
  present_illness: string | null;
  physical_examination: string | null;
  diagnosis: string;
  treatment: string | null;
  recommendation: string | null;
  note: string | null;
  created_at: string;
  updated_at: string;
}

export const createMedicalRecord = async (
  data: MedicalRecordCreateRequest,
): Promise<MedicalRecord> => {
  const response = await api.post<MedicalRecord>(
    "/medical-records",
    data,
  );

  return response.data;
};

export const getMedicalRecord = async (
  medicalRecordId: string,
): Promise<MedicalRecord> => {
  const response = await api.get<MedicalRecord>(
    `/medical-records/${medicalRecordId}`,
  );

  return response.data;
};

export interface DoctorMedicalHistory {
  appointment_id: string;
  appointment_date: string;
  start_time: string;
  end_time: string;
  patient_id: string;
  patient_name: string;
  status: string;
  medical_record: MedicalRecord | null;
}

export interface GetDoctorMedicalHistoryParams {
  date_from?: string;
  date_to?: string;
}

export const getDoctorMedicalHistory = async (
  params?: GetDoctorMedicalHistoryParams,
): Promise<DoctorMedicalHistory[]> => {
  const response = await api.get<DoctorMedicalHistory[]>(
    "/medical-records/doctor/history",
    {
      params,
    },
  );

  return response.data;
};