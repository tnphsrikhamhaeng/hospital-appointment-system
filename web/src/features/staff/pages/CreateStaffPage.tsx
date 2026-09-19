import {
  useEffect,
  useState,
  type FormEvent,
} from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle } from "lucide-react";

import {
  createStaff,
  getStaff,
  updateStaff,
  deactivateStaff,
  reactivateStaff,
  type StaffCreateRequest,
  type StaffResponse,
  type StaffUpdateRequest,
} from "../api/staffApi";

import { logout } from "../../auth/api/authApi";
import ChangePasswordModal from "../../profile/components/ChangePasswordModal";

import "../../doctor/pages/DoctorPage.css";

const staffModalStyle = `
  .staff-modal-grid {
    display: grid;
    grid-template-columns: repeat(
      2,
      minmax(0, 1fr)
    );
    gap: 16px;
    width: 100%;
    margin-top: 18px;
  }

  .staff-modal-field {
    width: 100%;
  }

  .staff-modal-field.full-width {
    grid-column: 1 / -1;
  }

  .staff-modal-field label {
    display: block;
    width: 100%;
    margin: 0 0 7px;
    text-align: left;
    color: var(--text);
    font-size: 13px;
    font-weight: 400;
    line-height: 1.4;
  }

  .staff-modal-field input {
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
  }

  .staff-modal-field input:focus {
    border-color: var(--primary);
  }

  .staff-modal-actions {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 20px;
  }

  .staff-modal-actions .action-button {
    width: 100%;
    min-height: 42px;
    box-sizing: border-box;
    justify-content: center;
  }

  .staff-modal-error {
    width: 100%;
    margin: 14px 0 0;
    color: var(--danger);
    font-size: 13px;
    line-height: 1.5;
    text-align: left;
  }

  .staff-modal-success {
    width: 100%;
    margin: 14px 0 0;
    color: var(--success);
    font-size: 13px;
    line-height: 1.5;
    text-align: left;
  }

  @media (max-width: 640px) {
    .staff-modal-grid {
      grid-template-columns: 1fr;
    }

    .staff-modal-field.full-width {
      grid-column: auto;
    }
  }
`;

function CreateStaffPage() {
  const navigate = useNavigate();

  /* =========================
     Staff List
  ========================== */
  const [staffList, setStaffList] = useState<
    StaffResponse[]
  >([]);

  const [search, setSearch] = useState("");

  const [showInactive, setShowInactive] =
    useState(false);

  const [isLoading, setIsLoading] =
    useState(true);

  const [errorMessage, setErrorMessage] =
    useState("");

  /* =========================
     Add Staff
  ========================== */
  const [isAddOpen, setIsAddOpen] =
    useState(false);

  const [form, setForm] =
    useState<StaffCreateRequest>({
      username: "",
      password: "",
      first_name: "",
      last_name: "",
      phone_number: "",
      email: "",
    });

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [addError, setAddError] =
    useState("");

  const [addSuccess, setAddSuccess] =
    useState("");

  /* =========================
     Edit Staff
  ========================== */
  const [selectedStaff, setSelectedStaff] =
    useState<StaffResponse | null>(null);

  const [editForm, setEditForm] =
    useState<StaffUpdateRequest>({
      username: "",
      first_name: "",
      last_name: "",
      phone_number: "",
      email: "",
    });

  const [isEditing, setIsEditing] =
    useState(false);

  const [editError, setEditError] =
    useState("");

  /* =========================
     Deactivate Staff
  ========================== */
  const [
    selectedDeactivateStaff,
    setSelectedDeactivateStaff,
  ] = useState<StaffResponse | null>(null);

  const [
    deactivatePassword,
    setDeactivatePassword,
  ] = useState("");

  const [
    isDeactivating,
    setIsDeactivating,
  ] = useState(false);

  const [
    deactivateError,
    setDeactivateError,
  ] = useState("");

  /* =========================
     Reactivate Staff
  ========================== */
  const [
    selectedReactivateStaff,
    setSelectedReactivateStaff,
  ] = useState<StaffResponse | null>(null);

  const [
    reactivatePassword,
    setReactivatePassword,
  ] = useState("");

  const [
    isReactivating,
    setIsReactivating,
  ] = useState(false);

  const [
    reactivateError,
    setReactivateError,
  ] = useState("");

  /* =========================
     Logout
  ========================== */
  const [isLogoutOpen, setIsLogoutOpen] =
    useState(false);

  /* =========================
     Change Password
  ========================== */
  const [
    isChangePasswordOpen,
    setIsChangePasswordOpen,
  ] = useState(false);

  /* =========================
     Load Staff
  ========================== */
  const loadStaff = async (
    searchValue = "",
    inactive = false,
  ) => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const data = await getStaff(
        searchValue.trim() || undefined,
        inactive ? "inactive" : "active",
      );

      setStaffList(data);
    } catch {
      setErrorMessage(
        "ไม่สามารถโหลดรายการเจ้าหน้าที่ได้",
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadStaff();
  }, []);

  /* =========================
     Search
  ========================== */
  const handleSearchChange = (
    value: string,
  ) => {
    setSearch(value);

    void loadStaff(
      value,
      showInactive,
    );
  };

  const handleSearch = () => {
    void loadStaff(
      search,
      showInactive,
    );
  };

  const handleClearSearch = () => {
    setSearch("");

    void loadStaff(
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

    void loadStaff(
      "",
      nextShowInactive,
    );
  };

  /* =========================
     Add Staff
  ========================== */
  const handleOpenAdd = () => {
    setForm({
      username: "",
      password: "",
      first_name: "",
      last_name: "",
      phone_number: "",
      email: "",
    });

    setAddError("");
    setAddSuccess("");
    setIsAddOpen(true);
  };

  const handleCloseAdd = () => {
    if (isSubmitting) {
      return;
    }

    setIsAddOpen(false);
    setAddError("");
    setAddSuccess("");
  };

  const handleChange = (
    field: keyof StaffCreateRequest,
    value: string,
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));

    setAddError("");
    setAddSuccess("");
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setAddError("");
    setAddSuccess("");

    if (
      !form.username.trim() ||
      !form.password ||
      !form.first_name.trim() ||
      !form.last_name.trim() ||
      !form.phone_number.trim() ||
      !form.email.trim()
    ) {
      setAddError(
        "กรุณากรอกข้อมูลให้ครบทุกช่อง",
      );
      return;
    }

    if (form.password.length < 8) {
      setAddError(
        "รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร",
      );
      return;
    }

    setIsSubmitting(true);

    try {
      await createStaff({
        username:
          form.username.trim(),
        password: form.password,
        first_name:
          form.first_name.trim(),
        last_name:
          form.last_name.trim(),
        phone_number:
          form.phone_number.trim(),
        email:
          form.email.trim(),
      });

      setAddSuccess(
        "เพิ่มเจ้าหน้าที่สำเร็จ",
      );

      setForm({
        username: "",
        password: "",
        first_name: "",
        last_name: "",
        phone_number: "",
        email: "",
      });

      await loadStaff(
        search,
        showInactive,
      );
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

        setAddError(
          response?.data?.detail ??
            "ไม่สามารถเพิ่มเจ้าหน้าที่ได้",
        );
      } else {
        setAddError(
          "ไม่สามารถเพิ่มเจ้าหน้าที่ได้",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  /* =========================
     Edit Staff
  ========================== */
  const handleOpenEdit = (
    staff: StaffResponse,
  ) => {
    setSelectedStaff(staff);

    setEditForm({
      username: staff.username,
      first_name: staff.first_name,
      last_name: staff.last_name,
      phone_number:
        staff.phone_number,
      email: staff.email,
    });

    setEditError("");
  };

  const handleCloseEdit = () => {
    if (isEditing) {
      return;
    }

    setSelectedStaff(null);
    setEditError("");
  };

  const handleEditChange = (
    field: keyof StaffUpdateRequest,
    value: string,
  ) => {
    setEditForm((current) => ({
      ...current,
      [field]: value,
    }));

    setEditError("");
  };

  const handleUpdateStaff = async () => {
    if (!selectedStaff) {
      return;
    }

    if (
      !editForm.username.trim() ||
      !editForm.first_name.trim() ||
      !editForm.last_name.trim() ||
      !editForm.phone_number.trim() ||
      !editForm.email.trim()
    ) {
      setEditError(
        "กรุณากรอกข้อมูลให้ครบทุกช่อง",
      );
      return;
    }

    try {
      setIsEditing(true);
      setEditError("");

      await updateStaff(
        selectedStaff.id,
        {
          username:
            editForm.username.trim(),
          first_name:
            editForm.first_name.trim(),
          last_name:
            editForm.last_name.trim(),
          phone_number:
            editForm.phone_number.trim(),
          email:
            editForm.email.trim(),
        },
      );

      setSelectedStaff(null);
      setEditError("");

      await loadStaff(
        search,
        showInactive,
      );
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

        setEditError(
          response?.data?.detail ??
            "ไม่สามารถแก้ไขข้อมูลเจ้าหน้าที่ได้",
        );
      } else {
        setEditError(
          "ไม่สามารถแก้ไขข้อมูลเจ้าหน้าที่ได้",
        );
      }
    } finally {
      setIsEditing(false);
    }
  };

  /* =========================
     Deactivate Staff
  ========================== */
  const handleOpenDeactivate = (
    staff: StaffResponse,
  ) => {
    setSelectedDeactivateStaff(staff);
    setDeactivatePassword("");
    setDeactivateError("");
  };

  const handleCloseDeactivate = () => {
    if (isDeactivating) {
      return;
    }

    setSelectedDeactivateStaff(null);
    setDeactivatePassword("");
    setDeactivateError("");
  };

  const handleDeactivateStaff = async () => {
    if (!selectedDeactivateStaff) {
      return;
    }

    if (!deactivatePassword.trim()) {
      setDeactivateError(
        "กรุณากรอกรหัสผ่านเจ้าหน้าที่",
      );
      return;
    }

    try {
      setIsDeactivating(true);
      setDeactivateError("");
      setErrorMessage("");

      await deactivateStaff(
        selectedDeactivateStaff.id,
        deactivatePassword,
      );

      setSelectedDeactivateStaff(null);
      setDeactivatePassword("");

      setStaffList((current) =>
        current.filter(
          (item) =>
            item.id !==
            selectedDeactivateStaff.id,
        ),
      );
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

        setDeactivateError(
          response?.data?.detail ??
            "รหัสผ่านไม่ถูกต้อง หรือไม่สามารถปิดใช้งานเจ้าหน้าที่ได้",
        );
      } else {
        setDeactivateError(
          "ไม่สามารถปิดใช้งานเจ้าหน้าที่ได้",
        );
      }
    } finally {
      setIsDeactivating(false);
    }
  };

  /* =========================
     Reactivate Staff
  ========================== */
  const handleOpenReactivate = (
    staff: StaffResponse,
  ) => {
    setSelectedReactivateStaff(staff);
    setReactivatePassword("");
    setReactivateError("");
  };

  const handleCloseReactivate = () => {
    if (isReactivating) {
      return;
    }

    setSelectedReactivateStaff(null);
    setReactivatePassword("");
    setReactivateError("");
  };

  const handleReactivateStaff = async () => {
    if (!selectedReactivateStaff) {
      return;
    }

    if (!reactivatePassword.trim()) {
      setReactivateError(
        "กรุณากรอกรหัสผ่านเจ้าหน้าที่",
      );
      return;
    }

    try {
      setIsReactivating(true);
      setReactivateError("");
      setErrorMessage("");

      await reactivateStaff(
        selectedReactivateStaff.id,
        reactivatePassword,
      );

      setSelectedReactivateStaff(null);
      setReactivatePassword("");

      setStaffList((current) =>
        current.filter(
          (item) =>
            item.id !==
            selectedReactivateStaff.id,
        ),
      );
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

        setReactivateError(
          response?.data?.detail ??
            "รหัสผ่านไม่ถูกต้อง หรือไม่สามารถเปิดใช้งานเจ้าหน้าที่ได้",
        );
      } else {
        setReactivateError(
          "ไม่สามารถเปิดใช้งานเจ้าหน้าที่ได้",
        );
      }
    } finally {
      setIsReactivating(false);
    }
  };

  /* =========================
     Logout
  ========================== */
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

  /* =========================
     Render
  ========================== */
  return (
    <main className="doctor-page">
      <style>
        {staffModalStyle}
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
            <strong>
              CareFlow
            </strong>

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

            <span>
              เช็คอินผู้ป่วย
            </span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() =>
              navigate(
                "/staff/doctors",
              )
            }
          >
            <span className="nav-icon">
              ⚕
            </span>

            <span>
              จัดการแพทย์
            </span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item active"
            onClick={() =>
              navigate(
                "/staff/create",
              )
            }
          >
            <span className="nav-icon">
              ♙
            </span>

            <span>
              จัดการเจ้าหน้าที่
            </span>
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

            <span>
              จัดการแผนก
            </span>
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
            onClick={
              handleOpenLogout
            }
          >
            <span className="nav-icon">
              ↪
            </span>

            <span>
              ออกจากระบบ
            </span>
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

            <h1>
              จัดการเจ้าหน้าที่
            </h1>

            <p>
              จัดการข้อมูลเจ้าหน้าที่
              และตรวจสอบรายชื่อเจ้าหน้าที่
              ในระบบ
            </p>
          </div>

          <div className="doctor-header-right">
            <button
              type="button"
              className="action-button primary"
              onClick={
                handleOpenAdd
              }
            >
              + เพิ่มเจ้าหน้าที่ใหม่
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
                  การจัดการเจ้าหน้าที่
                </span>

                <h2>
                  ค้นหาเจ้าหน้าที่
                </h2>

                <p>
                  ค้นหาจากชื่อเจ้าหน้าที่
                  หรือชื่อผู้ใช้
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
                  alignItems:
                    "center",
                  flexWrap:
                    "wrap",
                }}
              >
                <input
                  type="text"
                  value={search}
                  placeholder="ค้นหาชื่อเจ้าหน้าที่หรือชื่อผู้ใช้"
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
                    flex:
                      "1 1 360px",
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
                    outline:
                      "none",
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
                    ? "แสดงเจ้าหน้าที่ที่ใช้งาน"
                    : "แสดงเจ้าหน้าที่ที่ปิดใช้งาน"}
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
            Staff List
        ========================== */}
        <section className="current-patient-section">
          <div className="current-patient-card">
            <div className="current-patient-header">
              <div>
                <span className="section-eyebrow">
                  รายชื่อเจ้าหน้าที่
                </span>

                <h2>
                  {search
                    ? "ผลการค้นหาเจ้าหน้าที่"
                    : showInactive
                      ? "เจ้าหน้าที่ที่ปิดใช้งาน"
                      : "เจ้าหน้าที่ที่ใช้งาน"}
                </h2>

                <p>
                  {staffList.length}{" "}
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
                }}
              >
                กำลังโหลดรายการเจ้าหน้าที่...
              </div>
            ) : staffList.length ===
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
                }}
              >
                {search
                  ? "ไม่พบเจ้าหน้าที่ที่ตรงกับการค้นหา"
                  : showInactive
                    ? "ไม่มีเจ้าหน้าที่ที่ปิดใช้งาน"
                    : "ยังไม่มีข้อมูลเจ้าหน้าที่"}
              </div>
            ) : (
              <div
                style={{
                  display: "flex",
                  flexDirection:
                    "column",
                }}
              >
                {staffList.map(
                  (staff) => (
                    <article
                      key={staff.id}
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
                          {
                            staff.first_name
                          }{" "}
                          {
                            staff.last_name
                          }
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
                          }}
                        >
                          <span>
                            ชื่อผู้ใช้:{" "}
                            {
                              staff.username
                            }
                          </span>

                          <span>
                            อีเมล:{" "}
                            {staff.email}
                          </span>

                          <span>
                            เบอร์โทรศัพท์:{" "}
                            {
                              staff.phone_number
                            }
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
                        {!showInactive ? (
                          <>
                            <button
                              type="button"
                              className="action-button secondary"
                              onClick={() =>
                                handleOpenEdit(
                                  staff,
                                )
                              }
                            >
                              แก้ไข
                            </button>

                            <button
                              type="button"
                              className="action-button danger"
                              onClick={() =>
                                handleOpenDeactivate(
                                  staff,
                                )
                              }
                            >
                              ปิดใช้งาน
                            </button>
                          </>
                        ) : (
                          <button
                            type="button"
                            className="action-button primary"
                            onClick={() =>
                              handleOpenReactivate(
                                staff,
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
          Add Staff Modal
      ========================== */}
      {isAddOpen && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={
            handleCloseAdd
          }
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-staff-title"
            onClick={(event) =>
              event.stopPropagation()
            }
            style={{
              maxWidth:
                "680px",
              width: "calc(100% - 32px)",
            }}
          >
            <div className="doctor-modal-icon">
              ♙
            </div>

            <h2 id="add-staff-title">
              เพิ่มเจ้าหน้าที่
            </h2>

            <p>
              กรุณากรอกข้อมูลเจ้าหน้าที่
              ให้ครบถ้วน
            </p>

            <form
              onSubmit={handleSubmit}
            >
              <div className="staff-modal-grid">
                <div className="staff-modal-field">
                  <label htmlFor="staff-username">
                    ชื่อผู้ใช้
                  </label>

                  <input
                    id="staff-username"
                    type="text"
                    value={
                      form.username
                    }
                    onChange={(event) =>
                      handleChange(
                        "username",
                        event.target.value,
                      )
                    }
                    disabled={
                      isSubmitting
                    }
                    autoComplete="username"
                  />
                </div>

                <div className="staff-modal-field">
                  <label htmlFor="staff-password">
                    รหัสผ่าน
                  </label>

                  <input
                    id="staff-password"
                    type="password"
                    value={
                      form.password
                    }
                    onChange={(event) =>
                      handleChange(
                        "password",
                        event.target.value,
                      )
                    }
                    disabled={
                      isSubmitting
                    }
                    autoComplete="new-password"
                  />
                </div>

                <div className="staff-modal-field">
                  <label htmlFor="staff-first-name">
                    ชื่อ
                  </label>

                  <input
                    id="staff-first-name"
                    type="text"
                    value={
                      form.first_name
                    }
                    onChange={(event) =>
                      handleChange(
                        "first_name",
                        event.target.value,
                      )
                    }
                    disabled={
                      isSubmitting
                    }
                    autoComplete="given-name"
                  />
                </div>

                <div className="staff-modal-field">
                  <label htmlFor="staff-last-name">
                    นามสกุล
                  </label>

                  <input
                    id="staff-last-name"
                    type="text"
                    value={
                      form.last_name
                    }
                    onChange={(event) =>
                      handleChange(
                        "last_name",
                        event.target.value,
                      )
                    }
                    disabled={
                      isSubmitting
                    }
                    autoComplete="family-name"
                  />
                </div>

                <div className="staff-modal-field">
                  <label htmlFor="staff-phone">
                    เบอร์โทรศัพท์
                  </label>

                  <input
                    id="staff-phone"
                    type="tel"
                    value={
                      form.phone_number
                    }
                    onChange={(event) =>
                      handleChange(
                        "phone_number",
                        event.target.value,
                      )
                    }
                    disabled={
                      isSubmitting
                    }
                    autoComplete="tel"
                  />
                </div>

                <div className="staff-modal-field">
                  <label htmlFor="staff-email">
                    อีเมล
                  </label>

                  <input
                    id="staff-email"
                    type="email"
                    value={
                      form.email
                    }
                    onChange={(event) =>
                      handleChange(
                        "email",
                        event.target.value,
                      )
                    }
                    disabled={
                      isSubmitting
                    }
                    autoComplete="email"
                  />
                </div>
              </div>

              {addError && (
                <p
                  className="staff-modal-error"
                  role="alert"
                >
                  {addError}
                </p>
              )}

              {addSuccess && (
                <p
                  className="staff-modal-success"
                  role="status"
                >
                  {addSuccess}
                </p>
              )}

              <div className="staff-modal-actions">
                <button
                  type="submit"
                  className="action-button primary"
                  disabled={
                    isSubmitting
                  }
                >
                  {isSubmitting
                    ? "กำลังเพิ่มเจ้าหน้าที่..."
                    : "เพิ่มเจ้าหน้าที่"}
                </button>

                <button
                  type="button"
                  className="action-button secondary"
                  onClick={
                    handleCloseAdd
                  }
                  disabled={
                    isSubmitting
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
          Edit Staff Modal
      ========================== */}
      {selectedStaff && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={
            handleCloseEdit
          }
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="edit-staff-title"
            onClick={(event) =>
              event.stopPropagation()
            }
            style={{
              maxWidth:
                "680px",
              width: "calc(100% - 32px)",
            }}
          >
            <div className="doctor-modal-icon">
              ♙
            </div>

            <h2 id="edit-staff-title">
              แก้ไขข้อมูลเจ้าหน้าที่
            </h2>

            <p>
              แก้ไขข้อมูลเจ้าหน้าที่
            </p>

            <div className="staff-modal-grid">
              <div className="staff-modal-field full-width">
                <label htmlFor="edit-staff-username">
                  ชื่อผู้ใช้
                </label>

                <input
                  id="edit-staff-username"
                  type="text"
                  value={editForm.username}
                  disabled={isEditing}
                  onChange={(event) =>
                    handleEditChange(
                      "username",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="staff-modal-field">
                <label htmlFor="edit-staff-first-name">
                  ชื่อ
                </label>

                <input
                  id="edit-staff-first-name"
                  type="text"
                  value={editForm.first_name}
                  disabled={isEditing}
                  onChange={(event) =>
                    handleEditChange(
                      "first_name",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="staff-modal-field">
                <label htmlFor="edit-staff-last-name">
                  นามสกุล
                </label>

                <input
                  id="edit-staff-last-name"
                  type="text"
                  value={editForm.last_name}
                  disabled={isEditing}
                  onChange={(event) =>
                    handleEditChange(
                      "last_name",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="staff-modal-field">
                <label htmlFor="edit-staff-phone">
                  เบอร์โทรศัพท์
                </label>

                <input
                  id="edit-staff-phone"
                  type="tel"
                  value={editForm.phone_number}
                  disabled={isEditing}
                  onChange={(event) =>
                    handleEditChange(
                      "phone_number",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="staff-modal-field">
                <label htmlFor="edit-staff-email">
                  อีเมล
                </label>

                <input
                  id="edit-staff-email"
                  type="email"
                  value={editForm.email}
                  disabled={isEditing}
                  onChange={(event) =>
                    handleEditChange(
                      "email",
                      event.target.value,
                    )
                  }
                />
              </div>
            </div>

            {editError && (
              <p
                className="staff-modal-error"
                role="alert"
              >
                {editError}
              </p>
            )}

            <div className="staff-modal-actions">
              <button
                type="button"
                className="action-button primary"
                onClick={() =>
                  void handleUpdateStaff()
                }
                disabled={
                  isEditing
                }
              >
                {isEditing
                  ? "กำลังบันทึก..."
                  : "บันทึก"}
              </button>

              <button
                type="button"
                className="action-button secondary"
                onClick={
                  handleCloseEdit
                }
                disabled={
                  isEditing
                }
              >
                ยกเลิก
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================
          Deactivate Staff Modal
      ========================== */}
      {selectedDeactivateStaff && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={
            handleCloseDeactivate
          }
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="deactivate-staff-title"
            onClick={(event) =>
              event.stopPropagation()
            }
            style={{
              width: "calc(100% - 32px)",
              maxWidth: "520px",
            }}
          >
            <div className="doctor-modal-icon warning">
              <AlertTriangle size={20} />
            </div>

            <h2 id="deactivate-staff-title">
              ปิดใช้งานเจ้าหน้าที่
            </h2>

            <p>
              ต้องการปิดใช้งานเจ้าหน้าที่{" "}
              <strong>
                {
                  selectedDeactivateStaff.first_name
                }{" "}
                {
                  selectedDeactivateStaff.last_name
                }
              </strong>{" "}
              ใช่หรือไม่?
            </p>

            <form
              onSubmit={(event) => {
                event.preventDefault();
                void handleDeactivateStaff();
              }}
            >
              <div
                className="staff-modal-field"
                style={{
                  marginTop: "18px",
                }}
              >
                <label htmlFor="deactivate-staff-password">
                  ยืนยันรหัสผ่านเจ้าหน้าที่
                </label>

                <input
                  id="deactivate-staff-password"
                  type="password"
                  value={
                    deactivatePassword
                  }
                  placeholder="กรอกรหัสผ่าน"
                  disabled={
                    isDeactivating
                  }
                  autoComplete="current-password"
                  onChange={(event) => {
                    setDeactivatePassword(
                      event.target.value,
                    );
                    setDeactivateError("");
                  }}
                />
              </div>

              {deactivateError && (
                <p
                  className="staff-modal-error"
                  role="alert"
                >
                  {deactivateError}
                </p>
              )}

              <div className="staff-modal-actions">
                <button
                  type="submit"
                  className="action-button danger"
                  disabled={
                    isDeactivating
                  }
                >
                  {isDeactivating
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
                    isDeactivating
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
          Reactivate Staff Modal
      ========================== */}
      {selectedReactivateStaff && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={
            handleCloseReactivate
          }
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="reactivate-staff-title"
            onClick={(event) =>
              event.stopPropagation()
            }
            style={{
              width: "calc(100% - 32px)",
              maxWidth: "520px",
            }}
          >
            <div className="doctor-modal-icon">
              ♙
            </div>

            <h2 id="reactivate-staff-title">
              เปิดใช้งานเจ้าหน้าที่
            </h2>

            <p>
              ต้องการเปิดใช้งานเจ้าหน้าที่{" "}
              <strong>
                {
                  selectedReactivateStaff.first_name
                }{" "}
                {
                  selectedReactivateStaff.last_name
                }
              </strong>{" "}
              ใช่หรือไม่?
            </p>

            <form
              onSubmit={(event) => {
                event.preventDefault();
                void handleReactivateStaff();
              }}
            >
              <div
                className="staff-modal-field"
                style={{
                  marginTop: "18px",
                }}
              >
                <label htmlFor="reactivate-staff-password">
                  ยืนยันรหัสผ่านเจ้าหน้าที่
                </label>

                <input
                  id="reactivate-staff-password"
                  type="password"
                  value={
                    reactivatePassword
                  }
                  placeholder="กรอกรหัสผ่าน"
                  disabled={
                    isReactivating
                  }
                  autoComplete="current-password"
                  onChange={(event) => {
                    setReactivatePassword(
                      event.target.value,
                    );
                    setReactivateError("");
                  }}
                />
              </div>

              {reactivateError && (
                <p
                  className="staff-modal-error"
                  role="alert"
                >
                  {reactivateError}
                </p>
              )}

              <div className="staff-modal-actions">
                <button
                  type="submit"
                  className="action-button primary"
                  disabled={
                    isReactivating
                  }
                >
                  {isReactivating
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
                    isReactivating
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
          Logout Modal
      ========================== */}
      {isLogoutOpen && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={
            handleCloseLogout
          }
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="logout-modal-title"
            onClick={(event) =>
              event.stopPropagation()
            }
            style={{
              width: "calc(100% - 32px)",
              maxWidth: "420px",
            }}
          >
            <div className="doctor-modal-icon warning">
              <AlertTriangle
                size={20}
              />
            </div>

            <h2 id="logout-modal-title">
              ยืนยันการออกจากระบบ
            </h2>

            <p>
              คุณต้องการออกจากระบบใช่หรือไม่?
            </p>

            <div className="staff-modal-actions">
              <button
                type="button"
                className="action-button danger"
                onClick={
                  handleConfirmLogout
                }
              >
                ยืนยันการออกจากระบบ
              </button>

              <button
                type="button"
                className="action-button secondary"
                onClick={
                  handleCloseLogout
                }
              >
                ยกเลิก
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================
          Change Password
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
    </main>
  );
}

export default CreateStaffPage;