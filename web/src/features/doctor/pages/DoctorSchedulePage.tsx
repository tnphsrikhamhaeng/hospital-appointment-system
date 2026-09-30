import { useEffect, useState } from "react";
import {
  getMySchedule,
  type DoctorSchedule,
} from "../../appointment/api/appointmentApi";
import {
  getMyDoctorSchedule,
  type DoctorScheduleTemplate,
} from "../api/doctorScheduleApi";
import "./DoctorPage.css";
import "./DoctorSchedulePage.css";

const WEEKDAY_LABELS: Record<string, string> = {
  monday: "วันจันทร์",
  tuesday: "วันอังคาร",
  wednesday: "วันพุธ",
  thursday: "วันพฤหัสบดี",
  friday: "วันศุกร์",
  saturday: "วันเสาร์",
  sunday: "วันอาทิตย์",
};

function getTodayDate(): string {
  const today = new Date();

  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function formatTime(time: string): string {
  const [hour, minute] = time.split(":");

  return `${hour.padStart(2, "0")}:${minute.padStart(2, "0")}`;
}

function DoctorSchedulePage() {
  const formatThaiDate = () => {
    return new Intl.DateTimeFormat("th-TH", {
      day: "numeric",
      month: "long",
      year: "numeric",
    }).format(new Date());
  };

  const [appointmentDate, setAppointmentDate] = useState(getTodayDate());

  const [appointments, setAppointments] = useState<DoctorSchedule[]>([]);

  const [doctorSchedules, setDoctorSchedules] = useState<
    DoctorScheduleTemplate[]
  >([]);

  const [isLoading, setIsLoading] = useState(true);
  const [isScheduleLoading, setIsScheduleLoading] = useState(true);

  const [errorMessage, setErrorMessage] = useState("");
  const [scheduleErrorMessage, setScheduleErrorMessage] = useState("");

  useEffect(() => {
    const loadAppointmentSchedule = async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const data = await getMySchedule(appointmentDate);
        setAppointments(data);
      } catch {
        setErrorMessage("ไม่สามารถโหลดตารางนัดหมายได้");
        setAppointments([]);
      } finally {
        setIsLoading(false);
      }
    };

    void loadAppointmentSchedule();
  }, [appointmentDate]);

  useEffect(() => {
    const loadDoctorSchedule = async () => {
      setIsScheduleLoading(true);
      setScheduleErrorMessage("");

      try {
        const data = await getMyDoctorSchedule();

        const activeSchedules = data
          .filter((schedule) => schedule.is_active)
          .sort((a, b) => {
            const weekdayOrder: Record<string, number> = {
              monday: 1,
              tuesday: 2,
              wednesday: 3,
              thursday: 4,
              friday: 5,
              saturday: 6,
              sunday: 7,
            };

            return weekdayOrder[a.weekday] - weekdayOrder[b.weekday];
          });

        setDoctorSchedules(activeSchedules);
      } catch {
        setScheduleErrorMessage("ไม่สามารถโหลดวันและเวลาออกตรวจได้");
        setDoctorSchedules([]);
      } finally {
        setIsScheduleLoading(false);
      }
    };

    void loadDoctorSchedule();
  }, []);

  return (
    <section className="doctor-content">
      <header className="doctor-schedule-header">
        <div>
          <span className="page-eyebrow">CareFlow Hospital System</span>

          <h1>ตารางนัดหมาย</h1>

          <p>ตรวจสอบวันและเวลาออกตรวจ และรายการนัดหมายของคุณ</p>
        </div>

        <div className="doctor-header-right">
          <div className="today-date">
            <span>วันนี้</span>

            <strong>{formatThaiDate()}</strong>
          </div>
        </div>
      </header>

      <section className="doctor-schedule-card">
        <div className="doctor-schedule-card-header">
          <div>
            <h2>วันและเวลาออกตรวจ</h2>

            <p>วันและเวลาที่คุณมีตารางออกตรวจ</p>
          </div>
        </div>

        {isScheduleLoading && (
          <div className="doctor-schedule-state">
            <p>กำลังโหลดวันและเวลาออกตรวจ...</p>
          </div>
        )}

        {!isScheduleLoading && scheduleErrorMessage && (
          <div className="doctor-schedule-state doctor-schedule-state-error">
            <p role="alert">{scheduleErrorMessage}</p>
          </div>
        )}

        {!isScheduleLoading &&
          !scheduleErrorMessage &&
          doctorSchedules.length === 0 && (
            <div className="doctor-schedule-state">
              <p>ไม่พบข้อมูลวันและเวลาออกตรวจ</p>
            </div>
          )}

        {!isScheduleLoading &&
          !scheduleErrorMessage &&
          doctorSchedules.length > 0 && (
            <div className="doctor-clinic-schedule-list">
              {doctorSchedules.map((schedule) => (
                <article
                  className="doctor-clinic-schedule-item"
                  key={schedule.id}
                >
                  <div className="doctor-clinic-day">
                    {WEEKDAY_LABELS[schedule.weekday] ?? schedule.weekday}
                  </div>

                  <div className="doctor-clinic-time">
                    {formatTime(schedule.start_time)} -{" "}
                    {formatTime(schedule.end_time)} น.
                  </div>
                </article>
              ))}
            </div>
          )}
      </section>

      <section className="doctor-schedule-card">
        <div className="doctor-schedule-card-header">
          <div>
            <h2>รายการนัดหมาย</h2>

            <p>รายการนัดหมายตามวันที่เลือก</p>
          </div>

          <div className="doctor-schedule-date-picker">
            <label htmlFor="appointment-date">เลือกวันที่</label>

            <input
              id="appointment-date"
              type="date"
              value={appointmentDate}
              onChange={(event) => setAppointmentDate(event.target.value)}
            />
          </div>
        </div>

        {isLoading && (
          <div className="doctor-schedule-state">
            <p>กำลังโหลดตารางนัดหมาย...</p>
          </div>
        )}

        {!isLoading && errorMessage && (
          <div className="doctor-schedule-state doctor-schedule-state-error">
            <p role="alert">{errorMessage}</p>
          </div>
        )}

        {!isLoading && !errorMessage && appointments.length === 0 && (
          <div className="doctor-schedule-state">
            <p>ไม่มีรายการนัดหมายในวันนี้</p>
          </div>
        )}

        {!isLoading && !errorMessage && appointments.length > 0 && (
          <div className="doctor-appointment-list">
            {appointments.map((appointment) => (
              <article className="doctor-appointment-item" key={appointment.id}>
                <div className="doctor-appointment-time">
                  <span>เวลา</span>

                  <strong>
                    {formatTime(appointment.start_time)} -{" "}
                    {formatTime(appointment.end_time)} น.
                  </strong>
                </div>

                <div className="doctor-appointment-patient">
                  <span>ชื่อผู้ป่วย</span>

                  <strong>{appointment.patient_name}</strong>
                </div>

                <div className="doctor-appointment-status">
                  <span>สถานะ</span>

                  <strong>{appointment.status}</strong>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </section>
  );
}

export default DoctorSchedulePage;
