import { useEffect, useMemo, useState } from "react";
import {
  cancelAppointment,
  getStaffAppointments,
  sendStaffAppointmentNotification,
  updateAppointmentStatus,
  type Appointment,
} from "../../appointment/api/appointmentApi";
import "../../doctor/pages/DoctorPage.css";

const statusLabels: Record<string, string> = {
  pending: "รอเจ้าหน้าที่ยืนยัน",
  confirmed: "ยืนยันแล้ว",
  checked_in: "เช็คอินแล้ว",
  in_progress: "กำลังตรวจ",
  completed: "เสร็จสิ้น",
  cancelled: "ยกเลิก",
  no_show: "ไม่มาตามนัด",
};

const escapeHtml = (value: unknown) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

function StaffAppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [searchId, setSearchId] = useState("");
  const [filterDate, setFilterDate] = useState("");
  const [rooms, setRooms] = useState<Record<string, string>>({});

  const reload = async () => {
    setLoading(true);
    setError("");
    try {
      setAppointments(await getStaffAppointments());
    } catch {
      setError("โหลดรายการนัดหมายไม่สำเร็จ กรุณาลองใหม่อีกครั้ง");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void reload();
  }, []);

  const filteredAppointments = useMemo(() => {
    const needle = searchId.trim().toLowerCase();
    return [...appointments]
      .filter((item) => !needle || item.id.toLowerCase().includes(needle))
      .filter((item) => !filterDate || item.appointment_date === filterDate)
      .sort((a, b) =>
        a.appointment_date.localeCompare(b.appointment_date) ||
        a.start_time.localeCompare(b.start_time),
      );
  }, [appointments, searchId, filterDate]);

  const updateLocal = (updated: Appointment) => {
    setAppointments((items) =>
      items.map((item) => item.id === updated.id ? updated : item),
    );
  };

  const handleConfirm = async (appointment: Appointment) => {
    setBusyId(appointment.id);
    setError("");
    setNotice("");
    try {
      updateLocal(await updateAppointmentStatus(appointment.id, { status: "confirmed" }));
      setNotice("ยืนยันนัดหมายแล้ว และส่งการแจ้งเตือนไปยังผู้ป่วยแล้ว");
    } catch {
      setError("ยืนยันนัดหมายไม่สำเร็จ");
    } finally {
      setBusyId(null);
    }
  };

  const handleStatus = async (appointment: Appointment, status: "checked_in" | "in_progress") => {
    const room = (rooms[appointment.id] ?? "").trim();
    if (!room) {
      setError("กรุณากรอกเลขห้องก่อนดำเนินการ");
      return;
    }
    setBusyId(appointment.id);
    setError("");
    setNotice("");
    try {
      updateLocal(await updateAppointmentStatus(appointment.id, {
        status,
        room_number: room,
      }));
      setNotice(status === "checked_in"
        ? "เช็คอินสำเร็จ และแจ้งเลขห้องให้ผู้ป่วยแล้ว"
        : "เรียกผู้ป่วยเข้าตรวจและส่งแจ้งเตือนแล้ว");
    } catch {
      setError(status === "checked_in" ? "เช็คอินไม่สำเร็จ" : "เรียกผู้ป่วยไม่สำเร็จ");
    } finally {
      setBusyId(null);
    }
  };

  const handleCancel = async (appointment: Appointment) => {
    const reason = window.prompt("กรอกเหตุผลที่ยกเลิกนัดหมาย เช่น แพทย์ติดเหตุฉุกเฉิน");
    if (reason === null) return;
    if (!reason.trim()) {
      setError("กรุณากรอกเหตุผลการยกเลิก");
      return;
    }
    setBusyId(appointment.id);
    setError("");
    setNotice("");
    try {
      updateLocal(await cancelAppointment(appointment.id, { cancelled_reason: reason.trim() }));
      setNotice("ยกเลิกนัดหมายแล้ว ระบบได้ส่งการแจ้งเตือนไปยังผู้ป่วย");
    } catch {
      setError("ยกเลิกนัดหมายไม่สำเร็จ");
    } finally {
      setBusyId(null);
    }
  };

  const handleNotify = async (appointment: Appointment) => {
    const message = window.prompt("ข้อความที่ต้องการแจ้งผู้ป่วย");
    if (message === null) return;
    if (!message.trim()) {
      setError("กรุณากรอกข้อความแจ้งเตือน");
      return;
    }
    setBusyId(appointment.id);
    setError("");
    setNotice("");
    try {
      await sendStaffAppointmentNotification(appointment.id, message.trim());
      setNotice("ส่งข้อความแจ้งเตือนผู้ป่วยแล้ว");
    } catch {
      setError("ส่งแจ้งเตือนไม่สำเร็จ");
    } finally {
      setBusyId(null);
    }
  };

  const handleExportPdf = () => {
    const popup = window.open("", "_blank", "width=1100,height=800");
    if (!popup) {
      setError("เบราว์เซอร์บล็อกหน้ารายงาน กรุณาอนุญาต Pop-up แล้วลองอีกครั้ง");
      return;
    }
    const rows = filteredAppointments.map((item) => `
      <tr>
        <td>${escapeHtml(item.id)}</td>
        <td>${escapeHtml(item.patient_id)}</td>
        <td>${escapeHtml(item.doctor_id)}</td>
        <td>${escapeHtml(item.department_id)}</td>
        <td>${escapeHtml(item.appointment_date)}</td>
        <td>${escapeHtml(item.start_time.slice(0, 5))} - ${escapeHtml(item.end_time.slice(0, 5))}</td>
        <td>${escapeHtml(item.reason || "-")}</td>
        <td>${escapeHtml(statusLabels[item.status] ?? item.status)}</td>
        <td>${escapeHtml(item.cancelled_reason || "-")}</td>
        <td>${escapeHtml(item.confirmed_at || "-")}</td>
        <td>${escapeHtml(item.cancelled_at || "-")}</td>
        <td>${escapeHtml(item.created_at)}</td>
        <td>${escapeHtml(item.updated_at)}</td>
      </tr>`).join("");
    popup.document.write(`<!doctype html><html lang="th"><head><meta charset="utf-8">
      <title>รายงานนัดหมาย CareFlow</title>
      <style>
        body{font-family:Arial,sans-serif;padding:24px;color:#172033}
        h1{font-size:22px;margin-bottom:6px}p{font-size:12px;color:#555}
        table{border-collapse:collapse;width:100%;font-size:10px;table-layout:fixed}
        th,td{border:1px solid #bbb;padding:6px;overflow-wrap:anywhere;text-align:left}
        th{background:#eef2f7} @page{size:landscape;margin:12mm}
      </style></head><body>
      <h1>รายงานข้อมูลการนัดหมาย — CareFlow</h1>
      <p>ออกรายงานเมื่อ ${escapeHtml(new Date().toLocaleString("th-TH"))} | จำนวน ${filteredAppointments.length} รายการ</p>
      <table><thead><tr><th>รหัสนัดหมาย</th><th>รหัสผู้ป่วย</th><th>รหัสแพทย์</th><th>รหัสแผนก</th><th>วันที่</th><th>เวลา</th><th>เหตุผลการนัด</th><th>สถานะ</th><th>เหตุผลยกเลิก</th><th>ยืนยันเมื่อ</th><th>ยกเลิกเมื่อ</th><th>สร้างเมื่อ</th><th>แก้ไขล่าสุด</th></tr></thead>
      <tbody>${rows}</tbody></table>
      <script>window.onload=()=>window.print();</script></body></html>`);
    popup.document.close();
  };

  const formatDate = (value: string) => {
    if (!value) return "-";
    return new Intl.DateTimeFormat("th-TH", {
      day: "numeric", month: "short", year: "numeric",
    }).format(new Date(value + "T00:00:00"));
  };

  return (
    <section className="doctor-content">
      <header className="doctor-header">
        <div>
          <span className="page-eyebrow">CareFlow Hospital System</span>
          <h1>จัดการนัดหมาย</h1>
          <p>ตรวจสอบ ยืนยัน เช็คอิน เรียกตรวจ ส่งแจ้งเตือน และยกเลิกนัดหมาย</p>
        </div>
        <div className="doctor-header-right">
          <button type="button" className="action-button primary" onClick={handleExportPdf}>
            ส่งออกรายงาน PDF
          </button>
        </div>
      </header>

      {error && <div className="doctor-alert" role="alert">{error}</div>}
      {notice && <div className="doctor-alert" role="status">{notice}</div>}

      <section className="current-patient-card" style={{ marginBottom: 18 }}>
        <div style={{ display: "flex", gap: 14, flexWrap: "wrap", padding: 20, alignItems: "end" }}>
          <label style={{ display: "grid", gap: 6, minWidth: 220 }}>
            <span>ค้นหาด้วยรหัสนัดหมาย</span>
            <input value={searchId} onChange={(e) => setSearchId(e.target.value)} placeholder="กรอกรหัสนัดหมาย" />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span>กรองตามวันที่</span>
            <input type="date" value={filterDate} onChange={(e) => setFilterDate(e.target.value)} />
          </label>
          <button type="button" className="action-button secondary" onClick={() => { setSearchId(""); setFilterDate(""); }}>
            ล้างตัวกรอง
          </button>
          <button type="button" className="action-button secondary" onClick={() => void reload()}>
            โหลดข้อมูลใหม่
          </button>
        </div>
      </section>

      <section className="current-patient-card">
        <div style={{ padding: 20 }}>
          <h2 style={{ marginTop: 0 }}>รายการนัดหมายทั้งหมด ({filteredAppointments.length})</h2>
          {loading ? <p>กำลังโหลดข้อมูล...</p> : filteredAppointments.length === 0 ? <p>ไม่พบรายการนัดหมาย</p> : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 1050 }}>
                <thead><tr>
                  {["รหัสนัดหมาย / ผู้ป่วย", "วันที่", "เวลา", "สถานะ", "เลขห้อง", "การดำเนินการ"].map((label) =>
                    <th key={label} style={{ textAlign: "left", padding: "12px 8px", borderBottom: "1px solid var(--border)" }}>{label}</th>
                  )}
                </tr></thead>
                <tbody>
                  {filteredAppointments.map((item) => (
                    <tr key={item.id}>
                      <td style={{ padding: "12px 8px", borderBottom: "1px solid var(--border)", maxWidth: 240, overflowWrap: "anywhere" }}>
                        <strong>{item.id}</strong><div style={{ fontSize: 12, color: "var(--muted)" }}>Patient: {item.patient_id}</div>
                      </td>
                      <td style={{ padding: "12px 8px", borderBottom: "1px solid var(--border)", whiteSpace: "nowrap" }}>{formatDate(item.appointment_date)}</td>
                      <td style={{ padding: "12px 8px", borderBottom: "1px solid var(--border)", whiteSpace: "nowrap" }}>{item.start_time.slice(0, 5)}–{item.end_time.slice(0, 5)}</td>
                      <td style={{ padding: "12px 8px", borderBottom: "1px solid var(--border)", whiteSpace: "nowrap" }}>{statusLabels[item.status] ?? item.status}</td>
                      <td style={{ padding: "12px 8px", borderBottom: "1px solid var(--border)" }}>
                        <input aria-label={`เลขห้องสำหรับ ${item.id}`} value={rooms[item.id] ?? ""} onChange={(e) => setRooms((current) => ({ ...current, [item.id]: e.target.value }))} placeholder="เลขห้อง" style={{ width: 90 }} />
                      </td>
                      <td style={{ padding: "12px 8px", borderBottom: "1px solid var(--border)" }}>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                          {item.status === "pending" && <button className="action-button primary" disabled={busyId === item.id} onClick={() => void handleConfirm(item)}>ยืนยันนัด</button>}
                          {item.status === "confirmed" && <button className="action-button primary" disabled={busyId === item.id} onClick={() => void handleStatus(item, "checked_in")}>เช็คอิน</button>}
                          {item.status === "checked_in" && <button className="action-button primary" disabled={busyId === item.id} onClick={() => void handleStatus(item, "in_progress")}>เรียกตรวจ</button>}
                          {!["cancelled", "completed", "no_show"].includes(item.status) && <button className="action-button secondary" disabled={busyId === item.id} onClick={() => void handleNotify(item)}>ส่งแจ้งเตือน</button>}
                          {!["cancelled", "completed", "no_show"].includes(item.status) && <button className="action-button danger" disabled={busyId === item.id} onClick={() => void handleCancel(item)}>ยกเลิกนัด</button>}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </section>
  );
}

export default StaffAppointmentsPage;
