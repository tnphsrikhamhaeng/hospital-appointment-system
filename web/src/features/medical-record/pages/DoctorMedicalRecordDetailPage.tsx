import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  getDoctorMedicalHistory,
  getMedicalRecord,
  type MedicalRecord,
} from "../api/medicalRecordApi";
import api from "../../../api/axios";
import { logout } from "../../auth/api/authApi";
import ChangePasswordModal from "../../profile/components/ChangePasswordModal";
import "../../doctor/pages/DoctorPage.css";
import "./DoctorMedicalRecordDetailPage.css";

interface DoctorProfile {
  id: string;
  first_name: string;
  last_name: string;
}

function formatThaiDate(dateString: string) {
  return new Intl.DateTimeFormat("th-TH", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(dateString));
}

function DetailSection({
  title,
  value,
}: {
  title: string;
  value: string | null;
}) {
  return (
    <section className="medical-detail-section">
      <h3>{title}</h3>

      <div className="medical-detail-value">
        {value?.trim() ? value : "-"}
      </div>
    </section>
  );
}

export default function DoctorMedicalRecordDetailPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const medicalRecordId =
    searchParams.get("medical_record_id");

  const [record, setRecord] =
    useState<MedicalRecord | null>(null);

  const [patientName, setPatientName] =
    useState("-");

  const [doctorName, setDoctorName] =
    useState("-");

  const [appointmentDate, setAppointmentDate] =
    useState("-");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [isLogoutOpen, setIsLogoutOpen] =
    useState(false);

  const [isChangePasswordOpen, setIsChangePasswordOpen] =
    useState(false);

  useEffect(() => {
    const loadMedicalRecord = async () => {
      if (!medicalRecordId) {
        setError("ไม่พบรหัสข้อมูลการรักษา");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const [
          recordData,
          historyData,
          profileResponse,
        ] = await Promise.all([
          getMedicalRecord(medicalRecordId),
          getDoctorMedicalHistory(),
          api.get<DoctorProfile>("/profile"),
        ]);

        setRecord(recordData);

        const historyItem = historyData.find(
          (item) =>
            item.medical_record?.id ===
            recordData.id,
        );

        if (historyItem) {
          setPatientName(
            historyItem.patient_name,
          );

          setAppointmentDate(
            formatThaiDate(
              historyItem.appointment_date,
            ),
          );
        }

        const doctor = profileResponse.data;

        setDoctorName(
          `${doctor.first_name} ${doctor.last_name}`.trim(),
        );
      } catch {
        setError(
          "ไม่สามารถโหลดรายละเอียดการรักษาได้",
        );
      } finally {
        setLoading(false);
      }
    };

    void loadMedicalRecord();
  }, [medicalRecordId]);

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
            className="sidebar-nav-item"
            onClick={() =>
              navigate("/doctor")
            }
          >
            <span className="nav-icon">⌂</span>
            <span>หน้าหลัก</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item active"
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
            onClick={
              handleOpenChangePassword
            }
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

      {/* =========================
          Main Content
      ========================== */}
      <section className="doctor-main">
        <header className="doctor-header">
          <div>
            <span className="page-eyebrow">
              CareFlow Hospital System
            </span>

            <h1>รายละเอียดการรักษา</h1>

            <p>
              ตรวจสอบรายละเอียดการรักษาและข้อมูลทางการแพทย์ของผู้ป่วย
            </p>
          </div>

          <div className="doctor-header-right">
            <div className="today-date">
              <span>วันนี้</span>

              <strong>
                {formatThaiDate(
                  new Date().toISOString(),
                )}
              </strong>
            </div>
          </div>
        </header>

        <div className="medical-detail-content">
          <button
            type="button"
            className="medical-detail-back-button"
            onClick={() =>
              navigate("/doctor/history")
            }
          >
            <span
              className="back-arrow"
              aria-hidden="true"
            >
              ←
            </span>

            <span>
              กลับประวัติการรักษา
            </span>
          </button>

          {loading && (
            <div className="medical-detail-card">
              <div className="medical-detail-state">
                กำลังโหลดข้อมูลการรักษา...
              </div>
            </div>
          )}

          {!loading && error && (
            <div className="medical-detail-card">
              <div className="medical-detail-state medical-detail-error">
                {error}
              </div>
            </div>
          )}

          {!loading &&
            !error &&
            record && (
              <>
                <div className="medical-detail-card">
                  <div className="medical-detail-card-header">
                    <div>
                      <span className="medical-detail-eyebrow">
                        MEDICAL RECORD
                      </span>

                      <h2>
                        ข้อมูลการรักษา
                      </h2>
                    </div>
                  </div>

                  <div className="medical-detail-info-grid">
                    <div>
                      <span>ชื่อผู้ป่วย</span>

                      <strong>
                        {patientName}
                      </strong>
                    </div>

                    <div>
                      <span>ชื่อแพทย์</span>

                      <strong>
                        {doctorName}
                      </strong>
                    </div>

                    <div>
                      <span>วันที่ตรวจ</span>

                      <strong>
                        {appointmentDate}
                      </strong>
                    </div>

                    <div>
                      <span>
                        รหัสเวชระเบียน
                      </span>

                      <strong>
                        {record.id}
                      </strong>
                    </div>
                  </div>
                </div>

                <div className="medical-detail-card">
                  <h2 className="medical-detail-title">
                    รายละเอียดการตรวจรักษา
                  </h2>

                  <div className="medical-detail-sections">
                    <DetailSection
                      title="อาการสำคัญ (Chief Complaint)"
                      value={
                        record.chief_complaint
                      }
                    />

                    <DetailSection
                      title="ประวัติการเจ็บป่วยปัจจุบัน"
                      value={
                        record.present_illness
                      }
                    />

                    <DetailSection
                      title="ผลการตรวจร่างกาย"
                      value={
                        record.physical_examination
                      }
                    />

                    <DetailSection
                      title="การวินิจฉัย"
                      value={
                        record.diagnosis
                      }
                    />

                    <DetailSection
                      title="การรักษา"
                      value={
                        record.treatment
                      }
                    />

                    <DetailSection
                      title="คำแนะนำ"
                      value={
                        record.recommendation
                      }
                    />

                    <DetailSection
                      title="หมายเหตุ"
                      value={record.note}
                    />
                  </div>
                </div>
              </>
            )}
        </div>
      </section>
    </main>
  );
}