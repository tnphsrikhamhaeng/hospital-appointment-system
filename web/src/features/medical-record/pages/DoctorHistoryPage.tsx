import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import {
  getDoctorMedicalHistory,
  type DoctorMedicalHistory,
} from "../api/medicalRecordApi";
import { logout } from "../../auth/api/authApi";
import ChangePasswordModal from "../../profile/components/ChangePasswordModal";
import "../../doctor/pages/DoctorPage.css";
import "./DoctorHistoryPage.css";

type HistoryStatus = "all" | "completed" | "no_show";

function DoctorHistoryPage() {
  const navigate = useNavigate();

  const formatThaiDate = () => {
    return new Intl.DateTimeFormat("th-TH", {
      day: "numeric",
      month: "long",
      year: "numeric",
    }).format(new Date());
  };

  const [history, setHistory] = useState<DoctorMedicalHistory[]>([]);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [statusFilter, setStatusFilter] =
    useState<HistoryStatus>("all");

  const [isLogoutOpen, setIsLogoutOpen] =
    useState(false);

  const [isChangePasswordOpen, setIsChangePasswordOpen] =
    useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const loadHistory = async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const data = await getDoctorMedicalHistory({
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      });

      setHistory(data);
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
            "ไม่สามารถโหลดประวัติการรักษาได้",
        );
      } else {
        setErrorMessage(
          "ไม่สามารถโหลดประวัติการรักษาได้",
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadHistory();
  }, []);

  const filteredHistory = useMemo(() => {
    if (statusFilter === "all") {
      return history;
    }

    return history.filter(
      (item) => item.status === statusFilter,
    );
  }, [history, statusFilter]);

  const formatDate = (value: string) => {
    return new Date(
      `${value}T00:00:00`,
    ).toLocaleDateString("th-TH", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
  };

  const formatTime = (value: string) => {
    return value.slice(0, 5);
  };

  const getStatusLabel = (status: string) => {
    if (status === "completed") {
      return "เสร็จสิ้น";
    }

    if (status === "no_show") {
      return "ไม่มาตามนัด";
    }

    return status;
  };

  const getStatusClass = (status: string) => {
    if (status === "completed") {
      return "status-completed";
    }

    if (status === "no_show") {
      return "status-no-show";
    }

    return "";
  };

  const handleFilter = (event: FormEvent) => {
    event.preventDefault();

    if (dateFrom && dateTo && dateFrom > dateTo) {
      setErrorMessage(
        "วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด",
      );
      return;
    }

    void loadHistory();
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
    navigate("/login", { replace: true });
  };

  const handleOpenChangePassword = () => {
    setIsChangePasswordOpen(true);
  };

  const handleCloseChangePassword = () => {
    setIsChangePasswordOpen(false);
  };

  return (
    <main className="doctor-history-page">
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
            onClick={() => navigate("/doctor")}
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
        onClose={handleCloseChangePassword}
      />

      {/* =========================
          Main Content
      ========================== */}
      <section className="doctor-history-content">
        <header className="doctor-history-header">
          <div>
            <span className="page-eyebrow">
              CareFlow Hospital System
            </span>

            <h1>ประวัติการรักษา</h1>

            <p>
              ตรวจสอบประวัติการรักษา
              ของผู้ป่วยที่อยู่ในความรับผิดชอบ
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
            className="doctor-history-alert"
            role="alert"
          >
            {errorMessage}
          </div>
        )}

        {/* =========================
            Date Filter
        ========================== */}
        <section className="history-filter-card">
          <div className="history-card-header">
            <div>
              <span className="section-eyebrow">
                Filter
              </span>

              <h2>ค้นหาประวัติการรักษา</h2>

              <p>
                เลือกช่วงวันที่ที่ต้องการตรวจสอบ
              </p>
            </div>

            <span className="history-count">
              {filteredHistory.length} รายการ
            </span>
          </div>

          <form
            className="history-filter-form"
            onSubmit={handleFilter}
          >
            <div className="history-filter-field">
              <label htmlFor="date_from">
                ตั้งแต่วันที่
              </label>

              <input
                id="date_from"
                type="date"
                value={dateFrom}
                onChange={(event) =>
                  setDateFrom(event.target.value)
                }
              />
            </div>

            <div className="history-filter-field">
              <label htmlFor="date_to">
                ถึงวันที่
              </label>

              <input
                id="date_to"
                type="date"
                value={dateTo}
                onChange={(event) =>
                  setDateTo(event.target.value)
                }
              />
            </div>

            <button
              type="submit"
              className="history-search-button"
              disabled={isLoading}
            >
              {isLoading
                ? "กำลังโหลด..."
                : "ค้นหา"}
            </button>
          </form>
        </section>

        {/* =========================
            Status Filter
        ========================== */}
        <section className="history-status-section">
          <div className="history-status-header">
            <div>
              <span className="section-eyebrow">
                Status
              </span>

              <h2 className="history-status-title">
                สถานะประวัติ
              </h2>
            </div>

            <div className="history-status-buttons">
              {(
                [
                  ["all", "ทั้งหมด"],
                  ["completed", "เสร็จสิ้น"],
                  ["no_show", "ไม่มาตามนัด"],
                ] as const
              ).map(([filter, label]) => (
                <button
                  key={filter}
                  type="button"
                  className={
                    statusFilter === filter
                      ? "history-filter-button active"
                      : "history-filter-button"
                  }
                  onClick={() =>
                    setStatusFilter(filter)
                  }
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* =========================
            History Table
        ========================== */}
        <section className="history-table-card">
          <div className="history-card-header">
            <div>
              <span className="section-eyebrow">
                History
              </span>

              <h2>รายการประวัติการรักษา</h2>

              <p>
                รายการนัดหมายที่เสร็จสิ้น
                หรือผู้ป่วยไม่มาตามนัด
              </p>
            </div>

            <span className="history-count">
              {filteredHistory.length} รายการ
            </span>
          </div>

          {isLoading ? (
            <div className="history-empty-state">
              <div className="loading-spinner" />

              <p>
                กำลังโหลดประวัติการรักษา...
              </p>
            </div>
          ) : filteredHistory.length === 0 ? (
            <div className="history-empty-state">
              <div className="history-empty-icon">
                ▤
              </div>

              <h3>
                ไม่พบประวัติการรักษา
              </h3>

              <p>
                ลองเปลี่ยนช่วงวันที่
                หรือสถานะที่ต้องการค้นหา
              </p>
            </div>
          ) : (
            <div className="history-table-wrapper">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>วันที่</th>
                    <th>เวลา</th>
                    <th>ผู้ป่วย</th>
                    <th>สถานะ</th>
                    <th>การดำเนินการ</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredHistory.map((item) => (
                    <tr
                      key={item.appointment_id}
                    >
                      <td>
                        <span className="history-date">
                          {formatDate(
                            item.appointment_date,
                          )}
                        </span>
                      </td>

                      <td>
                        <div className="history-time">
                          <strong>
                            {formatTime(
                              item.start_time,
                            )}
                          </strong>

                          <span>-</span>

                          <span>
                            {formatTime(
                              item.end_time,
                            )}
                          </span>
                        </div>
                      </td>

                      <td>
                        <div className="history-patient-cell">
                          <span className="history-patient-avatar">
                            {item.patient_name.charAt(
                              0,
                            )}
                          </span>

                          <div>
                            <strong>
                              {item.patient_name}
                            </strong>
                          </div>
                        </div>
                      </td>

                      <td>
                        <span
                          className={`status-badge ${getStatusClass(
                            item.status,
                          )}`}
                        >
                          <span className="status-dot" />

                          {getStatusLabel(
                            item.status,
                          )}
                        </span>
                      </td>

                      <td>
                        {item.status === "completed" &&
                        item.medical_record ? (
                          <button
                            type="button"
                            className="history-detail-button"
                            onClick={() =>
                              navigate(
                                `/doctor/history/detail?medical_record_id=${item.medical_record?.id}`,
                              )
                            }
                          >
                            ดูรายละเอียดการรักษา
                          </button>
                        ) : (
                          <span className="history-no-show-label">
                            ไม่มาตามนัด
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!isLoading &&
            filteredHistory.length > 0 && (
              <div className="history-footer">
                <span>
                  แสดง {filteredHistory.length} รายการ
                </span>

                <span className="history-data-status">
                  <span className="history-data-status-dot" />
                  ข้อมูลอัปเดตจากระบบ
                </span>
              </div>
            )}
        </section>
      </section>
    </main>
  );
}

export default DoctorHistoryPage;