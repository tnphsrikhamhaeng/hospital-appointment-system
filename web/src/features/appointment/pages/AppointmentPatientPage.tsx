import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  getAppointmentPatient,
  type AppointmentPatient,
} from "../api/appointmentApi";

function AppointmentPatientPage() {
  const [searchParams] = useSearchParams();
  const appointmentId = searchParams.get("appointment_id");

  const [patient, setPatient] = useState<AppointmentPatient | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const loadPatient = async () => {
      if (!appointmentId) {
        setErrorMessage("ไม่พบรหัสนัดหมาย");
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setErrorMessage("");

      try {
        const data = await getAppointmentPatient(appointmentId);
        setPatient(data);
      } catch (error: unknown) {
        if (
          typeof error === "object" &&
          error !== null &&
          "response" in error
        ) {
          const response = (
            error as {
              response?: {
                data?: {
                  detail?: string;
                };
              };
            }
          ).response;

          setErrorMessage(
            response?.data?.detail ?? "ไม่สามารถโหลดข้อมูลผู้ป่วยได้",
          );
        } else {
          setErrorMessage("ไม่สามารถโหลดข้อมูลผู้ป่วยได้");
        }
      } finally {
        setIsLoading(false);
      }
    };

    void loadPatient();
  }, [appointmentId]);

  if (isLoading) {
    return <div>กำลังโหลดข้อมูลผู้ป่วย...</div>;
  }

  if (errorMessage) {
    return <div role="alert">{errorMessage}</div>;
  }

  if (!patient) {
    return <div role="alert">ไม่พบข้อมูลผู้ป่วย</div>;
  }

  return (
    <main>
      <h1>ข้อมูลผู้ป่วย</h1>

      <p>
        ชื่อ: {patient.first_name} {patient.last_name}
      </p>

      <p>Username: {patient.username}</p>

      <p>Email: {patient.email}</p>

      <p>เบอร์โทร: {patient.phone_number}</p>

      <p>เพศ: {patient.gender ?? "-"}</p>

      <p>วันเกิด: {patient.date_of_birth ?? "-"}</p>
    </main>
  );
}

export default AppointmentPatientPage;