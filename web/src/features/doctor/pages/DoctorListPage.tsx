import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
} from "lucide-react";

import {
  deleteDoctor,
  getDoctors,
  reactivateDoctor,
  type DoctorResponse,
} from "../api/doctorApi";

import ChangePasswordModal from "../../profile/components/ChangePasswordModal";

import "../../doctor/pages/DoctorPage.css";

/* =========================
   Translate API Errors
========================== */
const translateDoctorError = (
  message?: string,
): string => {
  if (!message) {
    return "เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง";
  }

  const errorMessages: Record<
    string,
    string
  > = {
    "Doctor not found":
      "ไม่พบข้อมูลแพทย์",

    "Doctor not found.":
      "ไม่พบข้อมูลแพทย์",

    "Invalid credentials":
      "รหัสผ่านไม่ถูกต้อง",

    "Invalid credentials.":
      "รหัสผ่านไม่ถูกต้อง",

    "Incorrect password":
      "รหัสผ่านไม่ถูกต้อง",

    "Incorrect password.":
      "รหัสผ่านไม่ถูกต้อง",

    "Password is incorrect":
      "รหัสผ่านไม่ถูกต้อง",

    "Password is incorrect.":
      "รหัสผ่านไม่ถูกต้อง",

    "Doctor is already inactive":
      "แพทย์รายนี้ถูกปิดใช้งานอยู่แล้ว",

    "Doctor is already inactive.":
      "แพทย์รายนี้ถูกปิดใช้งานอยู่แล้ว",

    "Doctor is already active":
      "แพทย์รายนี้เปิดใช้งานอยู่แล้ว",

    "Doctor is already active.":
      "แพทย์รายนี้เปิดใช้งานอยู่แล้ว",

    "Doctor not found or inactive":
      "ไม่พบแพทย์ หรือแพทย์ถูกปิดใช้งาน",

    "Doctor not found or inactive.":
      "ไม่พบแพทย์ หรือแพทย์ถูกปิดใช้งาน",

    "Username already exists":
      "Username นี้มีอยู่ในระบบแล้ว",

    "Username already exists.":
      "Username นี้มีอยู่ในระบบแล้ว",

    "Email already exists":
      "อีเมลนี้มีอยู่ในระบบแล้ว",

    "Email already exists.":
      "อีเมลนี้มีอยู่ในระบบแล้ว",

    "Phone number already exists":
      "เบอร์โทรศัพท์นี้มีอยู่ในระบบแล้ว",

    "Phone number already exists.":
      "เบอร์โทรศัพท์นี้มีอยู่ในระบบแล้ว",
  };

  return (
    errorMessages[message] ??
    "ไม่สามารถดำเนินการได้ กรุณาลองใหม่อีกครั้ง"
  );
};

const doctorModalStyle = `
  .doctor-action-modal {
  width: calc(100% - 32px);
  max-width: 520px;
  box-sizing: border-box;
}
  .doctor-action-modal-field {
    width: 100%;
    margin-top: 18px;
  }

  .doctor-action-modal-field label {
    display: block;
    width: 100%;
    margin-bottom: 7px;
    color: var(--text);
    font-size: 13px;
    font-weight: 400 !important;
    line-height: 1.4;
    text-align: left;
  }

  .doctor-action-modal-field input {
    display: block;
    width: 100%;
    height: 42px;
    box-sizing: border-box;
    padding: 0 12px;
    border: 1px solid var(--border);
    border-radius: 7px;
    outline: none;
    background: var(--surface);
    color: var(--text);
    font-family: var(--font);
    font-size: 14px;
    font-weight: 400 !important;
  }

  .doctor-action-modal-field input:focus {
    border-color: var(--primary);
  }

  .doctor-action-modal-error {
    width: 100%;
    margin: 10px 0 0;
    color: var(--danger);
    font-size: 13px;
    font-weight: 400 !important;
    line-height: 1.5;
    text-align: left;
  }

  .doctor-action-modal-actions {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 20px;
  }

  .doctor-action-modal-actions .action-button {
    width: 100%;
    min-height: 42px;
    box-sizing: border-box;
    justify-content: center;
    font-weight: 400 !important;
  }
`;

function DoctorListPage() {
  const navigate = useNavigate();

  const [doctors, setDoctors] = useState<
    DoctorResponse[]
  >([]);

  const [search, setSearch] = useState("");

  const [showInactive, setShowInactive] =
    useState(false);

  const [isLoading, setIsLoading] =
    useState(true);

  const [errorMessage, setErrorMessage] =
    useState("");

  /* =========================
     Change Password
  ========================== */
  const [
    isChangePasswordOpen,
    setIsChangePasswordOpen,
  ] = useState(false);

  /* =========================
     Deactivate Doctor
  ========================== */
  const [
    selectedDeactivateDoctor,
    setSelectedDeactivateDoctor,
  ] = useState<DoctorResponse | null>(null);

  const [
    deactivatePassword,
    setDeactivatePassword,
  ] = useState("");

  const [
    deactivating,
    setDeactivating,
  ] = useState(false);

  const [
    deactivateError,
    setDeactivateError,
  ] = useState("");

  /* =========================
     Reactivate Doctor
  ========================== */
  const [
    selectedDoctor,
    setSelectedDoctor,
  ] = useState<DoctorResponse | null>(null);

  const [password, setPassword] =
    useState("");

  const [
    reactivating,
    setReactivating,
  ] = useState(false);

  const [
    reactivateError,
    setReactivateError,
  ] = useState("");

  /* =========================
     Load Doctors
  ========================== */
  const loadDoctors = async (
    searchValue = "",
    inactive = false,
  ) => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const data = await getDoctors({
        ...(searchValue.trim()
          ? {
              search: searchValue.trim(),
            }
          : {}),
        ...(inactive
          ? {
              status: "inactive",
            }
          : {}),
      });

      setDoctors(data);
    } catch {
      setErrorMessage(
        "ไม่สามารถโหลดรายการแพทย์ได้",
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadDoctors();
  }, []);

  /* =========================
     Search
  ========================== */
  const handleSearchChange = (
    value: string,
  ) => {
    setSearch(value);

    void loadDoctors(
      value,
      showInactive,
    );
  };

  const handleSearch = () => {
    void loadDoctors(
      search,
      showInactive,
    );
  };

  const handleClearSearch = () => {
    setSearch("");

    void loadDoctors(
      "",
      showInactive,
    );
  };

  const handleToggleInactive = () => {
    const nextShowInactive =
      !showInactive;

    setShowInactive(
      nextShowInactive,
    );

    setSearch("");

    void loadDoctors(
      "",
      nextShowInactive,
    );
  };

  /* =========================
     Deactivate Modal
  ========================== */
  const handleOpenDeactivate = (
    doctor: DoctorResponse,
  ) => {
    setSelectedDeactivateDoctor(
      doctor,
    );

    setDeactivatePassword("");
    setDeactivateError("");
  };

  const handleCloseDeactivate = () => {
    if (deactivating) {
      return;
    }

    setSelectedDeactivateDoctor(
      null,
    );

    setDeactivatePassword("");
    setDeactivateError("");
  };

  const handleDeactivate = async () => {
    if (!selectedDeactivateDoctor) {
      return;
    }

    if (!deactivatePassword.trim()) {
      setDeactivateError(
        "กรุณากรอกรหัสผ่าน Staff",
      );

      return;
    }

    try {
      setDeactivating(true);
      setDeactivateError("");
      setErrorMessage("");

      await deleteDoctor(
        selectedDeactivateDoctor.id,
        deactivatePassword,
      );

      setSelectedDeactivateDoctor(
        null,
      );

      setDeactivatePassword("");

      setDoctors((current) =>
        current.filter(
          (item) =>
            item.id !==
            selectedDeactivateDoctor.id,
        ),
      );
    } catch (error: unknown) {
      let message: string | undefined;

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

        message =
          response?.data?.detail;
      }

      setDeactivateError(
        translateDoctorError(message),
      );
    } finally {
      setDeactivating(false);
    }
  };

  /* =========================
     Reactivate Modal
  ========================== */
  const handleOpenReactivate = (
    doctor: DoctorResponse,
  ) => {
    setSelectedDoctor(doctor);
    setPassword("");
    setReactivateError("");
  };

  const handleCloseReactivate = () => {
    if (reactivating) {
      return;
    }

    setSelectedDoctor(null);
    setPassword("");
    setReactivateError("");
  };

  const handleReactivate = async () => {
    if (!selectedDoctor) {
      return;
    }

    if (!password.trim()) {
      setReactivateError(
        "กรุณากรอกรหัสผ่าน Staff",
      );

      return;
    }

    try {
      setReactivating(true);
      setReactivateError("");
      setErrorMessage("");

      await reactivateDoctor(
        selectedDoctor.id,
        password,
      );

      setSelectedDoctor(null);
      setPassword("");

      await loadDoctors(
        search,
        showInactive,
      );
    } catch (error: unknown) {
      let message: string | undefined;

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

        message =
          response?.data?.detail;
      }

      setReactivateError(
        translateDoctorError(message),
      );
    } finally {
      setReactivating(false);
    }
  };

  const getDoctorName = (
    doctor: DoctorResponse,
  ) => {
    const prefaceMap: Record<
      string,
      string
    > = {
      mr_doctor: "นายแพทย์",
      female_doctor: "แพทย์หญิง",
      doctor: "แพทย์",
    };

    const thaiPreface =
      prefaceMap[doctor.preface] ??
      doctor.preface;

    return `${thaiPreface} ${doctor.first_name} ${doctor.last_name}`;
  };

  return (
    <main className="doctor-page">
      <style>
        {doctorModalStyle}
      </style>

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
              navigate(
                "/staff/doctors",
              )
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
              navigate(
                "/staff/create",
              )
            }
          >
            <span className="nav-icon">
              ♙
            </span>

            <span>จัดการเจ้าหน้าที่</span>
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
              navigate("/login", {
                replace: true,
              })
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
      <section className="doctor-content">
        <header className="doctor-header">
          <div>
            <span className="page-eyebrow">
              CareFlow Hospital System
            </span>

            <h1>จัดการแพทย์</h1>

            <p>
              จัดการข้อมูลแพทย์
              และตรวจสอบรายชื่อแพทย์ในระบบ
            </p>
          </div>

          <div className="doctor-header-right">
            <button
              type="button"
              className="action-button primary"
              onClick={() =>
                navigate(
                  "/staff/doctors/create",
                )
              }
            >
              + เพิ่มแพทย์ใหม่
            </button>
          </div>
        </header>

        {/* =========================
            Search
        ========================== */}
        <section className="current-patient-section">
          <div className="current-patient-card">
            <div className="current-patient-header">
              <div>
                <span className="section-eyebrow">
                  Doctor Management
                </span>

                <h2>
                  ค้นหาแพทย์
                </h2>

                <p>
                  ค้นหาจากชื่อแพทย์
                  หรือ Username
                </p>
              </div>
            </div>

            <div
              style={{
                padding:
                  "22px 24px 24px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  gap: "10px",
                  alignItems: "center",
                  flexWrap: "wrap",
                }}
              >
                <input
                  type="text"
                  value={search}
                  placeholder="ค้นหาชื่อแพทย์ หรือ Username"
                  onChange={(event) =>
                    handleSearchChange(
                      event.target.value,
                    )
                  }
                  onKeyDown={(event) => {
                    if (
                      event.key ===
                      "Enter"
                    ) {
                      handleSearch();
                    }
                  }}
                  style={{
                    flex: "1 1 360px",
                    minWidth: 0,
                    height: "42px",
                    boxSizing:
                      "border-box",
                    padding:
                      "0 12px",
                    border:
                      "1px solid var(--border)",
                    borderRadius:
                      "7px",
                    outline: "none",
                    background:
                      "var(--surface)",
                    color:
                      "var(--text)",
                    fontFamily:
                      "var(--font)",
                    fontSize:
                      "14px",
                  }}
                />

                <button
                  type="button"
                  className="action-button primary"
                  onClick={
                    handleSearch
                  }
                >
                  ค้นหา
                </button>

                {search && (
                  <button
                    type="button"
                    className="action-button secondary"
                    onClick={
                      handleClearSearch
                    }
                  >
                    ล้าง
                  </button>
                )}
              </div>

              <div
                style={{
                  marginTop: "14px",
                  display: "flex",
                  justifyContent:
                    "flex-start",
                }}
              >
                <button
                  type="button"
                  className="action-button secondary"
                  onClick={
                    handleToggleInactive
                  }
                >
                  {showInactive
                    ? "แสดงแพทย์ที่ใช้งาน"
                    : "แสดงแพทย์ที่ปิดใช้งาน"}
                </button>
              </div>
            </div>
          </div>
        </section>

        {errorMessage && (
          <div
            className="doctor-alert"
            role="alert"
          >
            {errorMessage}
          </div>
        )}

        {/* =========================
            Doctor List
        ========================== */}
        <section className="current-patient-section">
          <div className="current-patient-card">
            <div className="current-patient-header">
              <div>
                <span className="section-eyebrow">
                  Doctor List
                </span>

                <h2>
                  {search
                    ? "ผลการค้นหาแพทย์"
                    : showInactive
                      ? "แพทย์ที่ปิดใช้งาน"
                      : "แพทย์ที่เพิ่มล่าสุด"}
                </h2>

                <p>
                  {doctors.length}{" "}
                  รายการ
                </p>
              </div>
            </div>

            {isLoading ? (
              <div
                style={{
                  padding:
                    "32px 24px",
                  textAlign:
                    "center",
                  color:
                    "var(--muted)",
                  fontSize:
                    "14px",
                  fontWeight: 400,
                }}
              >
                กำลังโหลดรายการแพทย์...
              </div>
            ) : doctors.length ===
              0 ? (
              <div
                style={{
                  padding:
                    "32px 24px",
                  textAlign:
                    "center",
                  color:
                    "var(--muted)",
                  fontSize:
                    "14px",
                  fontWeight: 400,
                }}
              >
                {search
                  ? "ไม่พบแพทย์ที่ตรงกับการค้นหา"
                  : showInactive
                    ? "ไม่มีแพทย์ที่ปิดใช้งาน"
                    : "ยังไม่มีข้อมูลแพทย์"}
              </div>
            ) : (
              <div
                style={{
                  display: "flex",
                  flexDirection:
                    "column",
                }}
              >
                {doctors.map(
                  (doctor) => (
                    <article
                      key={doctor.id}
                      style={{
                        display:
                          "flex",
                        alignItems:
                          "center",
                        justifyContent:
                          "space-between",
                        gap: "24px",
                        padding:
                          "18px 24px",
                        borderTop:
                          "1px solid var(--border)",
                      }}
                    >
                      <div
                        style={{
                          minWidth: 0,
                          flex: 1,
                        }}
                      >
                        <strong
                          style={{
                            display:
                              "block",
                            color:
                              "var(--text)",
                            fontSize:
                              "15px",
                            fontWeight:
                              600,
                            marginBottom:
                              "8px",
                          }}
                        >
                          {getDoctorName(
                            doctor,
                          )}
                        </strong>

                        <div
                          style={{
                            display:
                              "flex",
                            flexWrap:
                              "wrap",
                            gap:
                              "6px 22px",
                            color:
                              "var(--muted)",
                            fontSize:
                              "13px",
                            lineHeight:
                              "1.6",
                            fontWeight:
                              400,
                          }}
                        >
                          <span>
                            แผนก:{" "}
                            {
                              doctor
                                .department
                                .name
                            }
                          </span>

                          <span>
                            ความเชี่ยวชาญ:{" "}
                            {doctor.specializations
                              .map(
                                (
                                  specialization,
                                ) =>
                                  specialization.name,
                              )
                              .join(
                                ", ",
                              ) ||
                              "ไม่ระบุ"}
                          </span>
                        </div>
                      </div>

                      <div
                        style={{
                          display:
                            "flex",
                          gap: "8px",
                          flexShrink: 0,
                        }}
                      >
                        {doctor.status !==
                          "inactive" && (
                          <>
                            <button
                              type="button"
                              className="action-button secondary"
                              onClick={() =>
                                navigate(
                                  `/staff/doctors/edit?doctor_id=${doctor.id}`,
                                )
                              }
                            >
                              แก้ไข
                            </button>

                            <button
                              type="button"
                              className="action-button secondary"
                              onClick={() =>
                                navigate(
                                  `/staff/doctors/schedule?doctor_id=${doctor.id}`,
                                )
                              }
                            >
                              ตารางเวลา
                            </button>

                            <button
                              type="button"
                              className="action-button danger"
                              onClick={() =>
                                handleOpenDeactivate(
                                  doctor,
                                )
                              }
                            >
                              ปิดใช้งาน
                            </button>
                          </>
                        )}

                        {doctor.status ===
                          "inactive" && (
                          <button
                            type="button"
                            className="action-button primary"
                            onClick={() =>
                              handleOpenReactivate(
                                doctor,
                              )
                            }
                          >
                            เปิดใช้งาน
                          </button>
                        )}
                      </div>
                    </article>
                  ),
                )}
              </div>
            )}
          </div>
        </section>
      </section>

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
          Deactivate Doctor Modal
      ========================== */}
      {selectedDeactivateDoctor && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={
            handleCloseDeactivate
          }
        >
         <div
          className="doctor-modal doctor-action-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="reactivate-doctor-title"
          onClick={(event) =>
            event.stopPropagation()
          }
          style={{
            width: "calc(100% - 32px)",
            maxWidth: "520px",
          }}
        >
          
            <div className="doctor-modal-icon warning">
              <AlertTriangle
                size={20}
              />
            </div>

            <h2 id="deactivate-doctor-title">
              ปิดใช้งานแพทย์
            </h2>

            <p>
              ต้องการปิดใช้งานแพทย์{" "}
              <span
                style={{
                  fontWeight: 500,
                }}
              >
                {getDoctorName(
                  selectedDeactivateDoctor,
                )}
              </span>{" "}
              ใช่หรือไม่?
            </p>

            <form
              onSubmit={(event) => {
                event.preventDefault();
                void handleDeactivate();
              }}
            >
              <div className="doctor-action-modal-field">
                <label htmlFor="deactivate-doctor-password">
                  ยืนยันรหัสผ่าน Staff
                </label>

                <input
                  id="deactivate-doctor-password"
                  type="password"
                  value={
                    deactivatePassword
                  }
                  placeholder="กรอกรหัสผ่าน"
                  disabled={
                    deactivating
                  }
                  autoComplete="current-password"
                  onChange={(event) => {
                    setDeactivatePassword(
                      event.target.value,
                    );

                    setDeactivateError(
                      "",
                    );
                  }}
                />
              </div>

              {deactivateError && (
                <p
                  className="doctor-action-modal-error"
                  role="alert"
                >
                  {deactivateError}
                </p>
              )}

              <div className="doctor-action-modal-actions">
                <button
                  type="submit"
                  className="action-button danger"
                  disabled={
                    deactivating
                  }
                >
                  {deactivating
                    ? "กำลังปิดใช้งาน..."
                    : "ยืนยันการปิดใช้งาน"}
                </button>

                <button
                  type="button"
                  className="action-button secondary"
                  onClick={
                    handleCloseDeactivate
                  }
                  disabled={
                    deactivating
                  }
                >
                  ยกเลิก
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =========================
          Reactivate Doctor Modal
      ========================== */}
      {selectedDoctor && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={
            handleCloseReactivate
          }
        >
          <div
            className="doctor-modal doctor-action-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="deactivate-doctor-title"
            onClick={(event) =>
              event.stopPropagation()
            }
            style={{
              width: "calc(100% - 32px)",
              maxWidth: "520px",
            }}
          >
            <div className="doctor-modal-icon warning">
              ↻
            </div>

            <h2 id="reactivate-doctor-title">
              เปิดใช้งานแพทย์
            </h2>

            <p>
              ต้องการเปิดใช้งานแพทย์{" "}
              <span
                style={{
                  fontWeight: 500,
                }}
              >
                {getDoctorName(
                  selectedDoctor,
                )}
              </span>{" "}
              ใช่หรือไม่?
            </p>

            <div className="doctor-action-modal-field">
              <label htmlFor="reactivate-doctor-password">
                ยืนยันรหัสผ่าน Staff
              </label>

              <input
                id="reactivate-doctor-password"
                type="password"
                value={password}
                placeholder="กรอกรหัสผ่าน"
                disabled={reactivating}
                autoComplete="current-password"
                onChange={(event) => {
                  setPassword(
                    event.target.value,
                  );

                  setReactivateError(
                    "",
                  );
                }}
                onKeyDown={(event) => {
                  if (
                    event.key ===
                    "Enter"
                  ) {
                    event.preventDefault();
                    void handleReactivate();
                  }
                }}
              />
            </div>

            {reactivateError && (
              <p
                className="doctor-action-modal-error"
                role="alert"
              >
                {reactivateError}
              </p>
            )}

            <div className="doctor-action-modal-actions">
              <button
                type="button"
                className="action-button primary"
                onClick={() =>
                  void handleReactivate()
                }
                disabled={
                  reactivating
                }
              >
                {reactivating
                  ? "กำลังเปิดใช้งาน..."
                  : "ยืนยันการเปิดใช้งาน"}
              </button>

              <button
                type="button"
                className="action-button secondary"
                onClick={
                  handleCloseReactivate
                }
                disabled={
                  reactivating
                }
              >
                ยกเลิก
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export default DoctorListPage;