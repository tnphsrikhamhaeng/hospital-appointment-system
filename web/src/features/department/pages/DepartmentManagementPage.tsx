import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  createDepartment,
  deleteDepartment,
  getDepartments,
  reactivateDepartment,
  updateDepartment,
  uploadDepartmentImage,
  type DepartmentResponse,
} from "../api/departmentApi";

import {
  createSpecialization,
  deleteSpecialization,
  getSpecializations,
  reactivateSpecialization,
  updateSpecialization,
  type SpecializationResponse,
} from "../api/specializationApi";

import { logout } from "../../auth/api/authApi";
import ChangePasswordModal from "../../profile/components/ChangePasswordModal";

import "../../doctor/pages/DoctorPage.css";

const departmentModalStyle = `
  .doctor-modal label {
    display: block;
    width: 100%;
    text-align: left;
    margin-bottom: 6px;
  }

  .doctor-modal form > div {
    width: 100%;
  }

  .doctor-modal form input,
  .doctor-modal form textarea,
  .doctor-modal form select {
    width: 100%;
    box-sizing: border-box;
  }

  .doctor-modal-actions {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .doctor-modal-actions .action-button {
    width: 100%;
    box-sizing: border-box;
  }
`;

type ModalType =
  | "create-department"
  | "edit-department"
  | "deactivate-department"
  | "create-specialization"
  | "edit-specialization"
  | "reactivate-department"
  | "reactivate-specialization"
  | "logout"
  | null;

const MAX_IMAGE_SIZE = 5 * 1024 * 1024;

const DepartmentManagementPage = () => {
  const navigate = useNavigate();

  const [departments, setDepartments] = useState<
    DepartmentResponse[]
  >([]);

  const [specializations, setSpecializations] = useState<
    SpecializationResponse[]
  >([]);

  const [search, setSearch] = useState("");
  const [showInactive, setShowInactive] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [modal, setModal] = useState<ModalType>(null);

  const [selectedDepartment, setSelectedDepartment] =
    useState<DepartmentResponse | null>(null);

  const [selectedSpecialization, setSelectedSpecialization] =
    useState<SpecializationResponse | null>(null);

  const [departmentName, setDepartmentName] = useState("");
  const [departmentDescription, setDepartmentDescription] =
    useState("");
  const [departmentImageUrl, setDepartmentImageUrl] =
    useState("");
  const [departmentImageFile, setDepartmentImageFile] =
    useState<File | null>(null);
  const [departmentImagePreview, setDepartmentImagePreview] =
    useState("");
  const [slotDuration, setSlotDuration] = useState("30");

  const [specializationName, setSpecializationName] =
    useState("");
  const [specializationDescription, setSpecializationDescription] =
    useState("");
  const [specializationDepartmentId, setSpecializationDepartmentId] =
    useState("");

  const [password, setPassword] = useState("");
  const [specializationToAddId, setSpecializationToAddId] =
    useState("");
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState("");

  const [isChangePasswordOpen, setIsChangePasswordOpen] =
    useState(false);

  // =========================================================
  // Load data
  // =========================================================

  const loadData = async (
    searchValue = "",
    inactive = false,
  ) => {
    try {
      setLoading(true);
      setError("");

      const status = inactive ? "inactive" : "active";

      const [departmentData, specializationData] =
        await Promise.all([
          getDepartments({
            ...(searchValue.trim()
              ? { search: searchValue.trim() }
              : {}),
            status,
          }),
          getSpecializations({
            ...(searchValue.trim()
              ? { search: searchValue.trim() }
              : {}),
            status,
          }),
        ]);

      setDepartments(departmentData);
      setSpecializations(specializationData);
    } catch {
      setError(
        "ไม่สามารถโหลดข้อมูลแผนกและความเชี่ยวชาญได้",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData("", false);
  }, []);

  // =========================================================
  // Search
  // =========================================================

  const filteredDepartments = useMemo(() => {
    const keyword = search.trim().toLowerCase();

    if (!keyword) {
      return departments;
    }

    return departments.filter((department) => {
      const departmentMatch =
        department.name.toLowerCase().includes(keyword) ||
        (department.description ?? "")
          .toLowerCase()
          .includes(keyword);

      const specializationMatch = specializations.some(
        (specialization) =>
          specialization.department_id === department.id &&
          (specialization.name
            .toLowerCase()
            .includes(keyword) ||
            (specialization.description ?? "")
              .toLowerCase()
              .includes(keyword)),
      );

      return departmentMatch || specializationMatch;
    });
  }, [departments, specializations, search]);

  const getDepartmentSpecializations = (
    departmentId: string,
  ) => {
    return specializations.filter(
      (specialization) =>
        specialization.department_id === departmentId,
    );
  };

  // =========================================================
  // Image helpers
  // =========================================================

  const handleDepartmentImageChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setActionError("");

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setActionError(
        "รองรับเฉพาะไฟล์ JPG, PNG และ WEBP",
      );

      event.target.value = "";
      return;
    }

    if (file.size > MAX_IMAGE_SIZE) {
      setActionError(
        "ขนาดรูปภาพต้องไม่เกิน 5 MB",
      );

      event.target.value = "";
      return;
    }

    setDepartmentImageFile(file);

    const previewUrl = URL.createObjectURL(file);
    setDepartmentImagePreview(previewUrl);
  };

  // =========================================================
  // Modal helpers
  // =========================================================

  const resetForm = () => {
    if (departmentImagePreview) {
      URL.revokeObjectURL(departmentImagePreview);
    }

    setDepartmentName("");
    setDepartmentDescription("");
    setDepartmentImageUrl("");
    setDepartmentImageFile(null);
    setDepartmentImagePreview("");
    setSlotDuration("30");

    setSpecializationName("");
    setSpecializationDescription("");
    setSpecializationDepartmentId("");

    setPassword("");
    setSpecializationToAddId("");
    setActionError("");

    setSelectedDepartment(null);
    setSelectedSpecialization(null);
  };

  const closeModal = () => {
    if (saving) {
      return;
    }

    setModal(null);
    resetForm();
  };

  const finishModal = () => {
    setModal(null);
    resetForm();
  };

  // =========================================================
  // Department
  // =========================================================

  const handleOpenCreateDepartment = () => {
    resetForm();
    setModal("create-department");
  };

  const handleOpenEditDepartment = (
    department: DepartmentResponse,
  ) => {
    if (department.status === "inactive") {
      return;
    }

    setSelectedDepartment(department);

    setDepartmentName(department.name);
    setDepartmentDescription(
      department.description ?? "",
    );
    setDepartmentImageUrl(
      department.image_url ?? "",
    );
    setDepartmentImageFile(null);
    setDepartmentImagePreview("");
    setSlotDuration(
      String(department.slot_duration_minutes),
    );

    setActionError("");
    setModal("edit-department");
  };

  const handleCreateDepartment = async () => {
    if (!departmentName.trim()) {
      setActionError("กรุณากรอกชื่อแผนก");
      return;
    }

    const duration = Number(slotDuration);

    if (!Number.isInteger(duration) || duration <= 0) {
      setActionError(
        "ระยะเวลานัดหมายต้องเป็นจำนวนเต็มมากกว่า 0",
      );
      return;
    }

    try {
      setSaving(true);
      setActionError("");

      let imageUrl = departmentImageUrl.trim() || null;

      if (departmentImageFile) {
        const uploadResponse =
          await uploadDepartmentImage(
            departmentImageFile,
          );

        imageUrl = uploadResponse.image_url;
      }

      await createDepartment({
        name: departmentName.trim(),
        description:
          departmentDescription.trim() || null,
        image_url: imageUrl,
        slot_duration_minutes: duration,
      });

      await loadData(search, showInactive);

      setSaving(false);
      finishModal();
    } catch {
      setActionError(
        "ไม่สามารถเพิ่มแผนกหรืออัปโหลดรูปภาพได้",
      );
      setSaving(false);
    }
  };

  const handleUpdateDepartment = async () => {
    if (!selectedDepartment) {
      return;
    }

    if (!departmentName.trim()) {
      setActionError("กรุณากรอกชื่อแผนก");
      return;
    }

    const duration = Number(slotDuration);

    if (!Number.isInteger(duration) || duration <= 0) {
      setActionError(
        "ระยะเวลานัดหมายต้องเป็นจำนวนเต็มมากกว่า 0",
      );
      return;
    }

    try {
      setSaving(true);
      setActionError("");

      let imageUrl = departmentImageUrl.trim() || null;

      if (departmentImageFile) {
        const uploadResponse =
          await uploadDepartmentImage(
            departmentImageFile,
          );

        imageUrl = uploadResponse.image_url;
      }

      await updateDepartment(selectedDepartment.id, {
        name: departmentName.trim(),
        description:
          departmentDescription.trim() || null,
        image_url: imageUrl,
        slot_duration_minutes: duration,
      });

      await loadData(search, showInactive);

      setSaving(false);
      finishModal();
    } catch {
      setActionError(
        "ไม่สามารถแก้ไขแผนกหรืออัปโหลดรูปภาพได้",
      );
      setSaving(false);
    }
  };

  const handleDeleteDepartment = (
    department: DepartmentResponse,
  ) => {
    if (department.status === "inactive") {
      return;
    }

    setSelectedDepartment(department);
    setPassword("");
    setActionError("");
    setModal("deactivate-department");
  };

  const handleDeactivateDepartment = async () => {
    if (!selectedDepartment) {
      return;
    }

    if (!password.trim()) {
      setActionError("กรุณากรอกรหัสผ่าน");
      return;
    }

    try {
      setSaving(true);
      setActionError("");

      await deleteDepartment(
        selectedDepartment.id,
        password,
      );

      await loadData(search, showInactive);

      setSaving(false);
      finishModal();
    } catch {
      setActionError(
        "รหัสผ่านไม่ถูกต้อง หรือไม่สามารถปิดใช้งานแผนกได้",
      );
      setSaving(false);
    }
  };

  const handleOpenReactivateDepartment = (
    department: DepartmentResponse,
  ) => {
    if (department.status !== "inactive") {
      return;
    }

    setSelectedDepartment(department);
    setPassword("");
    setActionError("");

    setModal("reactivate-department");
  };

  const handleReactivateDepartment = async () => {
    if (!selectedDepartment) {
      return;
    }

    if (!password.trim()) {
      setActionError("กรุณากรอกรหัสผ่าน");
      return;
    }

    try {
      setSaving(true);
      setActionError("");

      await reactivateDepartment(
        selectedDepartment.id,
        password,
      );

      await loadData(search, showInactive);

      setSaving(false);
      finishModal();
    } catch {
      setActionError(
        "รหัสผ่านไม่ถูกต้อง หรือไม่สามารถเปิดใช้งานแผนกได้",
      );
      setSaving(false);
    }
  };

  // =========================================================
  // Specialization
  // =========================================================

  const handleOpenCreateSpecialization = () => {
    resetForm();
    setModal("create-specialization");
  };

  const handleOpenEditSpecialization = (
    specialization: SpecializationResponse,
  ) => {
    if (specialization.status === "inactive") {
      return;
    }

    setSelectedSpecialization(specialization);

    setSpecializationName(specialization.name);
    setSpecializationDescription(
      specialization.description ?? "",
    );
    setSpecializationDepartmentId(
      specialization.department_id,
    );

    setActionError("");
    setModal("edit-specialization");
  };

  const handleCreateSpecialization = async () => {
    if (!specializationDepartmentId) {
      setActionError("กรุณาเลือกแผนก");
      return;
    }

    if (!specializationName.trim()) {
      setActionError(
        "กรุณากรอกชื่อความเชี่ยวชาญ",
      );
      return;
    }

    try {
      setSaving(true);
      setActionError("");

      await createSpecialization({
        name: specializationName.trim(),
        description:
          specializationDescription.trim() || null,
        department_id: specializationDepartmentId,
      });

      await loadData(search, showInactive);

      setSaving(false);
      finishModal();
    } catch {
      setActionError(
        "ไม่สามารถเพิ่มความเชี่ยวชาญได้",
      );
      setSaving(false);
    }
  };

  const handleUpdateSpecialization = async () => {
    if (!selectedSpecialization) {
      return;
    }

    if (!specializationDepartmentId) {
      setActionError("กรุณาเลือกแผนก");
      return;
    }

    if (!specializationName.trim()) {
      setActionError(
        "กรุณากรอกชื่อความเชี่ยวชาญ",
      );
      return;
    }

    try {
      setSaving(true);
      setActionError("");

      await updateSpecialization(
        selectedSpecialization.id,
        {
          name: specializationName.trim(),
          description:
            specializationDescription.trim() || null,
          department_id:
            specializationDepartmentId,
        },
      );

      await loadData(search, showInactive);

      setSaving(false);
      finishModal();
    } catch {
      setActionError(
        "ไม่สามารถแก้ไขความเชี่ยวชาญได้",
      );
      setSaving(false);
    }
  };

  const handleDeleteSpecialization = async (
    specialization: SpecializationResponse,
  ) => {
    if (specialization.status === "inactive") {
      return;
    }

    const confirmed = window.confirm(
      `ต้องการปิดใช้งานความเชี่ยวชาญ "${specialization.name}" หรือไม่?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      await deleteSpecialization(
        specialization.id,
      );

      await loadData(search, showInactive);
    } catch {
      setError(
        "ไม่สามารถปิดใช้งานความเชี่ยวชาญได้",
      );
    }
  };

  const handleOpenReactivateSpecialization = (
    specialization: SpecializationResponse,
  ) => {
    if (specialization.status !== "inactive") {
      return;
    }

    setSelectedSpecialization(specialization);
    setPassword("");
    setActionError("");

    setModal("reactivate-specialization");
  };

  const handleReactivateSpecialization = async () => {
    if (!selectedSpecialization) {
      return;
    }

    if (!password.trim()) {
      setActionError("กรุณากรอกรหัสผ่าน");
      return;
    }

    try {
      setSaving(true);
      setActionError("");

      await reactivateSpecialization(
        selectedSpecialization.id,
        password,
      );

      await loadData(search, showInactive);

      setSaving(false);
      finishModal();
    } catch {
      setActionError(
        "รหัสผ่านไม่ถูกต้อง หรือไม่สามารถเปิดใช้งานความเชี่ยวชาญได้",
      );
      setSaving(false);
    }
  };

  // =========================================================
  // Logout
  // =========================================================

  const handleOpenLogout = () => {
    setModal("logout");
  };

  const handleCloseLogout = () => {
    if (saving) {
      return;
    }

    setModal(null);
  };

  const handleConfirmLogout = () => {
    logout();
    setModal(null);
    navigate("/login", { replace: true });
  };

  const handleOpenChangePassword = () => {
    setIsChangePasswordOpen(true);
  };

  const handleCloseChangePassword = () => {
    setIsChangePasswordOpen(false);
  };

  return (
    <div className="doctor-page">
      <style>{departmentModalStyle}</style>

      {/* =====================================================
          Sidebar
      ====================================================== */}

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
          <span>ระบบสำหรับ Staff</span>
        </div>

        <nav className="sidebar-nav">
          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() => navigate("/staff")}
          >
            <span className="nav-icon">⌂</span>
            <span>เช็คอินผู้ป่วย</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() =>
              navigate("/staff/doctors")
            }
          >
            <span className="nav-icon">♙</span>
            <span>จัดการแพทย์</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() =>
              navigate("/staff/create")
            }
          >
            <span className="nav-icon">♙</span>
            <span>จัดการเจ้าหน้าที่</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item active"
            onClick={() =>
              navigate("/staff/departments")
            }
          >
            <span className="nav-icon">▦</span>
            <span>จัดการแผนก</span>
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

      {/* =====================================================
          Content
      ====================================================== */}

      <main className="doctor-content">
        <header className="doctor-header">
          <div>
            <span className="page-eyebrow">
              CareFlow Hospital System
            </span>

            <h1>จัดการแผนก</h1>

            <p>
              จัดการแผนกและความเชี่ยวชาญ
            </p>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              flexWrap: "wrap",
            }}
          >
            <button
              type="button"
              className="action-button secondary"
              onClick={
                handleOpenCreateSpecialization
              }
            >
              + เพิ่มความเชี่ยวชาญ
            </button>

            <button
              type="button"
              className="action-button primary"
              onClick={
                handleOpenCreateDepartment
              }
            >
              + เพิ่มแผนก
            </button>
          </div>
        </header>

        {/* ===================================================
            Search
        ==================================================== */}

        <section
          style={{
            marginBottom: 20,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              flexWrap: "wrap",
            }}
          >
            <input
              type="text"
              value={search}
              placeholder="ค้นหาแผนกหรือความเชี่ยวชาญ"
              onChange={(event) => {
                const value =
                  event.target.value;

                setSearch(value);

                void loadData(
                  value,
                  showInactive,
                );
              }}
              style={{
                flex: 1,
                minWidth: 220,
                height: 42,
                boxSizing: "border-box",
                padding: "0 12px",
                border:
                  "1px solid var(--border)",
                borderRadius: 7,
                background:
                  "var(--surface)",
                color: "var(--text)",
                fontFamily: "var(--font)",
                fontSize: 14,
                fontWeight: 400,
                outline: "none",
              }}
            />

            {search && (
              <button
                type="button"
                className="action-button secondary"
                onClick={() => {
                  setSearch("");
                  void loadData(
                    "",
                    showInactive,
                  );
                }}
              >
                ล้าง
              </button>
            )}

            <button
              type="button"
              className="action-button secondary"
              onClick={() => {
                const next =
                  !showInactive;

                setShowInactive(next);
                setSearch("");

                void loadData(
                  "",
                  next,
                );
              }}
            >
              {showInactive
                ? "แสดงรายการที่ใช้งาน"
                : "แสดงรายการที่ปิดใช้งาน"}
            </button>
          </div>
        </section>

        {/* ===================================================
            Loading / Error
        ==================================================== */}

        {loading && (
          <div className="current-patient-card">
            <div
              style={{
                padding: 24,
                color:
                  "var(--text-secondary)",
                fontSize: 14,
                fontWeight: 400,
              }}
            >
              กำลังโหลดข้อมูล...
            </div>
          </div>
        )}

        {!loading && error && (
          <div className="doctor-alert">
            {error}
          </div>
        )}

        {/* ===================================================
            Empty
        ==================================================== */}

        {!loading &&
          !error &&
          filteredDepartments.length ===
            0 && (
            <div className="current-patient-card">
              <div
                style={{
                  padding: 24,
                  color:
                    "var(--text-secondary)",
                  fontSize: 14,
                  fontWeight: 400,
                }}
              >
                {showInactive
                  ? "ไม่พบรายการที่ปิดใช้งาน"
                  : "ไม่พบข้อมูลแผนก"}
              </div>
            </div>
          )}

        {/* ===================================================
            Department Cards
        ==================================================== */}

        {!loading &&
          !error &&
          filteredDepartments.length >
            0 && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 20,
              }}
            >
              {filteredDepartments.map(
                (department) => {
                  const departmentSpecializations =
                    getDepartmentSpecializations(
                      department.id,
                    );

                  const isInactive =
                    department.status ===
                    "inactive";

                  return (
                    <section
                      key={department.id}
                      className="current-patient-card"
                      style={{
                        overflow: "hidden",
                      }}
                    >
                      {/* =============================
                          Department - Top
                      ============================== */}

                      <div
                        style={{
                          display: "flex",
                          alignItems:
                            "flex-start",
                          gap: 20,
                          padding:
                            "22px 24px",
                        }}
                      >
                        {department.image_url ? (
                          <img
                            src={
                              department.image_url
                            }
                            alt={
                              department.name
                            }
                            style={{
                              width: 88,
                              height: 88,
                              flexShrink: 0,
                              objectFit:
                                "cover",
                              borderRadius: 10,
                              border:
                                "1px solid var(--border)",
                            }}
                          />
                        ) : (
                          <div
                            style={{
                              width: 88,
                              height: 88,
                              flexShrink: 0,
                              display: "flex",
                              alignItems:
                                "center",
                              justifyContent:
                                "center",
                              borderRadius: 10,
                              background:
                                "#f1f5f9",
                              color:
                                "var(--text-secondary)",
                              fontSize: 12,
                              fontWeight: 400,
                            }}
                          >
                            ไม่มีรูป
                          </div>
                        )}

                        <div
                          style={{
                            flex: 1,
                            minWidth: 0,
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              alignItems:
                                "flex-start",
                              justifyContent:
                                "space-between",
                              gap: 20,
                            }}
                          >
                            <div>
                              <h2
                                style={{
                                  margin:
                                    "0 0 5px",
                                  color:
                                    "var(--text-h)",
                                  fontSize: 21,
                                  lineHeight:
                                    1.4,
                                  fontWeight: 500,
                                }}
                              >
                                {
                                  department.name
                                }
                              </h2>

                              <p
                                style={{
                                  margin: 0,
                                  color:
                                    "var(--text-secondary)",
                                  fontSize: 14,
                                  lineHeight:
                                    1.6,
                                  fontWeight: 400,
                                }}
                              >
                                {department.description ||
                                  "ไม่มีรายละเอียด"}
                              </p>
                            </div>

                            <span
                              style={{
                                flexShrink: 0,
                                color:
                                  isInactive
                                    ? "var(--danger)"
                                    : "var(--success)",
                                fontSize: 13,
                                lineHeight:
                                  1.4,
                                fontWeight: 400,
                              }}
                            >
                              {isInactive
                                ? "ปิดใช้งาน"
                                : "ใช้งาน"}
                            </span>
                          </div>

                          <p
                            style={{
                              margin:
                                "10px 0 14px",
                              color:
                                "var(--text-secondary)",
                              fontSize: 13,
                              lineHeight:
                                1.5,
                              fontWeight: 400,
                            }}
                          >
                            ระยะเวลานัดหมาย:{" "}
                            {
                              department.slot_duration_minutes
                            }{" "}
                            นาที
                          </p>

                          <div
                            style={{
                              display:
                                "flex",
                              gap: 10,
                              flexWrap:
                                "wrap",
                            }}
                          >
                            {!isInactive && (
                              <>
                                <button
                                  type="button"
                                  className="action-button secondary"
                                  onClick={() =>
                                    handleOpenEditDepartment(
                                      department,
                                    )
                                  }
                                >
                                  แก้ไข
                                </button>

                                <button
                                  type="button"
                                  className="action-button danger"
                                  onClick={() =>
                                    void handleDeleteDepartment(
                                      department,
                                    )
                                  }
                                >
                                  ปิดใช้งาน
                                </button>
                              </>
                            )}

                            {isInactive && (
                              <button
                                type="button"
                                className="action-button primary"
                                onClick={() =>
                                  handleOpenReactivateDepartment(
                                    department,
                                  )
                                }
                              >
                                เปิดใช้งาน
                              </button>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* =============================
                          Specialization - Bottom
                      ============================== */}

                      <div
                        style={{
                          borderTop:
                            "1px solid var(--border)",
                          padding:
                            "20px 24px 22px",
                        }}
                      >
                        <div
                          style={{
                            marginBottom: 14,
                          }}
                        >
                          <span
                            className="section-eyebrow"
                            style={{
                              marginBottom: 4,
                            }}
                          >
                            ความเชี่ยวชาญ
                          </span>

                          <h3
                            style={{
                              margin: 0,
                              color:
                                "var(--text-h)",
                              fontSize: 17,
                              lineHeight:
                                1.4,
                              fontWeight: 500,
                            }}
                          >
                            ความเชี่ยวชาญ
                          </h3>
                        </div>

                        {departmentSpecializations.length ===
                          0 ? (
                          <p
                            style={{
                              margin: 0,
                              color:
                                "var(--text-secondary)",
                              fontSize: 14,
                              lineHeight:
                                1.5,
                              fontWeight: 400,
                            }}
                          >
                            ยังไม่มีความเชี่ยวชาญ
                          </p>
                        ) : (
                          <div
                            style={{
                              display:
                                "flex",
                              flexDirection:
                                "column",
                              gap: 10,
                            }}
                          >
                            {departmentSpecializations.map(
                              (
                                specialization,
                              ) => {
                                const inactive =
                                  specialization.status ===
                                  "inactive";

                                return (
                                  <div
                                    key={
                                      specialization.id
                                    }
                                    style={{
                                      display:
                                        "flex",
                                      alignItems:
                                        "center",
                                      justifyContent:
                                        "space-between",
                                      gap: 20,
                                      padding:
                                        "13px 15px",
                                      border:
                                        "1px solid var(--border)",
                                      borderRadius: 8,
                                      background:
                                        inactive
                                          ? "#fafafa"
                                          : "var(--surface)",
                                    }}
                                  >
                                    <div
                                      style={{
                                        minWidth: 0,
                                      }}
                                    >
                                      <div
                                        style={{
                                          display:
                                            "flex",
                                          alignItems:
                                            "center",
                                          gap: 8,
                                        }}
                                      >
                                        <span
                                          style={{
                                            color:
                                              "var(--text)",
                                            fontSize:
                                              14,
                                            lineHeight:
                                              1.5,
                                            fontWeight:
                                              400,
                                          }}
                                        >
                                          {
                                            specialization.name
                                          }
                                        </span>

                                        <span
                                          style={{
                                            color:
                                              inactive
                                                ? "var(--danger)"
                                                : "var(--success)",
                                            fontSize:
                                              12,
                                            lineHeight:
                                              1.4,
                                            fontWeight:
                                              400,
                                          }}
                                        >
                                          {inactive
                                            ? "ปิดใช้งาน"
                                            : "ใช้งาน"}
                                        </span>
                                      </div>

                                      <p
                                        style={{
                                          margin:
                                            "3px 0 0",
                                          color:
                                            "var(--text-secondary)",
                                          fontSize:
                                            13,
                                          lineHeight:
                                            1.5,
                                          fontWeight:
                                            400,
                                        }}
                                      >
                                        {specialization.description ||
                                          "ไม่มีรายละเอียด"}
                                      </p>
                                    </div>

                                    <div
                                      style={{
                                        display:
                                          "flex",
                                        gap: 10,
                                        flexShrink:
                                          0,
                                      }}
                                    >
                                      {!inactive && (
                                        <>
                                          <button
                                            type="button"
                                            className="action-button secondary"
                                            onClick={() =>
                                              handleOpenEditSpecialization(
                                                specialization,
                                              )
                                            }
                                          >
                                            แก้ไข
                                          </button>

                                          <button
                                            type="button"
                                            className="action-button danger"
                                            onClick={() =>
                                              void handleDeleteSpecialization(
                                                specialization,
                                              )
                                            }
                                          >
                                            ปิดใช้งาน
                                          </button>
                                        </>
                                      )}

                                      {inactive && (
                                        <button
                                          type="button"
                                          className="action-button primary"
                                          onClick={() =>
                                            handleOpenReactivateSpecialization(
                                              specialization,
                                            )
                                          }
                                        >
                                          เปิดใช้งาน
                                        </button>
                                      )}
                                    </div>
                                  </div>
                                );
                              },
                            )}
                          </div>
                        )}
                      </div>
                    </section>
                  );
                },
              )}
            </div>
          )}
      </main>

      {/* =====================================================
          Create / Edit / Reactivate Modal
      ====================================================== */}

      {modal &&
        modal !== "logout" && (
          <div
            className="doctor-modal-overlay"
            role="presentation"
            onClick={(event) => {
              if (
                event.target ===
                  event.currentTarget &&
                !saving
              ) {
                closeModal();
              }
            }}
          >
            <div
              className="doctor-modal"
              role="dialog"
              aria-modal="true"
            >
              {/* Create Department */}

              {modal ===
                "create-department" && (
                <>
                  <div className="doctor-modal-icon">
                    +
                  </div>

                  <h2>
                    เพิ่มแผนก
                  </h2>

                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void handleCreateDepartment();
                    }}
                  >
                    <div>
                      <label htmlFor="department-name">
                        ชื่อแผนก
                      </label>

                      <input
                        id="department-name"
                        value={
                          departmentName
                        }
                        onChange={(event) =>
                          setDepartmentName(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                      />
                    </div>

                    <div>
                      <label htmlFor="department-description">
                        รายละเอียด
                      </label>

                      <textarea
                        id="department-description"
                        value={
                          departmentDescription
                        }
                        onChange={(event) =>
                          setDepartmentDescription(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                        rows={4}
                        style={{
                          width: "100%",
                          padding:
                            "10px 12px",
                          boxSizing:
                            "border-box",
                          border:
                            "1px solid var(--border)",
                          borderRadius: 7,
                          resize: "vertical",
                          fontFamily:
                            "var(--font)",
                          fontSize: 14,
                        }}
                      />
                    </div>

                    <div>
                      <label htmlFor="department-image">
                        รูปภาพ
                      </label>

                      <input
                        id="department-image"
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        onChange={
                          handleDepartmentImageChange
                        }
                        disabled={saving}
                      />

                      {departmentImagePreview && (
                        <div
                          style={{
                            marginTop: 10,
                          }}
                        >
                          <img
                            src={
                              departmentImagePreview
                            }
                            alt="ตัวอย่างรูปภาพแผนก"
                            style={{
                              width: 120,
                              height: 120,
                              objectFit:
                                "cover",
                              borderRadius: 10,
                              border:
                                "1px solid var(--border)",
                            }}
                          />
                        </div>
                      )}
                    </div>

                    <div>
                      <label htmlFor="slot-duration">
                        ระยะเวลานัดหมาย (นาที)
                      </label>

                      <input
                        id="slot-duration"
                        type="number"
                        min="1"
                        value={
                          slotDuration
                        }
                        onChange={(event) =>
                          setSlotDuration(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                      />
                    </div>

                    {actionError && (
                      <p role="alert">
                        {actionError}
                      </p>
                    )}

                    <div className="doctor-modal-actions">
                      <button
                        type="submit"
                        className="action-button primary"
                        disabled={saving}
                      >
                        {saving
                          ? "กำลังบันทึก..."
                          : "ยืนยัน"}
                      </button>

                      <button
                        type="button"
                        className="action-button secondary"
                        onClick={
                          closeModal
                        }
                        disabled={saving}
                      >
                        ยกเลิก
                      </button>
                    </div>
                  </form>
                </>
              )}

              {/* Edit Department */}

              {modal ===
                "edit-department" && (
                <>
                  <div className="doctor-modal-icon">
                    ✎
                  </div>

                  <h2>
                    แก้ไขแผนก
                  </h2>

                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void handleUpdateDepartment();
                    }}
                  >
                    <div>
                      <label htmlFor="edit-department-name">
                        ชื่อแผนก
                      </label>

                      <input
                        id="edit-department-name"
                        value={
                          departmentName
                        }
                        onChange={(event) =>
                          setDepartmentName(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                      />
                    </div>

                    <div>
                      <label htmlFor="edit-department-description">
                        รายละเอียด
                      </label>

                      <textarea
                        id="edit-department-description"
                        value={
                          departmentDescription
                        }
                        onChange={(event) =>
                          setDepartmentDescription(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                        rows={4}
                        style={{
                          width: "100%",
                          padding:
                            "10px 12px",
                          boxSizing:
                            "border-box",
                          border:
                            "1px solid var(--border)",
                          borderRadius: 7,
                          resize: "vertical",
                          fontFamily:
                            "var(--font)",
                          fontSize: 14,
                        }}
                      />
                    </div>

                    <div>
                      <label htmlFor="edit-department-image">
                        รูปภาพ
                      </label>

                      <input
                        id="edit-department-image"
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        onChange={
                          handleDepartmentImageChange
                        }
                        disabled={saving}
                      />

                      {departmentImagePreview ? (
                        <div
                          style={{
                            marginTop: 10,
                          }}
                        >
                          <img
                            src={
                              departmentImagePreview
                            }
                            alt="ตัวอย่างรูปภาพแผนก"
                            style={{
                              width: 120,
                              height: 120,
                              objectFit:
                                "cover",
                              borderRadius: 10,
                              border:
                                "1px solid var(--border)",
                            }}
                          />
                        </div>
                      ) : departmentImageUrl ? (
                        <div
                          style={{
                            marginTop: 10,
                          }}
                        >
                          <img
                            src={
                              departmentImageUrl
                            }
                            alt={
                              departmentName ||
                              "รูปภาพแผนก"
                            }
                            style={{
                              width: 120,
                              height: 120,
                              objectFit:
                                "cover",
                              borderRadius: 10,
                              border:
                                "1px solid var(--border)",
                            }}
                          />
                        </div>
                      ) : null}
                    </div>

                    <div>
                      <label htmlFor="edit-slot-duration">
                        ระยะเวลานัดหมาย (นาที)
                      </label>

                      <input
                        id="edit-slot-duration"
                        type="number"
                        min="1"
                        value={
                          slotDuration
                        }
                        onChange={(event) =>
                          setSlotDuration(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                      />
                    </div>

                    <div>
                      <label htmlFor="add-specialization">
                        เพิ่มความเชี่ยวชาญ
                      </label>

                      <select
                        id="add-specialization"
                        value={specializationToAddId}
                        onChange={(event) =>
                          setSpecializationToAddId(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                        style={{
                          width: "100%",
                          height: 42,
                          padding: "0 12px",
                          boxSizing: "border-box",
                          border: "1px solid var(--border)",
                          borderRadius: 7,
                          background: "var(--surface)",
                          color: "var(--text)",
                          fontFamily: "var(--font)",
                          fontSize: 14,
                          outline: "none",
                        }}
                      >
                        <option value="">
                          เลือกความเชี่ยวชาญ
                        </option>

                        {specializations
                          .filter(
                            (specialization) =>
                              specialization.status ===
                                "active" &&
                              specialization.department_id !==
                                selectedDepartment?.id,
                          )
                          .map((specialization) => (
                            <option
                              key={specialization.id}
                              value={specialization.id}
                            >
                              {specialization.name}
                            </option>
                          ))}
                      </select>
                    </div>

                    {actionError && (
                      <p role="alert">
                        {actionError}
                      </p>
                    )}

                    <div className="doctor-modal-actions">
                      <button
                        type="submit"
                        className="action-button primary"
                        disabled={saving}
                      >
                        {saving
                          ? "กำลังบันทึก..."
                          : "บันทึกการแก้ไข"}
                      </button>

                      <button
                        type="button"
                        className="action-button secondary"
                        onClick={
                          closeModal
                        }
                        disabled={saving}
                      >
                        ยกเลิก
                      </button>
                    </div>
                  </form>
                </>
              )}

              {/* Deactivate Department */}

              {modal ===
                "deactivate-department" && (
                <>
                  <div className="doctor-modal-icon warning">
                    !
                  </div>

                  <h2>
                    ปิดใช้งานแผนก
                  </h2>

                  <p>
                    ต้องการปิดใช้งานแผนก{" "}
                    <strong>
                      {selectedDepartment?.name}
                    </strong>{" "}
                    หรือไม่?
                  </p>

                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void handleDeactivateDepartment();
                    }}
                  >
                    <div>
                      <label htmlFor="deactivate-department-password">
                        ยืนยันรหัสผ่าน Staff
                      </label>

                      <input
                        id="deactivate-department-password"
                        type="password"
                        value={password}
                        placeholder="กรอกรหัสผ่าน"
                        onChange={(event) => {
                          setPassword(event.target.value);
                          setActionError("");
                        }}
                        disabled={saving}
                      />
                    </div>

                    {actionError && (
                      <p role="alert">
                        {actionError}
                      </p>
                    )}

                    <div className="doctor-modal-actions">
                      <button
                        type="submit"
                        className="action-button danger"
                        disabled={saving}
                      >
                        {saving
                          ? "กำลังปิดใช้งาน..."
                          : "ยืนยันปิดใช้งาน"}
                      </button>

                      <button
                        type="button"
                        className="action-button secondary"
                        onClick={closeModal}
                        disabled={saving}
                      >
                        ยกเลิก
                      </button>
                    </div>
                  </form>
                </>
              )}

              {/* Create Specialization */}

              {modal ===
                "create-specialization" && (
                <>
                  <div className="doctor-modal-icon">
                    +
                  </div>

                  <h2>
                    เพิ่มความเชี่ยวชาญ
                  </h2>

                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void handleCreateSpecialization();
                    }}
                  >
                    <div>
                      <label htmlFor="specialization-department">
                        แผนก
                      </label>

                      <select
                        id="specialization-department"
                        value={
                          specializationDepartmentId
                        }
                        onChange={(event) =>
                          setSpecializationDepartmentId(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                        style={{
                          width: "100%",
                          height: 42,
                          padding:
                            "0 12px",
                          border:
                            "1px solid var(--border)",
                          borderRadius: 7,
                          background:
                            "var(--surface)",
                          color:
                            "var(--text)",
                          fontFamily:
                            "var(--font)",
                          fontSize: 14,
                          outline: "none",
                        }}
                      >
                        <option value="">
                          เลือกแผนก
                        </option>

                        {departments
                          .filter(
                            (department) =>
                              department.status ===
                              "active",
                          )
                          .map(
                            (
                              department,
                            ) => (
                              <option
                                key={
                                  department.id
                                }
                                value={
                                  department.id
                                }
                              >
                                {
                                  department.name
                                }
                              </option>
                            ),
                          )}
                      </select>
                    </div>

                    <div>
                      <label htmlFor="specialization-name">
                        ชื่อความเชี่ยวชาญ
                      </label>

                      <input
                        id="specialization-name"
                        value={
                          specializationName
                        }
                        onChange={(event) =>
                          setSpecializationName(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                      />
                    </div>

                    <div>
                      <label htmlFor="specialization-description">
                        รายละเอียด
                      </label>

                      <textarea
                        id="specialization-description"
                        value={
                          specializationDescription
                        }
                        onChange={(event) =>
                          setSpecializationDescription(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                        rows={4}
                        style={{
                          width: "100%",
                          padding:
                            "10px 12px",
                          boxSizing:
                            "border-box",
                          border:
                            "1px solid var(--border)",
                          borderRadius: 7,
                          resize: "vertical",
                          fontFamily:
                            "var(--font)",
                          fontSize: 14,
                        }}
                      />
                    </div>

                    {actionError && (
                      <p role="alert">
                        {actionError}
                      </p>
                    )}

                    <div className="doctor-modal-actions">
                      <button
                        type="submit"
                        className="action-button primary"
                        disabled={saving}
                      >
                        {saving
                          ? "กำลังบันทึก..."
                          : "ยืนยัน"}
                      </button>

                      <button
                        type="button"
                        className="action-button secondary"
                        onClick={
                          closeModal
                        }
                        disabled={saving}
                      >
                        ยกเลิก
                      </button>
                    </div>
                  </form>
                </>
              )}

              {/* Edit Specialization */}

              {modal ===
                "edit-specialization" && (
                <>
                  <div className="doctor-modal-icon">
                    ✎
                  </div>

                  <h2>
                    แก้ไขความเชี่ยวชาญ
                  </h2>

                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void handleUpdateSpecialization();
                    }}
                  >
                    <div>
                      <label htmlFor="edit-specialization-department">
                        แผนก
                      </label>

                      <select
                        id="edit-specialization-department"
                        value={
                          specializationDepartmentId
                        }
                        onChange={(event) =>
                          setSpecializationDepartmentId(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                        style={{
                          width: "100%",
                          height: 42,
                          padding:
                            "0 12px",
                          border:
                            "1px solid var(--border)",
                          borderRadius: 7,
                          background:
                            "var(--surface)",
                          color:
                            "var(--text)",
                          fontFamily:
                            "var(--font)",
                          fontSize: 14,
                          outline: "none",
                        }}
                      >
                        <option value="">
                          เลือกแผนก
                        </option>

                        {departments
                          .filter(
                            (department) =>
                              department.status ===
                              "active",
                          )
                          .map(
                            (
                              department,
                            ) => (
                              <option
                                key={
                                  department.id
                                }
                                value={
                                  department.id
                                }
                              >
                                {
                                  department.name
                                }
                              </option>
                            ),
                          )}
                      </select>
                    </div>

                    <div>
                      <label htmlFor="edit-specialization-name">
                        ชื่อความเชี่ยวชาญ
                      </label>

                      <input
                        id="edit-specialization-name"
                        value={
                          specializationName
                        }
                        onChange={(event) =>
                          setSpecializationName(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                      />
                    </div>

                    <div>
                      <label htmlFor="edit-specialization-description">
                        รายละเอียด
                      </label>

                      <textarea
                        id="edit-specialization-description"
                        value={
                          specializationDescription
                        }
                        onChange={(event) =>
                          setSpecializationDescription(
                            event.target.value,
                          )
                        }
                        disabled={saving}
                        rows={4}
                        style={{
                          width: "100%",
                          padding:
                            "10px 12px",
                          boxSizing:
                            "border-box",
                          border:
                            "1px solid var(--border)",
                          borderRadius: 7,
                          resize: "vertical",
                          fontFamily:
                            "var(--font)",
                          fontSize:14,
                        }}
                      />
                    </div>

                    {actionError && (
                      <p role="alert">
                        {actionError}
                      </p>
                    )}

                    <div className="doctor-modal-actions">
                      <button
                        type="submit"
                        className="action-button primary"
                        disabled={saving}
                      >
                        {saving
                          ? "กำลังบันทึก..."
                          : "บันทึกการแก้ไข"}
                      </button>

                      <button
                        type="button"
                        className="action-button secondary"
                        onClick={
                          closeModal
                        }
                        disabled={saving}
                      >
                        ยกเลิก
                      </button>
                    </div>
                  </form>
                </>
              )}

              {/* Reactivate Department */}

              {modal ===
                "reactivate-department" && (
                <>
                  <div className="doctor-modal-icon">
                    !
                  </div>

                  <h2>
                    เปิดใช้งานแผนก
                  </h2>

                  <p>
                    ต้องการเปิดใช้งานแผนก{" "}
                    <strong>
                      {
                        selectedDepartment?.name
                      }
                    </strong>{" "}
                    หรือไม่?
                  </p>

                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void handleReactivateDepartment();
                    }}
                  >
                    <div>
                      <label htmlFor="reactivate-department-password">
                        ยืนยันรหัสผ่าน Staff
                      </label>

                      <input
                        id="reactivate-department-password"
                        type="password"
                        value={
                          password
                        }
                        placeholder="กรอกรหัสผ่าน"
                        onChange={(event) => {
                          setPassword(
                            event.target.value,
                          );
                          setActionError("");
                        }}
                        disabled={saving}
                      />
                    </div>

                    {actionError && (
                      <p role="alert">
                        {actionError}
                      </p>
                    )}

                    <div className="doctor-modal-actions">
                      <button
                        type="submit"
                        className="action-button primary"
                        disabled={saving}
                      >
                        {saving
                          ? "กำลังเปิดใช้งาน..."
                          : "ยืนยันการเปิดใช้งาน"}
                      </button>

                      <button
                        type="button"
                        className="action-button secondary"
                        onClick={
                          closeModal
                        }
                        disabled={saving}
                      >
                        ยกเลิก
                      </button>
                    </div>
                  </form>
                </>
              )}

              {/* Reactivate Specialization */}

              {modal ===
                "reactivate-specialization" && (
                <>
                  <div className="doctor-modal-icon">
                    !
                  </div>

                  <h2>
                    เปิดใช้งานความเชี่ยวชาญ
                  </h2>

                  <p>
                    ต้องการเปิดใช้งานความเชี่ยวชาญ{" "}
                    <strong>
                      {
                        selectedSpecialization?.name
                      }
                    </strong>{" "}
                    หรือไม่?
                  </p>

                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void handleReactivateSpecialization();
                    }}
                  >
                    <div>
                      <label htmlFor="reactivate-specialization-password">
                        ยืนยันรหัสผ่าน Staff
                      </label>

                      <input
                        id="reactivate-specialization-password"
                        type="password"
                        value={
                          password
                        }
                        placeholder="กรอกรหัสผ่าน"
                        onChange={(event) => {
                          setPassword(
                            event.target.value,
                          );
                          setActionError("");
                        }}
                        disabled={saving}
                      />
                    </div>

                    {actionError && (
                      <p role="alert">
                        {actionError}
                      </p>
                    )}

                    <div className="doctor-modal-actions">
                      <button
                        type="submit"
                        className="action-button primary"
                        disabled={saving}
                      >
                        {saving
                          ? "กำลังเปิดใช้งาน..."
                          : "ยืนยันการเปิดใช้งาน"}
                      </button>

                      <button
                        type="button"
                        className="action-button secondary"
                        onClick={
                          closeModal
                        }
                        disabled={saving}
                      >
                        ยกเลิก
                      </button>
                    </div>
                  </form>
                </>
              )}
            </div>
          </div>
        )}

      {/* =====================================================
          Logout Modal
      ====================================================== */}

      {modal === "logout" && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={(event) => {
            if (
              event.target ===
              event.currentTarget
            ) {
              handleCloseLogout();
            }
          }}
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
          >
            <div className="doctor-modal-icon warning">
              !
            </div>

            <h2>ออกจากระบบ</h2>

            <p>
              คุณต้องการออกจากระบบหรือไม่?
            </p>

            <div className="doctor-modal-actions">
              <button
                type="button"
                className="action-button danger"
                onClick={handleConfirmLogout}
              >
                ออกจากระบบ
              </button>

              <button
                type="button"
                className="action-button secondary"
                onClick={handleCloseLogout}
              >
                ยกเลิก
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================
          Change Password
      ====================================================== */}

      <ChangePasswordModal
        isOpen={isChangePasswordOpen}
        onClose={handleCloseChangePassword}
      />
    </div>
  );
};

export default DepartmentManagementPage;