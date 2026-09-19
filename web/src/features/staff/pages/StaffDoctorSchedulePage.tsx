import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  CalendarDays,
  Trash2,
} from "lucide-react";

import {
  createDoctorSchedule,
  deleteDoctorSchedule,
  getDoctorSchedule,
  updateDoctorSchedule,
  type DoctorScheduleTemplate,
  type Weekday,
} from "../../doctor/api/doctorScheduleApi";

import { getDoctorById } from "../../doctor/api/doctorApi";

import ChangePasswordModal from "../../profile/components/ChangePasswordModal";

import "../../doctor/pages/DoctorPage.css";

interface DoctorInfo {
  id: string;
  preface?: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  license_number?: string;
}

interface ScheduleForm {
  weekday: Weekday;
  start_time: string;
  end_time: string;
}

const WEEKDAY_OPTIONS: {
  value: Weekday;
  label: string;
}[] = [
  { value: "monday", label: "วันจันทร์" },
  { value: "tuesday", label: "วันอังคาร" },
  { value: "wednesday", label: "วันพุธ" },
  { value: "thursday", label: "วันพฤหัสบดี" },
  { value: "friday", label: "วันศุกร์" },
  { value: "saturday", label: "วันเสาร์" },
  { value: "sunday", label: "วันอาทิตย์" },
];

const WEEKDAY_ORDER: Record<Weekday, number> = {
  monday: 1,
  tuesday: 2,
  wednesday: 3,
  thursday: 4,
  friday: 5,
  saturday: 6,
  sunday: 7,
};

const EMPTY_FORM: ScheduleForm = {
  weekday: "monday",
  start_time: "09:00",
  end_time: "17:00",
};

const scheduleHeaderButtonStyle = {
  minHeight: "42px",
  padding: "0 16px",
  boxSizing: "border-box" as const,
  justifyContent: "center",
};

const getDoctorDisplayName = (
  doctor: DoctorInfo | null,
) => {
  if (!doctor) {
    return "แพทย์";
  }

  if (doctor.full_name) {
    return doctor.full_name;
  }

  const prefaceMap: Record<string, string> = {
    mr_doctor: "นายแพทย์",
    female_doctor: "แพทย์หญิง",
    ms_doctor: "แพทย์หญิง",
    doctor: "แพทย์",
  };

  const thaiPreface = doctor.preface
    ? prefaceMap[doctor.preface] ?? doctor.preface
    : "";

  const fullName = [
    thaiPreface,
    doctor.first_name,
    doctor.last_name,
  ]
    .filter(Boolean)
    .join(" ")
    .trim();

  return fullName || "แพทย์";
};

const getErrorMessage = (error: unknown) => {
  const axiosError = error as {
    response?: {
      data?: {
        detail?: string | { msg?: string }[];
      };
    };
  };

  const detail = axiosError.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg)
      .filter(Boolean)
      .join(", ");
  }

  return "เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง";
};

const formatTime = (time: string) => {
  return time.slice(0, 5);
};

const getWeekdayLabel = (weekday: Weekday) => {
  return (
    WEEKDAY_OPTIONS.find(
      (item) => item.value === weekday,
    )?.label ?? weekday
  );
};

const StaffDoctorSchedulePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const doctorId = searchParams.get("doctor_id");

  const [doctor, setDoctor] =
    useState<DoctorInfo | null>(null);

  const [schedules, setSchedules] = useState<
    DoctorScheduleTemplate[]
  >([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  /* =========================
     Change Password
  ========================== */
  const [
    isChangePasswordOpen,
    setIsChangePasswordOpen,
  ] = useState(false);

  const [showModal, setShowModal] = useState(false);

  const [editingSchedule, setEditingSchedule] =
    useState<DoctorScheduleTemplate | null>(null);

  const [form, setForm] =
    useState<ScheduleForm>(EMPTY_FORM);

  const [saving, setSaving] = useState(false);

  const [showDeleteModal, setShowDeleteModal] =
    useState(false);

  const [deletingSchedule, setDeletingSchedule] =
    useState<DoctorScheduleTemplate | null>(null);

  const [deletePassword, setDeletePassword] =
    useState("");

  const [deleting, setDeleting] =
    useState(false);

  const [deleteError, setDeleteError] =
    useState("");

  const [formError, setFormError] = useState("");

  const sortedSchedules = useMemo(() => {
    return [...schedules].sort((a, b) => {
      const weekdayDifference =
        WEEKDAY_ORDER[a.weekday] -
        WEEKDAY_ORDER[b.weekday];

      if (weekdayDifference !== 0) {
        return weekdayDifference;
      }

      return a.start_time.localeCompare(
        b.start_time,
      );
    });
  }, [schedules]);

  const loadData = async () => {
    if (!doctorId) {
      setError("ไม่พบข้อมูลแพทย์");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const [
        doctorResponse,
        scheduleResponse,
      ] = await Promise.all([
        getDoctorById(doctorId),
        getDoctorSchedule(doctorId),
      ]);

      setDoctor(
        doctorResponse as DoctorInfo,
      );

      setSchedules(scheduleResponse);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, [doctorId]);

  const openCreateModal = () => {
    setEditingSchedule(null);
    setForm(EMPTY_FORM);
    setFormError("");
    setShowModal(true);
  };

  const openEditModal = (
    schedule: DoctorScheduleTemplate,
  ) => {
    setEditingSchedule(schedule);

    setForm({
      weekday: schedule.weekday,
      start_time: formatTime(
        schedule.start_time,
      ),
      end_time: formatTime(
        schedule.end_time,
      ),
    });

    setFormError("");
    setShowModal(true);
  };

  const closeModal = () => {
    if (saving) {
      return;
    }

    setShowModal(false);
    setEditingSchedule(null);
    setForm(EMPTY_FORM);
    setFormError("");
  };

  const handleFormChange = (
    field: keyof ScheduleForm,
    value: string,
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    if (!doctorId) {
      return;
    }

    if (
      !form.start_time ||
      !form.end_time
    ) {
      setFormError(
        "กรุณาระบุเวลาเริ่มต้นและเวลาสิ้นสุด",
      );
      return;
    }

    if (
      form.start_time >=
      form.end_time
    ) {
      setFormError(
        "เวลาเริ่มต้นต้องน้อยกว่าเวลาสิ้นสุด",
      );
      return;
    }

    try {
      setSaving(true);
      setFormError("");

      if (editingSchedule) {
        await updateDoctorSchedule(
          editingSchedule.id,
          {
            weekday: form.weekday,
            start_time: form.start_time,
            end_time: form.end_time,
          },
        );
      } else {
        await createDoctorSchedule({
          doctor_id: doctorId,
          weekday: form.weekday,
          start_time: form.start_time,
          end_time: form.end_time,
        });
      }

      await loadData();

      setShowModal(false);
      setEditingSchedule(null);
      setForm(EMPTY_FORM);
      setFormError("");
    } catch (err) {
      setFormError(
        getErrorMessage(err),
      );
    } finally {
      setSaving(false);
    }
  };

  const openDeleteModal = (
    schedule: DoctorScheduleTemplate,
  ) => {
    setDeletingSchedule(schedule);
    setDeletePassword("");
    setDeleteError("");
    setShowDeleteModal(true);
  };

  const closeDeleteModal = () => {
    if (deleting) {
      return;
    }

    setShowDeleteModal(false);
    setDeletingSchedule(null);
    setDeletePassword("");
    setDeleteError("");
  };

  const handleDelete = async () => {
    if (!deletingSchedule) {
      return;
    }

    if (!deletePassword.trim()) {
      setDeleteError(
        "กรุณากรอกรหัสผ่าน Staff",
      );
      return;
    }

    try {
      setDeleting(true);
      setDeleteError("");
      setError("");

      await deleteDoctorSchedule(
        deletingSchedule.id,
      );

      setShowDeleteModal(false);
      setDeletingSchedule(null);
      setDeletePassword("");

      await loadData();
    } catch (err) {
      setDeleteError(
        getErrorMessage(err),
      );
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="doctor-page">
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
          <span>
            ระบบสำหรับเจ้าหน้าที่
          </span>
        </div>

        <nav className="sidebar-nav">
          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() =>
              navigate("/staff")
            }
          >
            <span className="nav-icon">
              ▣
            </span>

            <span>เช็คอินผู้ป่วย</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item active"
            onClick={() =>
              navigate("/staff/doctors")
            }
          >
            <span className="nav-icon">
              ⚕
            </span>

            <span>จัดการแพทย์</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() =>
              navigate("/staff")
            }
          >
            <span className="nav-icon">
              ♙
            </span>

            <span>จัดการ Staff</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() =>
              navigate(
                "/staff/departments",
              )
            }
          >
            <span className="nav-icon">
              ▦
            </span>

            <span>จัดการแผนก</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <button
            type="button"
            className="sidebar-bottom-item"
            onClick={() =>
              setIsChangePasswordOpen(
                true,
              )
            }
          >
            <span className="nav-icon">
              ⚿
            </span>

            <span>
              เปลี่ยนรหัสผ่าน
            </span>
          </button>

          <button
            type="button"
            className="sidebar-bottom-item logout-item"
            onClick={() =>
              navigate("/login")
            }
          >
            <span className="nav-icon">
              ↪
            </span>

            <span>ออกจากระบบ</span>
          </button>
        </div>
      </aside>

      {/* =========================
          Main Content
      ========================== */}
      <main className="doctor-content">
        <header className="doctor-header">
          <div>
            <span className="page-eyebrow">
              จัดการแพทย์
            </span>

            <h1>
              ตารางเวลาของแพทย์
            </h1>

            <p>
              จัดการวันและเวลาที่แพทย์เปิดให้บริการสำหรับการนัดหมาย
            </p>
          </div>

          <div
            className="doctor-header-right"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <button
              type="button"
              className="action-button secondary"
              onClick={() =>
                navigate(
                  "/staff/doctors",
                )
              }
              style={scheduleHeaderButtonStyle}
            >
              กลับ
            </button>

            <button
              type="button"
              className="action-button primary"
              onClick={openCreateModal}
              style={scheduleHeaderButtonStyle}
            >
              เพิ่มตารางเวลา
            </button>
          </div>
        </header>

        {error && (
          <div className="doctor-alert">
            {error}
          </div>
        )}

        <section className="current-patient-section">
          <div className="current-patient-card">
            <div className="current-patient-header">
              <div>
                <span className="section-eyebrow">
                  Doctor
                </span>

                <h2>
                  {getDoctorDisplayName(
                    doctor,
                  )}
                </h2>

                <p>
                  {doctor?.license_number
                    ? `เลขใบประกอบวิชาชีพ ${doctor.license_number}`
                    : "จัดการตารางเวลาการให้บริการของแพทย์"}
                </p>
              </div>
            </div>

            <div className="current-patient-details">
              {loading ? (
                <div className="empty-appointments">
                  <div className="loading-spinner" />

                  <p>
                    กำลังโหลดตารางเวลา...
                  </p>
                </div>
              ) : sortedSchedules.length ===
                0 ? (
                <div className="no-current-patient">
                  <div className="empty-icon">
                    <CalendarDays
                      size={22}
                    />
                  </div>

                  <div>
                    <h2>
                      ยังไม่มีตารางเวลา
                    </h2>

                    <p>
                      เพิ่มตารางเวลาสำหรับแพทย์คนนี้เพื่อเปิดช่วงเวลาสำหรับการนัดหมาย
                    </p>
                  </div>
                </div>
              ) : (
                <div className="upcoming-queue-list">
                  {sortedSchedules.map(
                    (schedule) => (
                      <div
                        key={schedule.id}
                        className="upcoming-queue-item"
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "24px",
                          width: "100%",
                          boxSizing:
                            "border-box",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            alignItems:
                              "center",
                            gap: "32px",
                            flex: 1,
                            minWidth: 0,
                          }}
                        >
                          <strong
                            style={{
                              minWidth:
                                "72px",
                              color:
                                "var(--text)",
                              fontSize:
                                "14px",
                              fontWeight: 600,
                              whiteSpace:
                                "nowrap",
                            }}
                          >
                            {getWeekdayLabel(
                              schedule.weekday,
                            )}
                          </strong>

                          <span
                            style={{
                              color:
                                "var(--text)",
                              fontSize:
                                "14px",
                              whiteSpace:
                                "nowrap",
                            }}
                          >
                            {formatTime(
                              schedule.start_time,
                            )}{" "}
                            -{" "}
                            {formatTime(
                              schedule.end_time,
                            )}
                          </span>
                        </div>

                        <span
                          className={
                            schedule.is_active
                              ? "status-badge status-checked-in"
                              : "status-badge status-cancelled"
                          }
                          style={{
                            flexShrink: 0,
                          }}
                        >
                          <span className="status-dot" />

                          {schedule.is_active
                            ? "เปิดให้บริการ"
                            : "ปิดใช้งาน"}
                        </span>

                        <div
                          className="queue-actions"
                          style={{
                            display: "flex",
                            alignItems:
                              "center",
                            gap: "8px",
                            flexShrink: 0,
                          }}
                        >
                          <button
                            type="button"
                            className="action-button secondary"
                            onClick={() =>
                              openEditModal(
                                schedule,
                              )
                            }
                          >
                            แก้ไข
                          </button>

                          <button
                            type="button"
                            className="action-button danger"
                            onClick={() =>
                              openDeleteModal(
                                schedule,
                              )
                            }
                            disabled={deleting}
                          >
                            ลบ
                          </button>
                        </div>
                      </div>
                    ),
                  )}
                </div>
              )}
            </div>
          </div>
        </section>
      </main>

      {/* =========================
          Change Password Modal
      ========================== */}
      <ChangePasswordModal
        isOpen={
          isChangePasswordOpen
        }
        onClose={() =>
          setIsChangePasswordOpen(
            false,
          )
        }
      />

      {/* =========================
          Add / Edit Schedule Modal
      ========================== */}
      {showModal && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={closeModal}
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="schedule-modal-title"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="doctor-modal-icon">
              <CalendarDays
                size={20}
              />
            </div>

            <h2 id="schedule-modal-title">
              {editingSchedule
                ? "แก้ไขตารางเวลา"
                : "เพิ่มตารางเวลา"}
            </h2>

            <p>
              {getDoctorDisplayName(
                doctor,
              )}
            </p>

            <form
              onSubmit={(event) => {
                event.preventDefault();
                void handleSave();
              }}
            >
              <div
                style={{
                  textAlign: "left",
                }}
              >
                <label
                  htmlFor="schedule-weekday"
                  style={{
                    display: "block",
                    textAlign: "left",
                  }}
                >
                  วันให้บริการ
                </label>

                <select
                  id="schedule-weekday"
                  value={form.weekday}
                  disabled={saving}
                  onChange={(event) =>
                    handleFormChange(
                      "weekday",
                      event.target.value,
                    )
                  }
                  style={{
                    width: "100%",
                    height: "42px",
                    boxSizing:
                      "border-box",
                    padding: "0 12px",
                    border:
                      "1px solid var(--border)",
                    borderRadius: "7px",
                    outline: "none",
                    background:
                      "var(--surface)",
                    color:
                      "var(--text)",
                    fontFamily:
                      "var(--font)",
                    fontSize: "14px",
                  }}
                >
                  {WEEKDAY_OPTIONS.map(
                    (option) => (
                      <option
                        key={option.value}
                        value={
                          option.value
                        }
                      >
                        {option.label}
                      </option>
                    ),
                  )}
                </select>
              </div>

              <div
                style={{
                  textAlign: "left",
                }}
              >
                <label
                  htmlFor="schedule-start-time"
                  style={{
                    display: "block",
                    textAlign: "left",
                  }}
                >
                  เวลาเริ่มต้น
                </label>

                <input
                  id="schedule-start-time"
                  type="time"
                  value={
                    form.start_time
                  }
                  disabled={saving}
                  onChange={(event) =>
                    handleFormChange(
                      "start_time",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div
                style={{
                  textAlign: "left",
                }}
              >
                <label
                  htmlFor="schedule-end-time"
                  style={{
                    display: "block",
                    textAlign: "left",
                  }}
                >
                  เวลาสิ้นสุด
                </label>

                <input
                  id="schedule-end-time"
                  type="time"
                  value={
                    form.end_time
                  }
                  disabled={saving}
                  onChange={(event) =>
                    handleFormChange(
                      "end_time",
                      event.target.value,
                    )
                  }
                />
              </div>

              {formError && (
                <p role="alert">
                  {formError}
                </p>
              )}

              <div
                className="doctor-modal-actions"
                style={{
                  flexDirection:
                    "column",
                  alignItems:
                    "stretch",
                  gap: "8px",
                  width: "100%",
                }}
              >
                <button
                  type="submit"
                  className="action-button primary"
                  disabled={saving}
                  style={{
                    width: "100%",
                    justifyContent:
                      "center",
                    boxSizing:
                      "border-box",
                  }}
                >
                  {saving
                    ? "กำลังบันทึก..."
                    : editingSchedule
                      ? "บันทึกการแก้ไข"
                      : "เพิ่มตารางเวลา"}
                </button>

                <button
                  type="button"
                  className="action-button secondary"
                  disabled={saving}
                  onClick={closeModal}
                  style={{
                    width: "100%",
                    justifyContent:
                      "center",
                    boxSizing:
                      "border-box",
                  }}
                >
                  ยกเลิก
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =========================
          Delete Confirmation Modal
      ========================== */}
      {showDeleteModal &&
        deletingSchedule && (
          <div
            className="doctor-modal-overlay"
            role="presentation"
            onClick={closeDeleteModal}
          >
            <div
              className="doctor-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="delete-schedule-title"
              onClick={(event) =>
                event.stopPropagation()
              }
            >
              <div className="doctor-modal-icon warning">
                <Trash2 size={20} />
              </div>

              <h2 id="delete-schedule-title">
                ยืนยันการลบตารางเวลา
              </h2>

              <p>
                ต้องการลบตารางเวลา{" "}
                <strong>
                  {getWeekdayLabel(
                    deletingSchedule.weekday,
                  )}
                </strong>{" "}
                เวลา{" "}
                <strong>
                  {formatTime(
                    deletingSchedule.start_time,
                  )}{" "}
                  -{" "}
                  {formatTime(
                    deletingSchedule.end_time,
                  )}
                </strong>{" "}
                หรือไม่?
              </p>

              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  void handleDelete();
                }}
              >
                <div
                  style={{
                    textAlign: "left",
                  }}
                >
                  <label
                    htmlFor="delete-schedule-password"
                    style={{
                      display: "block",
                      textAlign: "left",
                    }}
                  >
                    ยืนยันรหัสผ่าน Staff
                  </label>

                  <input
                    id="delete-schedule-password"
                    type="password"
                    value={deletePassword}
                    placeholder="กรอกรหัสผ่าน"
                    disabled={deleting}
                    onChange={(event) => {
                      setDeletePassword(
                        event.target.value,
                      );
                      setDeleteError("");
                    }}
                  />
                </div>

                {deleteError && (
                  <p role="alert">
                    {deleteError}
                  </p>
                )}

                <div
                  className="doctor-modal-actions"
                  style={{
                    flexDirection:
                      "column",
                    alignItems:
                      "stretch",
                    gap: "8px",
                    width: "100%",
                  }}
                >
                  <button
                    type="submit"
                    className="action-button danger"
                    disabled={deleting}
                    style={{
                      width: "100%",
                      justifyContent:
                        "center",
                      boxSizing:
                        "border-box",
                    }}
                  >
                    {deleting
                      ? "กำลังลบ..."
                      : "ยืนยันการลบ"}
                  </button>

                  <button
                    type="button"
                    className="action-button secondary"
                    disabled={deleting}
                    onClick={
                      closeDeleteModal
                    }
                    style={{
                      width: "100%",
                      justifyContent:
                        "center",
                      boxSizing:
                        "border-box",
                    }}
                  >
                    ยกเลิก
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
    </div>
  );
};

export default StaffDoctorSchedulePage;

