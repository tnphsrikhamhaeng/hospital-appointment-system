import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getMyAppointments,
  getAppointmentPatient,
  updateAppointmentStatus,
  type Appointment,
  type AppointmentPatient,
} from "../../appointment/api/appointmentApi";
import { logout } from "../../auth/api/authApi";
import ChangePasswordModal from "../../profile/components/ChangePasswordModal";
import "./DoctorPage.css";

const NO_SHOW_WAIT_MINUTES = 15;

function DoctorPage() {
  const navigate = useNavigate();

  const [appointments, setAppointments] = useState<
    Appointment[]
  >([]);

  const [patients, setPatients] = useState<
    Record<string, AppointmentPatient>
  >({});

  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [isUpdating, setIsUpdating] = useState<string | null>(
    null,
  );

  const [currentTime, setCurrentTime] = useState(
    new Date(),
  );

  const [delayAppointmentId, setDelayAppointmentId] =
    useState<string | null>(null);

  const [noShowAppointmentId, setNoShowAppointmentId] =
    useState<string | null>(null);

  const [isLogoutOpen, setIsLogoutOpen] =
    useState(false);

  const [isChangePasswordOpen, setIsChangePasswordOpen] =
    useState(false);

  const handleOpenLogout = () => {
    setIsLogoutOpen(true);
  };

  const handleCloseLogout = () => {
    setIsLogoutOpen(false);
  };

  const handleConfirmLogout = () => {
    logout();
    setIsLogoutOpen(false);
    navigate("/login", { replace: true });
  };

  const handleOpenChangePassword = () => {
    setIsChangePasswordOpen(true);
  };

  const handleCloseChangePassword = () => {
    setIsChangePasswordOpen(false);
  };

  useEffect(() => {
    const loadAppointments = async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const data = await getMyAppointments();

        setAppointments(data);

        const patientResults = await Promise.allSettled(
          data.map(async (appointment) => {
            const patient = await getAppointmentPatient(
              appointment.id,
            );

            return {
              appointmentId: appointment.id,
              patient,
            };
          }),
        );

        const patientMap: Record<
          string,
          AppointmentPatient
        > = {};

        patientResults.forEach((result) => {
          if (result.status === "fulfilled") {
            patientMap[result.value.appointmentId] =
              result.value.patient;
          }
        });

        setPatients(patientMap);
      } catch {
        setErrorMessage(
          "ไม่สามารถโหลดรายการนัดหมายได้",
        );
      } finally {
        setIsLoading(false);
      }
    };

    void loadAppointments();
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setCurrentTime(new Date());
    }, 30_000);

    return () => {
      window.clearInterval(timer);
    };
  }, []);

  const todayAppointments = useMemo(() => {
    const today = new Date()
      .toISOString()
      .split("T")[0];

    return appointments.filter(
      (appointment) =>
        appointment.appointment_date === today,
    );
  }, [appointments]);

  const dashboardAppointments =
    todayAppointments.length > 0
      ? todayAppointments
      : appointments;

  const sortedAppointments = useMemo(() => {
    return [...dashboardAppointments].sort(
      (a, b) =>
        a.start_time.localeCompare(b.start_time),
    );
  }, [dashboardAppointments]);

  const currentPatientAppointment = useMemo(() => {
    return (
      sortedAppointments.find(
        (appointment) =>
          appointment.status === "in_progress",
      ) ?? null
    );
  }, [sortedAppointments]);

  const nextPatientAppointment = useMemo(() => {
    if (currentPatientAppointment) {
      return null;
    }

    return (
      sortedAppointments.find(
        (appointment) =>
          appointment.status === "checked_in",
      ) ?? null
    );
  }, [
    currentPatientAppointment,
    sortedAppointments,
  ]);

  const upcomingAppointments = useMemo(() => {
    const checkedInAppointments =
      sortedAppointments.filter(
        (appointment) =>
          appointment.status === "checked_in",
      );

    if (currentPatientAppointment) {
      return checkedInAppointments;
    }

    return checkedInAppointments.filter(
      (appointment) =>
        appointment.id !==
        nextPatientAppointment?.id,
    );
  }, [
    currentPatientAppointment,
    nextPatientAppointment,
    sortedAppointments,
  ]);

  const handleCallPatient = async (
    appointment: Appointment,
  ) => {
    const roomNumber = window.prompt(
      "กรุณาระบุเลขห้องตรวจ",
    );

    if (!roomNumber?.trim()) {
      return;
    }

    setErrorMessage("");
    setIsUpdating(appointment.id);

    try {
      const updatedAppointment =
        await updateAppointmentStatus(
          appointment.id,
          {
            status: "in_progress",
            room_number: roomNumber.trim(),
          },
        );

      setAppointments((currentAppointments) =>
        currentAppointments.map(
          (currentAppointment) =>
            currentAppointment.id ===
            updatedAppointment.id
              ? updatedAppointment
              : currentAppointment,
        ),
      );
    } catch {
      setErrorMessage("ไม่สามารถเรียกผู้ป่วยได้");
    } finally {
      setIsUpdating(null);
    }
  };

  const handleMedicalRecord = (
    appointment: Appointment,
  ) => {
    navigate(
      `/medical-record?appointment_id=${appointment.id}`,
    );
  };

  const handleNoShow = (
    appointment: Appointment,
  ) => {
    setNoShowAppointmentId(appointment.id);
  };

  const handleConfirmNoShow = async () => {
    if (!noShowAppointmentId) {
      return;
    }

    const appointment =
      sortedAppointments.find(
        (item) =>
          item.id === noShowAppointmentId,
      );

    if (!appointment) {
      setNoShowAppointmentId(null);
      return;
    }

    setErrorMessage("");
    setIsUpdating(appointment.id);

    try {
      const updatedAppointment =
        await updateAppointmentStatus(
          appointment.id,
          {
            status: "no_show",
            room_number: "",
          },
        );

      setAppointments((currentAppointments) =>
        currentAppointments.map(
          (currentAppointment) =>
            currentAppointment.id ===
            updatedAppointment.id
              ? updatedAppointment
              : currentAppointment,
        ),
      );

      setNoShowAppointmentId(null);
    } catch {
      setErrorMessage(
        "ไม่สามารถบันทึกผู้ป่วยไม่มาตามนัดได้",
      );
    } finally {
      setIsUpdating(null);
    }
  };

  const handleDelayNotice = (
    appointment: Appointment,
  ) => {
    setDelayAppointmentId(appointment.id);
  };

  const handleConfirmDelayNotice = () => {
    if (!delayAppointmentId) {
      return;
    }

    const appointment =
      sortedAppointments.find(
        (item) =>
          item.id === delayAppointmentId,
      );

    if (!appointment) {
      setDelayAppointmentId(null);
      return;
    }

    setErrorMessage(
      `UI สำหรับแจ้งการรักษาล่าช้า: ${
        getPatientName(appointment)
      }`,
    );

    setDelayAppointmentId(null);
  };

  /*
   * TODO:
   * เปลี่ยน Logic เป็น "เวลานัดหมายเริ่มต้น + 15 นาที"
   * ในขั้นตอนแก้ Function No-show
   */
  const canMarkNoShow = (
    appointment: Appointment,
  ) => {
    if (appointment.status !== "in_progress") {
      return false;
    }

    const calledAt = new Date(
      appointment.updated_at,
    );

    if (Number.isNaN(calledAt.getTime())) {
      return false;
    }

    const elapsedMinutes =
      (currentTime.getTime() -
        calledAt.getTime()) /
      (1000 * 60);

    return elapsedMinutes >= NO_SHOW_WAIT_MINUTES;
  };

  const getRemainingNoShowMinutes = (
    appointment: Appointment,
  ) => {
    const calledAt = new Date(
      appointment.updated_at,
    );

    if (Number.isNaN(calledAt.getTime())) {
      return NO_SHOW_WAIT_MINUTES;
    }

    const elapsedMinutes =
      (currentTime.getTime() -
        calledAt.getTime()) /
      (1000 * 60);

    return Math.max(
      0,
      Math.ceil(
        NO_SHOW_WAIT_MINUTES -
          elapsedMinutes,
      ),
    );
  };

  const formatThaiDate = () => {
    return new Intl.DateTimeFormat("th-TH", {
      day: "numeric",
      month: "long",
      year: "numeric",
    }).format(new Date());
  };

  const formatDateOfBirth = (
    patient: AppointmentPatient,
  ) => {
    if (
      !("date_of_birth" in patient) ||
      !patient.date_of_birth
    ) {
      return "ไม่ระบุ";
    }

    const date = new Date(
      String(patient.date_of_birth),
    );

    if (Number.isNaN(date.getTime())) {
      return "ไม่ระบุ";
    }

    return new Intl.DateTimeFormat("th-TH", {
      day: "numeric",
      month: "long",
      year: "numeric",
    }).format(date);
  };

  const getGenderLabel = (
    patient: AppointmentPatient,
  ) => {
    if (!patient.gender) {
      return "ไม่ระบุ";
    }

    switch (
      String(patient.gender).toLowerCase()
    ) {
      case "male":
        return "ชาย";

      case "female":
        return "หญิง";

      case "other":
        return "อื่น ๆ";

      default:
        return String(patient.gender);
    }
  };

  const getPatientName = (
    appointment: Appointment,
  ) => {
    const patient = patients[appointment.id];

    if (!patient) {
      return "กำลังโหลดข้อมูล";
    }

    return `${patient.first_name} ${patient.last_name}`;
  };

  const getPatientCode = (
    appointment: Appointment,
  ) => {
    return appointment.patient_id.slice(
      0,
      8,
    );
  };

  const getStatusLabel = (
    status: Appointment["status"],
  ) => {
    switch (status) {
      case "confirmed":
        return "ยืนยันแล้ว";

      case "checked_in":
        return "รอตรวจ";

      case "in_progress":
        return "กำลังตรวจ";

      case "completed":
        return "เสร็จสิ้น";

      case "cancelled":
        return "ยกเลิก";

      case "no_show":
        return "ไม่มาตามนัด";

      default:
        return status;
    }
  };

  const getStatusClass = (
    status: Appointment["status"],
  ) => {
    switch (status) {
      case "confirmed":
        return "status-confirmed";

      case "checked_in":
        return "status-checked-in";

      case "in_progress":
        return "status-in-progress";

      case "completed":
        return "status-completed";

      case "cancelled":
        return "status-cancelled";

      case "no_show":
        return "status-no-show";

      default:
        return "";
    }
  };

  const currentPatient =
    currentPatientAppointment
      ? patients[
          currentPatientAppointment.id
        ]
      : null;

  const delayAppointment =
    delayAppointmentId
      ? sortedAppointments.find(
          (appointment) =>
            appointment.id ===
            delayAppointmentId,
        )
      : null;

  const noShowAppointment =
    noShowAppointmentId
      ? sortedAppointments.find(
          (appointment) =>
            appointment.id ===
            noShowAppointmentId,
        )
      : null;

  return (
    <main className="doctor-page">
      {/* =========================
          Sidebar
      ========================== */}
      <aside className="doctor-sidebar">
        <div className="sidebar-brand">
          <img
            src="/image/logo/LOGO.png"
            alt="CareFlow"
            className="sidebar-logo"
          />

          <div>
            <strong>CareFlow</strong>

            <span>
              ระบบบริหารจัดการโรงพยาบาล
            </span>
          </div>
        </div>

        <div className="sidebar-role">
          <span>ระบบสำหรับแพทย์</span>
        </div>

        <nav className="sidebar-nav">
          <button
            type="button"
            className="sidebar-nav-item active"
            onClick={() =>
              navigate("/doctor")
            }
          >
            <span className="nav-icon">⌂</span>
            <span>หน้าหลัก</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() =>
              navigate("/doctor/history")
            }
          >
            <span className="nav-icon">▤</span>
            <span>ประวัติการรักษา</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() =>
              navigate("/doctor/schedule")
            }
          >
            <span className="nav-icon">▦</span>
            <span>ตารางนัดหมาย</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <button
            type="button"
            className="sidebar-bottom-item"
            onClick={handleOpenChangePassword}
          >
            <span className="nav-icon">⚿</span>
            <span>เปลี่ยนรหัสผ่าน</span>
          </button>

          <button
            type="button"
            className="sidebar-bottom-item logout-item"
            onClick={handleOpenLogout}
          >
            <span className="nav-icon">↪</span>
            <span>ออกจากระบบ</span>
          </button>
        </div>
      </aside>

      {/* =========================
          Main Content
      ========================== */}
      <section className="doctor-content">
        <header className="doctor-header">
          <div>
            <span className="page-eyebrow">
              CareFlow Hospital System
            </span>

            <h1>หน้าหลัก</h1>

            <p>
              จัดการคิวและดูแลผู้ป่วย
              ที่อยู่ในความรับผิดชอบของคุณ
            </p>
          </div>

          <div className="doctor-header-right">
            <div className="today-date">
              <span>วันนี้</span>

              <strong>
                {formatThaiDate()}
              </strong>
            </div>
          </div>
        </header>

        {errorMessage && (
          <div
            className="doctor-alert"
            role="alert"
          >
            {errorMessage}
          </div>
        )}

        {/* =====================================================
            Current Patient / Next Patient
        ====================================================== */}
        <section
          id="patient-info"
          className="current-patient-section"
        >
          {isLoading ? (
            <div className="current-patient-card no-current-patient">
              <div className="loading-spinner" />

              <div>
                <span className="section-eyebrow">
                  กำลังโหลดข้อมูล
                </span>

                <h2>กำลังโหลดคิวผู้ป่วย...</h2>

                <p>กรุณารอสักครู่</p>
              </div>
            </div>
          ) : currentPatientAppointment ? (
            <div className="current-patient-card in-treatment">
              <div className="current-patient-header">
                <div>
                  <span className="section-eyebrow">
                    ผู้ป่วยที่กำลังตรวจ
                  </span>

                  <h2>
                    {getPatientName(
                      currentPatientAppointment,
                    )}
                  </h2>

                  <p>
                    คิวเวลา{" "}
                    {currentPatientAppointment.start_time.slice(
                      0,
                      5,
                    )}{" "}
                    -{" "}
                    {currentPatientAppointment.end_time.slice(
                      0,
                      5,
                    )}
                  </p>
                </div>

                <span
                  className={`status-badge ${getStatusClass(
                    currentPatientAppointment.status,
                  )}`}
                >
                  <span className="status-dot" />
                  กำลังตรวจ
                </span>
              </div>

              <div className="current-patient-details">
                <div className="patient-main-info">
                  <div className="large-patient-avatar">
                    {getPatientName(
                      currentPatientAppointment,
                    ).charAt(0)}
                  </div>

                  <div>
                    <strong>
                      {getPatientName(
                        currentPatientAppointment,
                      )}
                    </strong>

                    {currentPatient && (
                      <>
                        <span>
                          เพศ:{" "}
                          {getGenderLabel(
                            currentPatient,
                          )}
                        </span>

                        <span>
                          วันเกิด:{" "}
                          {formatDateOfBirth(
                            currentPatient,
                          )}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="current-patient-actions">
                <button
                  type="button"
                  className="action-button primary"
                  onClick={() =>
                    handleMedicalRecord(
                      currentPatientAppointment,
                    )
                  }
                >
                  บันทึกผลการรักษา
                </button>

                <button
                  type="button"
                  className="action-button danger"
                  onClick={() =>
                    handleNoShow(
                      currentPatientAppointment,
                    )
                  }
                  disabled={
                    !canMarkNoShow(
                      currentPatientAppointment,
                    )
                  }
                  title={
                    canMarkNoShow(
                      currentPatientAppointment,
                    )
                      ? "สามารถบันทึกผู้ป่วยไม่มาตามนัดได้"
                      : `สามารถกดได้หลังเรียกผู้ป่วยครบ ${NO_SHOW_WAIT_MINUTES} นาที`
                  }
                >
                  {canMarkNoShow(
                    currentPatientAppointment,
                  )
                    ? "ผู้ป่วยไม่มาตามนัด"
                    : `รอ ${getRemainingNoShowMinutes(
                        currentPatientAppointment,
                      )} นาที`}
                </button>
              </div>
            </div>
          ) : nextPatientAppointment ? (
            <div className="current-patient-card next-patient">
              <div className="current-patient-header">
                <div>
                  <span className="section-eyebrow">
                    คิวถัดไป
                  </span>

                  <h2>
                    {getPatientName(
                      nextPatientAppointment,
                    )}
                  </h2>

                  <p>
                    นัดหมายเวลา{" "}
                    {nextPatientAppointment.start_time.slice(
                      0,
                      5,
                    )}{" "}
                    -{" "}
                    {nextPatientAppointment.end_time.slice(
                      0,
                      5,
                    )}
                  </p>
                </div>

                <span
                  className={`status-badge ${getStatusClass(
                    nextPatientAppointment.status,
                  )}`}
                >
                  <span className="status-dot" />
                  รอตรวจ
                </span>
              </div>

              <div className="next-patient-body">
                <div className="patient-main-info">
                  <div className="large-patient-avatar">
                    {getPatientName(
                      nextPatientAppointment,
                    ).charAt(0)}
                  </div>

                  <div>
                    <strong>
                      {getPatientName(
                        nextPatientAppointment,
                      )}
                    </strong>

                    <span>
                      รหัสผู้ป่วย{" "}
                      {getPatientCode(
                        nextPatientAppointment,
                      )}
                    </span>

                    <span>
                      คิวแรกที่พร้อมสำหรับการตรวจ
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  className="action-button primary call-patient-button"
                  onClick={() =>
                    void handleCallPatient(
                      nextPatientAppointment,
                    )
                  }
                  disabled={
                    isUpdating ===
                    nextPatientAppointment.id
                  }
                >
                  {isUpdating ===
                  nextPatientAppointment.id
                    ? "กำลังเรียกผู้ป่วย..."
                    : "เรียกผู้ป่วย"}
                </button>
              </div>
            </div>
          ) : (
            <div className="current-patient-card no-current-patient">
              <div className="empty-icon">
                ✓
              </div>

              <div>
                <span className="section-eyebrow">
                  ไม่มีผู้ป่วยที่รอตรวจ
                </span>

                <h2>
                  ขณะนี้ไม่มีคิวผู้ป่วย
                </h2>

                <p>
                  เมื่อมีผู้ป่วยเช็กอินแล้ว
                  คิวถัดไปจะแสดงที่บริเวณนี้
                </p>
              </div>
            </div>
          )}
        </section>

        {/* =====================================================
            Upcoming Queue
        ====================================================== */}
        <section
          id="upcoming-appointments"
          className="upcoming-section"
        >
          <div className="appointment-section-header">
            <div>
              <span className="section-eyebrow">
                คิว
              </span>

              <h2>คิวผู้ป่วยถัดไป</h2>

              <p>
                ผู้ป่วยที่รอรับการตรวจ
                และสามารถแจ้งการรักษาล่าช้าได้
              </p>
            </div>

            <span className="appointment-count">
              {upcomingAppointments.length} คิว
            </span>
          </div>

          {upcomingAppointments.length === 0 ? (
            <div className="empty-appointments">
              <div className="empty-icon">
                ✓
              </div>

              <h3>
                ไม่มีผู้ป่วยในคิวถัดไป
              </h3>

              <p>
                เมื่อมีผู้ป่วยเช็กอิน
                รายการจะแสดงที่นี่
              </p>
            </div>
          ) : (
            <div className="upcoming-queue-list">
              {upcomingAppointments.map(
                (appointment, index) => (
                  <article
                    key={appointment.id}
                    className="upcoming-queue-item"
                  >
                    <div className="queue-number">
                      {index + 1}
                    </div>

                    <div className="queue-time">
                      <strong>
                        {appointment.start_time.slice(
                          0,
                          5,
                        )}
                      </strong>

                      <span>
                        {appointment.end_time.slice(
                          0,
                          5,
                        )}
                      </span>
                    </div>

                    <div className="queue-patient">
                      <div className="patient-avatar">
                        {getPatientName(
                          appointment,
                        ).charAt(0)}
                      </div>

                      <div>
                        <strong>
                          {getPatientName(
                            appointment,
                          )}
                        </strong>

                        <span>
                          รหัสผู้ป่วย{" "}
                          {getPatientCode(
                            appointment,
                          )}
                        </span>
                      </div>
                    </div>

                    <span
                      className={`status-badge ${getStatusClass(
                        appointment.status,
                      )}`}
                    >
                      <span className="status-dot" />
                      {getStatusLabel(
                        appointment.status,
                      )}
                    </span>

                    <div className="queue-actions">
                      <button
                        type="button"
                        className="action-button warning"
                        onClick={() =>
                          handleDelayNotice(
                            appointment,
                          )
                        }
                      >
                        แจ้งการรักษาล่าช้า
                      </button>
                    </div>
                  </article>
                ),
              )}
            </div>
          )}
        </section>
      </section>

      {/* =======================================================
          No-show Confirmation Modal
      ======================================================== */}
      {noShowAppointment && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={() =>
            setNoShowAppointmentId(null)
          }
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="no-show-modal-title"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="doctor-modal-icon warning">
              !
            </div>

            <h2 id="no-show-modal-title">
              ยืนยันผู้ป่วยไม่มาตามนัด
            </h2>

            <p>
              คุณต้องการบันทึกผู้ป่วย{" "}
              <strong>
                {getPatientName(
                  noShowAppointment,
                )}
              </strong>{" "}
              ว่าไม่มาตามนัดใช่หรือไม่?
            </p>

            <p className="modal-note">
              เมื่อยืนยันแล้ว
              สถานะนัดหมายจะถูกเปลี่ยนเป็น
              “ไม่มาตามนัด”
            </p>

            <div className="doctor-modal-actions">
              <button
                type="button"
                className="action-button secondary"
                onClick={() =>
                  setNoShowAppointmentId(null)
                }
                disabled={
                  isUpdating ===
                  noShowAppointment.id
                }
              >
                ยกเลิก
              </button>

              <button
                type="button"
                className="action-button danger"
                onClick={() =>
                  void handleConfirmNoShow()
                }
                disabled={
                  isUpdating ===
                  noShowAppointment.id
                }
              >
                {isUpdating ===
                noShowAppointment.id
                  ? "กำลังบันทึก..."
                  : "ยืนยัน"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =======================================================
          Logout Confirmation Modal
      ======================================================== */}
      {isLogoutOpen && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={handleCloseLogout}
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="logout-modal-title"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="doctor-modal-icon warning">
              ↪
            </div>

            <h2 id="logout-modal-title">
              ยืนยันการออกจากระบบ
            </h2>

            <p>
              คุณต้องการออกจากระบบใช่หรือไม่?
            </p>

            <div className="doctor-modal-actions">
              <button
                type="button"
                className="action-button secondary"
                onClick={handleCloseLogout}
              >
                ยกเลิก
              </button>

              <button
                type="button"
                className="action-button danger"
                onClick={handleConfirmLogout}
              >
                ยืนยัน
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =======================================================
          Change Password Modal
      ======================================================== */}
      <ChangePasswordModal
        isOpen={isChangePasswordOpen}
        onClose={handleCloseChangePassword}
      />

      {/* =======================================================
          Delay Notification Modal
      ======================================================== */}
      {delayAppointment && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={() =>
            setDelayAppointmentId(null)
          }
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delay-modal-title"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="doctor-modal-icon warning">
              !
            </div>

            <h2 id="delay-modal-title">
              แจ้งการรักษาล่าช้า
            </h2>

            <p>
              แจ้งผู้ป่วย{" "}
              <strong>
                {getPatientName(
                  delayAppointment,
                )}
              </strong>{" "}
              ว่าการรักษาอาจล่าช้ากว่ากำหนด
            </p>

            <div className="delay-info">
              <span>เวลานัดหมาย</span>

              <strong>
                {delayAppointment.start_time.slice(
                  0,
                  5,
                )}{" "}
                -{" "}
                {delayAppointment.end_time.slice(
                  0,
                  5,
                )}
              </strong>
            </div>

            <p className="modal-note">
              ขณะนี้เป็นการแสดงหน้าจอเท่านั้น
              ยังไม่ได้ส่งการแจ้งเตือนจริง
            </p>

            <div className="doctor-modal-actions">
              <button
                type="button"
                className="action-button secondary"
                onClick={() =>
                  setDelayAppointmentId(null)
                }
              >
                ยกเลิก
              </button>

              <button
                type="button"
                className="action-button warning"
                onClick={
                  handleConfirmDelayNotice
                }
              >
                ส่งการแจ้งเตือน
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export default DoctorPage;