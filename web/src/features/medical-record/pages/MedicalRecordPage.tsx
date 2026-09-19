import { useState, type FormEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  createMedicalRecord,
  type MedicalRecordCreateRequest,
} from "../api/medicalRecordApi";
import { logout } from "../../auth/api/authApi";
import ChangePasswordModal from "../../profile/components/ChangePasswordModal";
import "../../doctor/pages/DoctorPage.css";
import "./MedicalRecordPage.css";

function formatThaiDate() {
  return new Intl.DateTimeFormat("th-TH", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date());
}

function MedicalRecordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const appointmentId =
    searchParams.get("appointment_id");

  const [formData, setFormData] = useState<
    Omit<MedicalRecordCreateRequest, "appointment_id">
  >({
    chief_complaint: "",
    present_illness: null,
    physical_examination: null,
    diagnosis: "",
    treatment: null,
    recommendation: null,
    note: null,
  });

  const [isSaving, setIsSaving] =
    useState(false);

  const [errorMessage, setErrorMessage] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  const [isLogoutOpen, setIsLogoutOpen] =
    useState(false);

  const [isChangePasswordOpen, setIsChangePasswordOpen] =
    useState(false);

  const handleChange = (
    field: keyof Omit<
      MedicalRecordCreateRequest,
      "appointment_id"
    >,
    value: string,
  ) => {
    setFormData((current) => ({
      ...current,
      [field]: value || null,
    }));

    setErrorMessage("");
    setSuccessMessage("");
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (!appointmentId) {
      setErrorMessage("ไม่พบรหัสนัดหมาย");
      return;
    }

    if (!formData.chief_complaint?.trim()) {
      setErrorMessage(
        "กรุณากรอกอาการสำคัญ",
      );
      return;
    }

    if (!formData.diagnosis?.trim()) {
      setErrorMessage(
        "กรุณากรอกการวินิจฉัย",
      );
      return;
    }

    setIsSaving(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      await createMedicalRecord({
        appointment_id: appointmentId,
        chief_complaint:
          formData.chief_complaint.trim(),
        present_illness:
          formData.present_illness?.trim() ||
          null,
        physical_examination:
          formData.physical_examination?.trim() ||
          null,
        diagnosis:
          formData.diagnosis.trim(),
        treatment:
          formData.treatment?.trim() ||
          null,
        recommendation:
          formData.recommendation?.trim() ||
          null,
        note:
          formData.note?.trim() || null,
      });

      setSuccessMessage(
        "บันทึกผลการรักษาสำเร็จ",
      );

      setFormData({
        chief_complaint: "",
        present_illness: null,
        physical_examination: null,
        diagnosis: "",
        treatment: null,
        recommendation: null,
        note: null,
      });
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
          response?.data?.detail ??
            "ไม่สามารถบันทึกผลการรักษาได้",
        );
      } else {
        setErrorMessage(
          "ไม่สามารถบันทึกผลการรักษาได้",
        );
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleOpenLogout = () => {
    setIsLogoutOpen(true);
  };

  const handleCloseLogout = () => {
    setIsLogoutOpen(false);
  };

  const handleConfirmLogout = () => {
    logout();
    setIsLogoutOpen(false);
    navigate("/login", {
      replace: true,
    });
  };

  const handleOpenChangePassword = () => {
    setIsChangePasswordOpen(true);
  };

  const handleCloseChangePassword = () => {
    setIsChangePasswordOpen(false);
  };

  const renderSidebar = () => (
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
          <span className="nav-icon">
            ⌂
          </span>

          <span>หน้าหลัก</span>
        </button>

        <button
          type="button"
          className="sidebar-nav-item"
          onClick={() =>
            navigate("/doctor/history")
          }
        >
          <span className="nav-icon">
            ▤
          </span>

          <span>ประวัติการรักษา</span>
        </button>

        <button
          type="button"
          className="sidebar-nav-item"
          onClick={() =>
            navigate("/doctor/schedule")
          }
        >
          <span className="nav-icon">
            ▦
          </span>

          <span>ตารางนัดหมาย</span>
        </button>
      </nav>

      <div className="sidebar-bottom">
        <button
          type="button"
          className="sidebar-bottom-item"
          onClick={
            handleOpenChangePassword
          }
        >
          <span className="nav-icon">
            ⚿
          </span>

          <span>เปลี่ยนรหัสผ่าน</span>
        </button>

        <button
          type="button"
          className="sidebar-bottom-item logout-item"
          onClick={handleOpenLogout}
        >
          <span className="nav-icon">
            ↪
          </span>

          <span>ออกจากระบบ</span>
        </button>
      </div>
    </aside>
  );

  return (
    <main className="doctor-page">
      {renderSidebar()}

      {/* =========================
          Logout Confirmation Modal
      ========================== */}
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

      {/* =========================
          Change Password Modal
      ========================== */}
      <ChangePasswordModal
        isOpen={isChangePasswordOpen}
        onClose={
          handleCloseChangePassword
        }
      />

      <section className="doctor-content">
        <header className="doctor-header">
          <div>
            <span className="page-eyebrow">
              CareFlow Hospital System
            </span>

            <h1>บันทึกผลการรักษา</h1>

            <p>
              บันทึกข้อมูลการตรวจรักษาและผลการวินิจฉัย
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

        {!appointmentId ? (
          <div className="medical-record-empty">
            <h1>
              ไม่พบข้อมูลนัดหมาย
            </h1>

            <p role="alert">
              ไม่พบรหัสนัดหมายสำหรับบันทึกผลการรักษา
            </p>

            <button
              type="button"
              className="medical-record-back-button"
              onClick={() =>
                navigate("/doctor")
              }
            >
              <span className="back-arrow">
                ←
              </span>

              <span>
                กลับหน้าหลัก
              </span>
            </button>
          </div>
        ) : (
          <div className="medical-record-content">
            <button
              type="button"
              className="medical-record-back-button"
              onClick={() =>
                navigate("/doctor")
              }
            >
              <span
                className="back-arrow"
                aria-hidden="true"
              >
                ←
              </span>

              <span>
                กลับหน้าหลัก
              </span>
            </button>

            <form
              className="medical-record-form-card"
              onSubmit={handleSubmit}
            >
              <div className="medical-record-card-header">
                <span className="medical-record-eyebrow">
                  MEDICAL RECORD
                </span>

                <h2>
                  ข้อมูลการรักษา
                </h2>

                <p>
                  กรุณากรอกข้อมูลการตรวจรักษาให้ครบถ้วน
                </p>
              </div>

              <div className="medical-record-form">
                <div className="medical-record-field medical-record-field-full">
                  <label htmlFor="chief_complaint">
                    อาการสำคัญ{" "}
                    <span>*</span>
                  </label>

                  <textarea
                    id="chief_complaint"
                    value={
                      formData.chief_complaint
                    }
                    onChange={(event) =>
                      handleChange(
                        "chief_complaint",
                        event.target.value,
                      )
                    }
                    placeholder="ระบุอาการสำคัญของผู้ป่วย"
                    required
                  />
                </div>

                <div className="medical-record-field">
                  <label htmlFor="present_illness">
                    ประวัติอาการปัจจุบัน
                  </label>

                  <textarea
                    id="present_illness"
                    value={
                      formData.present_illness ??
                      ""
                    }
                    onChange={(event) =>
                      handleChange(
                        "present_illness",
                        event.target.value,
                      )
                    }
                    placeholder="ระบุประวัติอาการหรือการเจ็บป่วยปัจจุบัน"
                  />
                </div>

                <div className="medical-record-field">
                  <label htmlFor="physical_examination">
                    ผลการตรวจร่างกาย
                  </label>

                  <textarea
                    id="physical_examination"
                    value={
                      formData.physical_examination ??
                      ""
                    }
                    onChange={(event) =>
                      handleChange(
                        "physical_examination",
                        event.target.value,
                      )
                    }
                    placeholder="ระบุผลการตรวจร่างกาย"
                  />
                </div>

                <div className="medical-record-field medical-record-field-full">
                  <label htmlFor="diagnosis">
                    การวินิจฉัย{" "}
                    <span>*</span>
                  </label>

                  <textarea
                    id="diagnosis"
                    value={
                      formData.diagnosis
                    }
                    onChange={(event) =>
                      handleChange(
                        "diagnosis",
                        event.target.value,
                      )
                    }
                    placeholder="ระบุผลการวินิจฉัย"
                    required
                  />
                </div>

                <div className="medical-record-field medical-record-field-full">
                  <label htmlFor="treatment">
                    การรักษา
                  </label>

                  <textarea
                    id="treatment"
                    value={
                      formData.treatment ??
                      ""
                    }
                    onChange={(event) =>
                      handleChange(
                        "treatment",
                        event.target.value,
                      )
                    }
                    placeholder="ระบุรายละเอียดการรักษา"
                  />
                </div>

                <div className="medical-record-field">
                  <label htmlFor="recommendation">
                    คำแนะนำ
                  </label>

                  <textarea
                    id="recommendation"
                    value={
                      formData.recommendation ??
                      ""
                    }
                    onChange={(event) =>
                      handleChange(
                        "recommendation",
                        event.target.value,
                      )
                    }
                    placeholder="ระบุคำแนะนำสำหรับผู้ป่วย"
                  />
                </div>

                <div className="medical-record-field">
                  <label htmlFor="note">
                    หมายเหตุ
                  </label>

                  <textarea
                    id="note"
                    value={
                      formData.note ?? ""
                    }
                    onChange={(event) =>
                      handleChange(
                        "note",
                        event.target.value,
                      )
                    }
                    placeholder="ระบุหมายเหตุเพิ่มเติม"
                  />
                </div>
              </div>

              {(errorMessage ||
                successMessage) && (
                <div
                  className={
                    errorMessage
                      ? "medical-record-message medical-record-message-error"
                      : "medical-record-message medical-record-message-success"
                  }
                  role={
                    errorMessage
                      ? "alert"
                      : "status"
                  }
                >
                  {errorMessage ||
                    successMessage}
                </div>
              )}

              <div className="medical-record-form-actions">
                <button
                  type="button"
                  className="medical-record-cancel-button"
                  onClick={() =>
                    navigate("/doctor")
                  }
                  disabled={isSaving}
                >
                  ยกเลิก
                </button>

                <button
                  type="submit"
                  className="medical-record-submit-button"
                  disabled={isSaving}
                >
                  {isSaving
                    ? "กำลังบันทึก..."
                    : "บันทึกผลการรักษา"}
                </button>
              </div>
            </form>
          </div>
        )}
      </section>
    </main>
  );
}

export default MedicalRecordPage;