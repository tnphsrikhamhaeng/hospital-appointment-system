import { useState, type FormEvent } from "react";
import {
  staffCheckIn,
  staffCheckInPreview,
  type StaffCheckInPreviewResponse,
} from "../../appointment/api/appointmentQrApi";

import "../../doctor/pages/DoctorPage.css";

const checkInModalStyle = `
  .check-in-modal {
    font-weight: 400;
  }

  .check-in-modal h2 {
    font-weight: 500 !important;
  }

  .check-in-modal > p {
    font-weight: 400 !important;
  }

  .check-in-modal-data {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px 18px;
    width: 100%;
    margin-top: 20px;
    padding: 16px;
    box-sizing: border-box;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--surface);
    text-align: left;
  }

  .check-in-modal-data-item {
    min-width: 0;
    font-weight: 400;
  }

  .check-in-modal-data-item.full-width {
    grid-column: 1 / -1;
  }

  .check-in-modal-data-label {
    display: block;
    margin-bottom: 4px;
    color: var(--muted);
    font-size: 12px;
    font-weight: 400 !important;
    line-height: 1.4;
  }

  .check-in-modal-data-value {
    display: block;
    color: var(--text);
    font-size: 14px;
    font-weight: 400 !important;
    line-height: 1.5;
    word-break: break-word;
  }

  .check-in-modal-data-value.patient-name {
    font-size: 15px;
    font-weight: 500 !important;
  }

  .check-in-modal-actions {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 20px;
  }

  .check-in-modal-actions .action-button {
    width: 100%;
    min-height: 42px;
    box-sizing: border-box;
    justify-content: center;
    font-weight: 400 !important;
  }

  @media (max-width: 640px) {
    .check-in-modal-data {
      grid-template-columns: 1fr;
    }

    .check-in-modal-data-item.full-width {
      grid-column: auto;
    }
  }
`;
const translateCheckInError = (message?: string): string => {
  if (!message) {
    return "ไม่สามารถตรวจสอบ QR Token ได้";
  }

  const errorMessages: Record<string, string> = {
    "Appointment QR Code not found.": "ไม่พบ QR Code ของการนัดหมาย",
    "Appointment QR Code not found": "ไม่พบ QR Code ของการนัดหมาย",
  };

  return errorMessages[message] ?? message;
};
function StaffCheckInPage() {
  const [token, setToken] = useState("");
  const [isCheckingIn, setIsCheckingIn] = useState(false);

  const [isPreviewing, setIsPreviewing] = useState(false);

  const [previewData, setPreviewData] =
    useState<StaffCheckInPreviewResponse | null>(null);

  const [errorMessage, setErrorMessage] = useState("");

  const [successMessage, setSuccessMessage] = useState("");

  const handleClosePreview = () => {
    if (isCheckingIn) {
      return;
    }

    setPreviewData(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setErrorMessage("");
    setSuccessMessage("");

    if (!token.trim()) {
      setErrorMessage("กรุณากรอก QR Token");
      return;
    }

    setIsPreviewing(true);

    try {
      const response = await staffCheckInPreview({
        token: token.trim(),
      });

      setPreviewData(response);
    } catch (error: unknown) {
      if (typeof error === "object" && error !== null && "response" in error) {
        const response = (
          error as {
            response?: {
              data?: {
                detail?: string;
              };
            };
          }
        ).response;

        setErrorMessage(translateCheckInError(response?.data?.detail));
      } else {
        setErrorMessage("ไม่สามารถตรวจสอบ QR Token ได้");
      }
    } finally {
      setIsPreviewing(false);
    }
  };

  const handleConfirmCheckIn = async () => {
    if (!previewData || !token.trim()) {
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");
    setIsCheckingIn(true);

    try {
      await staffCheckIn({
        token: token.trim(),
      });

      setSuccessMessage("เช็คอินผู้ป่วยสำเร็จ");
      setToken("");
      setPreviewData(null);
    } catch (error: unknown) {
      if (typeof error === "object" && error !== null && "response" in error) {
        const response = (
          error as {
            response?: {
              data?: {
                detail?: string;
              };
            };
          }
        ).response;

        setErrorMessage(translateCheckInError(response?.data?.detail));
      } else {
        setErrorMessage("ไม่สามารถเช็คอินผู้ป่วยได้");
      }
    } finally {
      setIsCheckingIn(false);
    }
  };

  const formatThaiDate = () => {
    return new Intl.DateTimeFormat("th-TH", {
      day: "numeric",
      month: "long",
      year: "numeric",
    }).format(new Date());
  };

  const formatAppointmentDate = (value: string) => {
    return new Intl.DateTimeFormat("th-TH", {
      day: "numeric",
      month: "long",
      year: "numeric",
    }).format(new Date(`${value}T00:00:00`));
  };

  const formatTime = (value: string) => {
    return value.slice(0, 5);
  };

  return (
    <main className="doctor-page">
      <style>{checkInModalStyle}</style>

      {/* =========================
          Main Content
      ========================== */}
      <section className="doctor-content">
        <header className="doctor-header">
          <div>
            <span className="page-eyebrow">CareFlow Hospital System</span>

            <h1>เช็คอินผู้ป่วย</h1>

            <p>
              รับ QR Code เพื่อยืนยันการมาถึงของผู้ป่วย และเช็คอินการนัดหมาย
            </p>
          </div>

          <div className="doctor-header-right">
            <div className="today-date">
              <span>วันนี้</span>

              <strong>{formatThaiDate()}</strong>
            </div>
          </div>
        </header>

        {errorMessage && (
          <div className="doctor-alert" role="alert">
            {errorMessage}
          </div>
        )}

        {/* =========================
            Check-in Card
        ========================== */}
        <section className="current-patient-section">
          <div className="current-patient-card">
            <div className="current-patient-header">
              <div>
                <span className="section-eyebrow">Patient Check-in</span>

                <h2>ยืนยันการเช็คอินผู้ป่วย</h2>

                <p>
                  กรุณากรอกรหัส QR Token ของการนัดหมาย เพื่อดูข้อมูลก่อนยืนยัน
                  การเช็คอิน
                </p>
              </div>

              <span
                className="status-badge"
                style={{
                  background: "#FFF4D6",
                  color: "#B77900",
                }}
              >
                <span
                  className="status-dot"
                  style={{
                    background: "#E5A900",
                  }}
                />
                รอเช็คอิน
              </span>
            </div>

            <form
              onSubmit={handleSubmit}
              style={{
                padding: "22px 24px 24px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "7px",
                  maxWidth: "620px",
                }}
              >
                <label
                  htmlFor="qr-token"
                  style={{
                    color: "var(--text)",
                    fontSize: "13px",
                    lineHeight: "1.5",
                    fontWeight: 400,
                  }}
                >
                  QR Token
                </label>

                <input
                  id="qr-token"
                  type="text"
                  value={token}
                  onChange={(event) => {
                    setToken(event.target.value);
                    setErrorMessage("");
                    setSuccessMessage("");
                    setPreviewData(null);
                  }}
                  placeholder="เช่น CF-ABCD-23"
                  disabled={isPreviewing || isCheckingIn}
                  autoComplete="off"
                  style={{
                    width: "100%",
                    height: "42px",
                    boxSizing: "border-box",
                    padding: "0 12px",
                    border: "1px solid var(--border)",
                    borderRadius: "7px",
                    outline: "none",
                    background: "var(--surface)",
                    color: "var(--text)",
                    fontFamily: "var(--font)",
                    fontSize: "14px",
                  }}
                />
              </div>

              {successMessage && (
                <p
                  role="status"
                  style={{
                    margin: "14px 0 0",
                    padding: "10px 12px",
                    border: "1px solid #c9e8d8",
                    borderRadius: "7px",
                    background: "var(--success-bg)",
                    color: "var(--success)",
                    fontSize: "13px",
                    lineHeight: "1.5",
                    fontWeight: 400,
                  }}
                >
                  {successMessage}
                </p>
              )}

              <div
                className="doctor-modal-actions"
                style={{
                  justifyContent: "flex-start",
                  marginTop: "18px",
                }}
              >
                <button
                  type="submit"
                  className="action-button primary"
                  disabled={isPreviewing || isCheckingIn}
                  style={{
                    fontWeight: 400,
                  }}
                >
                  {isPreviewing ? "กำลังตรวจสอบ..." : "ตรวจสอบ QR"}
                </button>
              </div>
            </form>
          </div>
        </section>
      </section>

      {/* =========================
          Check-in Confirmation Modal
      ========================== */}
      {previewData && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={handleClosePreview}
        >
          <div
            className="doctor-modal check-in-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="check-in-modal-title"
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "calc(100% - 32px)",
              maxWidth: "520px",
              fontWeight: 400,
            }}
          >
            <div className="doctor-modal-icon warning">✓</div>

            <h2 id="check-in-modal-title">ยืนยันการเช็คอิน</h2>

            <p>กรุณาตรวจสอบข้อมูล ก่อนยืนยันการเช็คอินผู้ป่วย</p>

            <div className="check-in-modal-data">
              <div className="check-in-modal-data-item full-width">
                <span className="check-in-modal-data-label">ผู้ป่วย</span>

                <span className="check-in-modal-data-value patient-name">
                  {previewData.patient_name}
                </span>
              </div>

              <div className="check-in-modal-data-item">
                <span className="check-in-modal-data-label">วันที่นัดหมาย</span>

                <span className="check-in-modal-data-value">
                  {formatAppointmentDate(previewData.appointment_date)}
                </span>
              </div>

              <div className="check-in-modal-data-item">
                <span className="check-in-modal-data-label">เวลานัดหมาย</span>

                <span className="check-in-modal-data-value">
                  {formatTime(previewData.start_time)} -{" "}
                  {formatTime(previewData.end_time)} น.
                </span>
              </div>

              <div className="check-in-modal-data-item">
                <span className="check-in-modal-data-label">แพทย์</span>

                <span className="check-in-modal-data-value">
                  {previewData.doctor_name}
                </span>
              </div>

              <div className="check-in-modal-data-item">
                <span className="check-in-modal-data-label">แผนก</span>

                <span className="check-in-modal-data-value">
                  {previewData.department_name}
                </span>
              </div>
            </div>

            <div className="check-in-modal-actions">
              <button
                type="button"
                className="action-button primary"
                onClick={handleConfirmCheckIn}
                disabled={isCheckingIn}
              >
                {isCheckingIn ? "กำลัง Check-in..." : "ยืนยัน Check-in"}
              </button>

              <button
                type="button"
                className="action-button secondary"
                onClick={handleClosePreview}
                disabled={isCheckingIn}
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

export default StaffCheckInPage;
