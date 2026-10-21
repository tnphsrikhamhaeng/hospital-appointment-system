import { useEffect, useMemo, useState } from "react";
import {
  cancelAppointment, getStaffAppointments, sendStaffAppointmentNotification,
  updateAppointmentStatus, type Appointment,
} from "../../appointment/api/appointmentApi";
import "../../doctor/pages/DoctorPage.css";

const statusLabels: Record<string, string> = {
  pending: "รอยืนยัน", confirmed: "รอเช็คอิน", checked_in: "เช็คอินแล้ว",
  in_progress: "กำลังตรวจ", completed: "เสร็จสิ้น", cancelled: "ยกเลิก",
  no_show: "ไม่มาตามนัด",
};
const terminal = ["cancelled", "completed", "no_show"];
const escapeHtml = (v: unknown) => String(v ?? "-").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#39;");

function StaffAppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [searchId, setSearchId] = useState("");
  const [filterDate, setFilterDate] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [rooms, setRooms] = useState<Record<string, string>>({});
  const [selected, setSelected] = useState<Appointment | null>(null);
  const [exportOpen, setExportOpen] = useState(false);
  const [exportFields, setExportFields] = useState(["patient_name","doctor_name","department_name","appointment_date","start_time","status","reason","cancelled_reason"]);

  const reload = async () => {
    setLoading(true); setError("");
    try { setAppointments(await getStaffAppointments()); }
    catch { setError("โหลดรายการนัดหมายไม่สำเร็จ กรุณาลองใหม่"); }
    finally { setLoading(false); }
  };
  useEffect(() => { void reload(); }, []);

  const filtered = useMemo(() => appointments
    .filter(a => !searchId.trim() || a.id.toLowerCase().includes(searchId.trim().toLowerCase()) || (a.patient_name ?? "").toLowerCase().includes(searchId.trim().toLowerCase()))
    .filter(a => !filterDate || a.appointment_date === filterDate)
    .filter(a => filterStatus === "all" || a.status === filterStatus)
    .sort((a,b) => a.appointment_date.localeCompare(b.appointment_date) || a.start_time.localeCompare(b.start_time)),
  [appointments, searchId, filterDate, filterStatus]);

  const updateLocal = (a: Appointment) => {
    setAppointments(xs => xs.map(x => x.id === a.id ? a : x));
    setSelected(a);
  };
  const runAction = async (a: Appointment, action: "confirm" | "checkin" | "call" | "cancel" | "notify") => {
    setError(""); setNotice("");
    if (action === "cancel") {
      const reason = window.prompt("กรอกเหตุผลการยกเลิกนัด");
      if (reason === null) return;
      if (!reason.trim()) { setError("กรุณากรอกเหตุผลการยกเลิก"); return; }
      setBusyId(a.id);
      try { updateLocal(await cancelAppointment(a.id,{cancelled_reason:reason.trim()})); setNotice("ยกเลิกนัดและส่งแจ้งเตือนแล้ว"); }
      catch { setError("ยกเลิกนัดไม่สำเร็จ"); } finally { setBusyId(null); }
      return;
    }
    if (action === "notify") {
      const message = window.prompt("ข้อความแจ้งเตือนผู้ป่วย");
      if (message === null) return;
      if (!message.trim()) { setError("กรุณากรอกข้อความ"); return; }
      setBusyId(a.id);
      try { await sendStaffAppointmentNotification(a.id,message.trim()); setNotice("ส่งแจ้งเตือนแล้ว"); }
      catch { setError("ส่งแจ้งเตือนไม่สำเร็จ"); } finally { setBusyId(null); }
      return;
    }
    const status = action === "confirm" ? "confirmed" : action === "checkin" ? "checked_in" : "in_progress";
    const room = (rooms[a.id] ?? "").trim();
    if (action !== "confirm" && !room) { setError("กรุณากรอกเลขห้องตรวจก่อนดำเนินการ"); return; }
    setBusyId(a.id);
    try {
      updateLocal(await updateAppointmentStatus(a.id,{status, ...(action === "confirm" ? {} : {room_number:room})}));
      setNotice(action === "confirm" ? "ยืนยันนัดหมายและส่งแจ้งเตือนแล้ว" : action === "checkin" ? "เช็คอินและแจ้งเลขห้องแล้ว" : "เรียกผู้ป่วยและแจ้งเตือนแล้ว");
    } catch { setError("ดำเนินการไม่สำเร็จ กรุณาลองใหม่"); }
    finally { setBusyId(null); }
  };

  const fields: Record<string,string> = {
    patient_name:"ชื่อผู้ป่วย", doctor_name:"แพทย์", department_name:"แผนก",
    appointment_date:"วันที่นัด", start_time:"เวลา", status:"สถานะ",
    confirmed_at:"ยืนยันเมื่อ", cancelled_at:"ยกเลิกเมื่อ",
  };
  const exportReport = () => {
    const rows = filtered.map(a => "<tr>" + exportFields.map(k => {
      const val = k === "status" ? statusLabels[a.status] : k === "start_time" ? a.start_time.slice(0,5) + "–" + a.end_time.slice(0,5) : (a as unknown as Record<string,unknown>)[k];
      return "<td>" + escapeHtml(val) + "</td>";
    }).join("") + "</tr>").join("");
    const w = window.open("", "_blank", "width=1100,height=800");
    if (!w) { setError("กรุณาอนุญาต Pop-up เพื่อบันทึกรายงาน"); return; }
    w.document.write(`<!doctype html><html lang="th"><meta charset="utf-8"><title>รายงานนัดหมาย</title><style>body{font-family:Arial,sans-serif;padding:24px}table{border-collapse:collapse;width:100%;font-size:11px}td,th{border:1px solid #bbb;padding:7px;text-align:left}th{background:#eef2f7}@page{size:landscape;margin:12mm}</style><h2>รายงานนัดหมาย CareFlow</h2><p>จำนวน ${filtered.length} รายการ</p><table><thead><tr>${exportFields.map(k=>"<th>"+escapeHtml(fields[k] ?? k)+"</th>").join("")}</tr></thead><tbody>${rows}</tbody></table><script>window.onload=()=>window.print()</script></html>`);
    w.document.close(); setExportOpen(false);
  };
  const dateLabel = (d:string) => d ? new Intl.DateTimeFormat("th-TH",{day:"numeric",month:"short",year:"numeric"}).format(new Date(d+"T00:00:00")) : "-";

  return <section className="doctor-content staff-appointments">
    <style>{`
      .staff-appointments input,.staff-appointments select{box-sizing:border-box;min-height:40px;padding:9px 12px;border:1px solid var(--border,#d7dfeb);border-radius:8px;background:var(--surface,#fff);color:var(--text,#172033);font:inherit;outline:none}
      .staff-appointments input:focus,.staff-appointments select:focus{border-color:#2672c9;box-shadow:0 0 0 3px #2672c91c}
      .staff-appointments .filter-label{display:grid;gap:6px;min-width:180px;font-size:13px;font-weight:600}
      .staff-appointments .appointment-row{cursor:pointer}.staff-appointments .appointment-row:hover{background:#f4f8fd}
      .staff-appointments .status-pill{display:inline-block;border-radius:20px;padding:5px 10px;background:#eef3f9;font-size:12px;white-space:nowrap}
      .staff-appointments .modal-backdrop{position:fixed;inset:0;background:#0b183b88;display:flex;align-items:center;justify-content:center;padding:18px;z-index:9999}
      .staff-appointments .modal-panel{background:var(--surface,#fff);color:var(--text,#172033);width:min(680px,100%);max-height:90vh;overflow:auto;border-radius:16px;padding:24px;box-shadow:0 20px 60px #0003}
      .staff-appointments .detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:20px 0}
      .staff-appointments .detail-item{padding:12px;border:1px solid var(--border,#d7dfeb);border-radius:10px;overflow-wrap:anywhere}
      .staff-appointments .detail-item small{display:block;color:var(--muted,#64748b);margin-bottom:5px}
      .staff-appointments .staff-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
      @media(max-width:650px){.staff-appointments .detail-grid{grid-template-columns:1fr}}
    `}</style>
    <header className="doctor-header"><div><span className="page-eyebrow">CareFlow Hospital System</span><h1>จัดการนัดหมาย</h1><p>เลือกนัดหมายเพื่อดูรายละเอียดและดำเนินการ</p></div>
      <button className="action-button primary" onClick={()=>setExportOpen(true)}>ส่งออกรายงาน PDF</button></header>
    {error && <div className="doctor-alert" role="alert">{error}</div>}{notice && <div className="doctor-alert" role="status">{notice}</div>}
    <section className="current-patient-card" style={{marginBottom:18}}><div style={{display:"flex",gap:14,flexWrap:"wrap",padding:20,alignItems:"end"}}>
      <label className="filter-label">ค้นหารหัสนัดหรือชื่อผู้ป่วย<input value={searchId} onChange={e=>setSearchId(e.target.value)} placeholder="พิมพ์ชื่อหรือรหัสนัด"/></label>
      <label className="filter-label">วันที่นัด<input type="date" value={filterDate} onChange={e=>setFilterDate(e.target.value)}/></label>
      <label className="filter-label">กรองตามสถานะ<select value={filterStatus} onChange={e=>setFilterStatus(e.target.value)}><option value="all">ทุกสถานะ</option>{Object.entries(statusLabels).map(([v,l])=><option key={v} value={v}>{l}</option>)}</select></label>
      <button className="action-button secondary" onClick={()=>{setSearchId("");setFilterDate("");setFilterStatus("all");}}>ล้างตัวกรอง</button>
      <button className="action-button secondary" onClick={()=>void reload()}>โหลดข้อมูลใหม่</button>
    </div></section>
    <section className="current-patient-card"><div style={{padding:20}}><h2 style={{marginTop:0}}>รายการนัดหมาย ({filtered.length})</h2>
      {loading?<p>กำลังโหลดข้อมูล...</p>:!filtered.length?<p>ไม่พบรายการนัดหมาย</p>:<div style={{overflowX:"auto"}}><table style={{width:"100%",borderCollapse:"collapse",minWidth:780}}><thead><tr>{["ชื่อผู้ป่วย","วันที่","เวลา","สถานะ","รายละเอียด"].map(x=><th key={x} style={{textAlign:"left",padding:"12px 8px",borderBottom:"1px solid var(--border)"}}>{x}</th>)}</tr></thead><tbody>
        {filtered.map(a=><tr key={a.id} className="appointment-row" onClick={()=>setSelected(a)}><td style={{padding:"12px 8px",borderBottom:"1px solid var(--border)"}}><strong>{a.patient_name || "ไม่พบชื่อผู้ป่วย"}</strong><div style={{fontSize:12,color:"var(--muted)"}}>{a.doctor_name || "ไม่พบชื่อแพทย์"}</div></td><td style={{padding:"12px 8px",whiteSpace:"nowrap",borderBottom:"1px solid var(--border)"}}>{dateLabel(a.appointment_date)}</td><td style={{padding:"12px 8px",whiteSpace:"nowrap",borderBottom:"1px solid var(--border)"}}>{a.start_time.slice(0,5)}–{a.end_time.slice(0,5)}</td><td style={{padding:"12px 8px",borderBottom:"1px solid var(--border)"}}><span className="status-pill">{statusLabels[a.status]??a.status}</span></td><td style={{padding:"12px 8px",borderBottom:"1px solid var(--border)"}}><button className="action-button secondary" onClick={e=>{e.stopPropagation();setSelected(a)}}>ดูรายละเอียด</button></td></tr>)}
      </tbody></table></div>}
    </div></section>

    {selected && <div className="modal-backdrop" onClick={()=>setSelected(null)}><section className="modal-panel" role="dialog" aria-modal="true" aria-labelledby="appointment-modal-title" onClick={e=>e.stopPropagation()}>
      <div style={{display:"flex",justifyContent:"space-between",gap:12,alignItems:"start"}}><div><span className="page-eyebrow">รายละเอียดนัดหมาย</span><h2 id="appointment-modal-title" style={{margin:"6px 0"}}>{selected.patient_name || "ไม่พบชื่อผู้ป่วย"}</h2><span className="status-pill">{statusLabels[selected.status]??selected.status}</span></div><button className="action-button secondary" onClick={()=>setSelected(null)}>ปิด</button></div>
      <div className="detail-grid">{[["แพทย์",selected.doctor_name],["แผนก",selected.department_name],["วันที่",dateLabel(selected.appointment_date)],["เวลา",selected.start_time.slice(0,5)+"–"+selected.end_time.slice(0,5)],["รหัสนัดหมาย",selected.id]].map(([k,v])=><div className="detail-item" key={k}><small>{k}</small><strong>{v || "-"}</strong></div>)}</div>
      {!terminal.includes(selected.status) && <label className="filter-label" style={{maxWidth:260}}>เลขห้องตรวจ (ใช้ตอนเช็คอิน/เรียกตรวจ)<input value={rooms[selected.id]??""} onChange={e=>setRooms(s=>({...s,[selected.id]:e.target.value}))} placeholder="เช่น 101"/></label>}
      <div className="staff-actions">
        {selected.status==="pending" && <button className="action-button primary" disabled={busyId===selected.id} onClick={()=>void runAction(selected,"confirm")}>ยืนยันนัดหมาย</button>}
        {selected.status==="confirmed" && <button className="action-button primary" disabled={busyId===selected.id} onClick={()=>void runAction(selected,"checkin")}>เช็คอิน</button>}
        {selected.status==="checked_in" && <button className="action-button primary" disabled={busyId===selected.id} onClick={()=>void runAction(selected,"call")}>เรียกตรวจ</button>}
        {!terminal.includes(selected.status) && <button className="action-button secondary" disabled={busyId===selected.id} onClick={()=>void runAction(selected,"notify")}>ส่งแจ้งเตือน</button>}
        {["pending","confirmed","checked_in"].includes(selected.status) && <button className="action-button danger" disabled={busyId===selected.id} onClick={()=>void runAction(selected,"cancel")}>ยกเลิกนัด</button>}
      </div>
    </section></div>}

    {exportOpen && <div className="modal-backdrop" onClick={()=>setExportOpen(false)}><section className="modal-panel" role="dialog" aria-modal="true" onClick={e=>e.stopPropagation()}>
      <h2>เลือกข้อมูลสำหรับรายงาน PDF</h2><p>จะส่งออกเฉพาะรายการที่ผ่านตัวกรองปัจจุบัน ({filtered.length} รายการ) และแสดงข้อมูลเป็นชื่อ ไม่ใช่ ID</p>
      <div style={{display:"grid",gridTemplateColumns:"repeat(2,minmax(0,1fr))",gap:12,margin:"18px 0"}}>{Object.entries(fields).map(([k,label])=><label key={k} style={{display:"flex",gap:8,alignItems:"center"}}><input type="checkbox" checked={exportFields.includes(k)} onChange={e=>setExportFields(old=>e.target.checked?[...old,k]:old.filter(x=>x!==k))}/>{label}</label>)}</div>
      <div className="staff-actions"><button className="action-button primary" disabled={!exportFields.length || !filtered.length} onClick={exportReport}>เปิดหน้าบันทึก PDF</button><button className="action-button secondary" onClick={()=>setExportOpen(false)}>ยกเลิก</button></div>
      <p style={{fontSize:12,color:"var(--muted)"}}>ในหน้าพิมพ์ เลือก “Save as PDF / บันทึกเป็น PDF” เพื่อเซฟลงเครื่อง</p>
    </section></div>}
  </section>;
}
export default StaffAppointmentsPage;
